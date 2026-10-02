"""Separate AI-reference exploratory evaluation; never a human accuracy result.

The original primary evaluator and student-review finalizer remain unchanged.
Run with ``python -m rolelens.exploratory --help``. No API is called by default.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import date, datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time
import uuid

from project_core.evidence import canonical_json, verify_lock
from project_core.metrics import latency_summary
from .pipeline import analyze
from .provider import DEFAULT_MODEL
from .taxonomy import BY_ID

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data" / "primary_cases_v2.jsonl"
LOCK = ROOT / "data" / "primary_cases_v2_lock.json"
PROTOCOL = ROOT / "data" / "primary_protocol_v2.json"
REFERENCE_KIND = "ai_generated_exploratory"
LIMITATION = (
    "Agreement against Codex AI-generated reference labels, not human accuracy or "
    "correctness. No student review is asserted. Shared model assumptions may inflate "
    "agreement; literal quote validation does not establish semantic support."
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _atomic_write(path: Path, content: bytes) -> None:
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def _exclusive_run(directory: Path):
    """OS lock releases on process exit; concurrent runs cannot double-spend."""
    with (directory / ".run.lock").open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError("Another exploratory run is using this output directory") from exc
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RuntimeError("Another exploratory run is using this output directory") from exc
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _reject_human_markers(value) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"reviewer", "review_date", "student_reviewed", "student_reviewer"}:
                raise ValueError("AI references must not contain student or human review fields")
            if key == "human_reviewed" and child is not False:
                raise ValueError("AI references must declare human_reviewed=false")
            if key == "reference_status" and child != REFERENCE_KIND:
                raise ValueError("Mislabeled reference_status in exploratory reference")
            _reject_human_markers(child)
    elif isinstance(value, list):
        for child in value:
            _reject_human_markers(child)


def _valid_gaps(value) -> bool:
    return (
        isinstance(value, list) and len(value) == 3
        and all(isinstance(item, str) and item in BY_ID for item in value)
        and len(set(value)) == 3
    )


def _input_paths(cases_path: Path | None, lock_path: Path | None,
                 protocol_path: Path | None) -> tuple[Path, Path, Path, bool]:
    supplied = (cases_path is not None, lock_path is not None, protocol_path is not None)
    if any(supplied) and not all(supplied):
        raise ValueError("Custom inputs require --cases, --case-lock and --protocol together")
    return (cases_path or CASES, lock_path or LOCK, protocol_path or PROTOCOL, all(supplied))


def load_references(path: Path, *, cases_path: Path | None = None,
                    lock_path: Path | None = None,
                    protocol_path: Path | None = None) -> tuple[list[dict], dict, bytes]:
    """Verify one frozen phase; AI references remain a separate artifact.

    Omitting all three custom paths retains the original ten-case input gate.
    An expansion must supply its own input lock and pre-prediction protocol.
    """
    source, lock, protocol_file, custom = _input_paths(cases_path, lock_path, protocol_path)
    cases = verify_lock(source, lock)
    protocol = json.loads(protocol_file.read_text(encoding="utf-8"))
    count = len(cases)
    if [row["id"] for row in cases] != protocol["case_ids"]:
        raise ValueError("Frozen input IDs or ordering differ from the protocol")
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", row["id"]) for row in cases):
        raise ValueError("Case IDs must be safe, nonempty filenames")
    if custom:
        if (type(protocol.get("case_count")) is not int or protocol["case_count"] != count
                or not isinstance(protocol.get("phase_id"), str) or not protocol["phase_id"].strip()
                or protocol.get("predictions_run_at_freeze") is not False
                or protocol.get("input_reference_status") != "INPUT_ONLY_FROZEN"):
            raise ValueError("Custom protocol needs the case count, phase ID and explicit input-only pre-prediction freeze")
        if protocol.get("input_file_sha256") != _sha(source.read_bytes()):
            raise ValueError("Custom protocol does not match the frozen input file hash")
        if protocol.get("input_case_lock_sha256") != _sha(lock.read_bytes()):
            raise ValueError("Custom protocol does not match the frozen input lock hash")
        expected_status = "INPUT_ONLY_FROZEN"
    else:
        if count != 10:
            raise ValueError("Default evaluation requires the original ten frozen v2 inputs")
        expected_status = "PENDING_STUDENT_REVIEW"
    if any(row.get("reference_status") != expected_status or "reference_gaps" in row for row in cases):
        raise ValueError("Source inputs must retain their frozen input-only reference state")
    if any(not isinstance(row.get(field), str) or not row[field].strip()
           for row in cases for field in ("jd", "profile", "profile_id", "bucket")):
        raise ValueError("Each case needs a nonempty JD, profile, profile ID and PM bucket")
    if len({row["profile_id"] for row in cases}) != count:
        raise ValueError("A profile must not be reused within a phase")
    if any(row["bucket"] not in {"AI_PM", "COMMERCIAL_PM"} for row in cases):
        raise ValueError("Only AI_PM and COMMERCIAL_PM target-role buckets are supported")
    if protocol["taxonomy_sha256_at_freeze"] != _sha((ROOT / "rolelens" / "taxonomy.py").read_bytes()):
        raise ValueError("Taxonomy differs from the original frozen input protocol")
    raw = path.read_bytes()
    reference = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(reference, dict):
        raise ValueError("AI reference artifact must be a JSON object")
    _reject_human_markers(reference)
    if (reference.get("reference_kind") != REFERENCE_KIND
            or reference.get("human_reviewed") is not False
            or reference.get("producer") != "Codex AI"):
        raise ValueError("Require explicit ai_generated_exploratory / human_reviewed=false / Codex AI provenance")
    try:
        generated_on = date.fromisoformat(reference["generated_date"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("AI references need an explicit YYYY-MM-DD generated_date") from exc
    if generated_on < date.fromisoformat(protocol["freeze_date"]):
        raise ValueError("AI references cannot predate the frozen inputs")
    if reference.get("input_file_sha256") != _sha(source.read_bytes()):
        raise ValueError("AI references do not match the frozen source file hash")
    rows = reference.get("cases")
    if not isinstance(rows, list) or len(rows) != count or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"AI references must contain {count} case objects")
    ids = [row.get("case_id") for row in rows]
    if any(not isinstance(case_id, str) for case_id in ids) or len(set(ids)) != count or set(ids) != {row["id"] for row in cases}:
        raise ValueError("AI reference IDs must match this frozen phase exactly")
    for row in rows:
        if not _valid_gaps(row.get("gap_ids")):
            raise ValueError(f"{row['case_id']}: require three distinct valid AI-reference gap IDs")
    return cases, reference, raw


def _prediction(result: dict, mode: str) -> tuple[list[str] | None, list[str]]:
    if mode == "baseline":
        baseline = result.get("baseline", {})
        gaps = baseline.get("top_gaps")
        accepted = not baseline.get("abstained", True) and _valid_gaps(gaps)
        reasons = [baseline.get("abstain_reason") or "BASELINE_NO_VALID_THREE_GAPS"]
    else:
        gaps = [item.get("capability_id") for item in result.get("analysis", {}).get("top_gaps", [])]
        accepted = result.get("status") == "ok" and _valid_gaps(gaps)
        reasons = result.get("reason_codes") or ["AI_NO_VALID_THREE_GAPS"]
    return (gaps, []) if accepted else (None, reasons)


def agreement_metrics(references: list[list[str]], predictions: list[list[str] | None]) -> dict:
    """All-case denominator includes every abstention as zero overlap."""
    if not references or len(references) != len(predictions):
        raise ValueError("Need aligned nonempty references and predictions")
    if any(not _valid_gaps(row) for row in references) or any(row is not None and not _valid_gaps(row) for row in predictions):
        raise ValueError("Reference and accepted prediction sets need three valid IDs")
    overlaps = [len(set(ref) & set(pred)) if pred is not None else 0 for ref, pred in zip(references, predictions)]
    total = len(references)
    accepted = sum(pred is not None for pred in predictions)
    passed = sum(value >= 2 for value in overlaps)
    return {
        "case_count": total,
        "accepted_count": accepted,
        "abstention_count": total - accepted,
        "coverage": accepted / total,
        "mean_overlap_all_cases_abstain_zero": sum(overlaps) / total,
        "mean_overlap_fraction_all_cases_abstain_zero": sum(overlaps) / (3 * total),
        "case_pass_at_least_two_of_three_count": passed,
        "case_pass_at_least_two_of_three_all_cases": passed / total,
        "accepted_only_mean_overlap": sum(overlaps) / accepted if accepted else None,
        "accepted_only_pass_at_least_two_of_three": passed / accepted if accepted else None,
        "metric_interpretation": "AI-reference agreement only; not human accuracy",
    }


def _number(value) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value >= 0


def summarize(records: list[dict], reference: dict, mode: str, manifest: dict) -> dict:
    by_id = {row["case_id"]: row["gap_ids"] for row in reference["cases"]}
    refs = [by_id[row["case_id"]] for row in records]
    baseline = [_prediction(row["result"], "baseline") for row in records]
    requested = [_prediction(row["result"], mode) for row in records]
    model_runs = [row["result"].get("model_run", {}) for row in records]
    costs = [run["billed_cost_usd"] for run in model_runs if _number(run.get("billed_cost_usd"))]
    estimates = [run["estimated_cost_usd"] for run in model_runs if _number(run.get("estimated_cost_usd"))]
    reasons = Counter(reason for _, codes in requested for reason in codes)
    return {
        "evaluation_type": "ai_reference_exploratory_" + mode,
        "reference_kind": REFERENCE_KIND,
        "human_reviewed": False,
        "limitation": LIMITATION,
        "manifest_sha256": _sha(canonical_json(manifest).encode("utf-8")),
        "input_file_sha256": manifest["identity"]["input_file_sha256"],
        "reference_file_sha256": manifest["identity"]["reference_file_sha256"],
        "baseline_ai_reference_agreement": agreement_metrics(refs, [row[0] for row in baseline]),
        "requested_mode_ai_reference_agreement": agreement_metrics(refs, [row[0] for row in requested]),
        "abstention_reason_counts": dict(reasons),
        "baseline_abstention_reason_counts": dict(Counter(reason for _, codes in baseline for reason in codes)),
        "latency_including_abstentions": latency_summary([row["elapsed_ms"] for row in records]),
        "total_response_reported_cost_usd": round(sum(costs), 8) if costs else None,
        "response_reported_cost_case_count": len(costs),
        "response_reported_cost_missing_case_count": len(records) - len(costs) if mode == "ai" else 0,
        "total_estimated_cost_usd": round(sum(estimates), 8) if estimates else None,
        "cost_note": "Includes response-reported charges for invalid and abstained responses; missing costs are unknown, not zero. These are not provider invoices.",
        "external_model_requested": mode == "ai",
        "raw_inputs_exported": False,
        "case_results": [{
            "case_id": row["case_id"],
            "accepted": prediction is not None,
            "prediction_gap_ids": prediction,
            "reference_gap_ids": by_id[row["case_id"]],
            "overlap": len(set(prediction) & set(by_id[row["case_id"]])) if prediction is not None else 0,
            "reason_codes": codes,
            "latency_ms": row["elapsed_ms"],
            "response_reported_cost_usd": row["result"].get("model_run", {}).get("billed_cost_usd"),
        } for row, (prediction, codes) in zip(records, requested)],
    }


def evaluate(reference_path: Path, out_dir: Path, *, mode: str = "baseline",
             knowledge: Path = ROOT / "data" / "knowledge_notes.jsonl",
             allow_external_processing: bool = False, model: str = DEFAULT_MODEL,
             cases_path: Path | None = None, lock_path: Path | None = None,
             protocol_path: Path | None = None) -> dict:
    if mode not in {"baseline", "ai"}:
        raise ValueError("mode must be baseline or ai")
    if mode == "ai" and not allow_external_processing:
        raise ValueError("AI exploratory evaluation requires --allow-external-processing")
    source, lock, protocol_file, custom = _input_paths(cases_path, lock_path, protocol_path)
    cases, reference, reference_bytes = load_references(
        reference_path, cases_path=cases_path, lock_path=lock_path, protocol_path=protocol_path)
    identity = {
        "schema_version": 1,
        "reference_kind": REFERENCE_KIND,
        "human_reviewed": False,
        "input_file_sha256": _sha(source.read_bytes()),
        "input_lock_sha256": _sha(lock.read_bytes()),
        "protocol_sha256": _sha(protocol_file.read_bytes()),
        "reference_file_sha256": _sha(reference_bytes),
        "knowledge_sha256": _sha(knowledge.read_bytes()),
        "mode": mode,
        "model": model if mode == "ai" else None,
        "external_processing_authorized": allow_external_processing if mode == "ai" else False,
        "source_code_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha(path.read_bytes())
            for folder in ("rolelens", "project_core") for path in sorted((ROOT / folder).glob("*.py"))
        },
    }
    if custom:
        protocol = json.loads(protocol_file.read_text(encoding="utf-8"))
        identity.update({"phase_id": protocol["phase_id"], "case_count": len(cases)})
    out_dir.mkdir(parents=True, exist_ok=True)
    with _exclusive_run(out_dir):
        manifest_path = out_dir / "manifest.json"
        snapshot_path = out_dir / "reference_snapshot.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("identity") != identity or not snapshot_path.exists() or snapshot_path.read_bytes() != reference_bytes:
                raise ValueError("Run inputs, labels or code changed; use a new exploratory output directory")
        else:
            if any(path.name != "reference_snapshot.json" for path in out_dir.glob("*.json")):
                raise ValueError("Per-case outputs exist without a manifest; refusing to adopt them")
            if snapshot_path.exists() and snapshot_path.read_bytes() != reference_bytes:
                raise ValueError("Existing frozen reference snapshot differs")
            _atomic_write(snapshot_path, reference_bytes)
            manifest = {"identity": identity, "labels_frozen_before_predictions": True,
                        "freeze_recorded_at_utc": datetime.now(timezone.utc).isoformat(), "limitation": LIMITATION}
            _atomic_write(manifest_path, _json_bytes(manifest))
        run_hash = _sha(canonical_json(manifest).encode("utf-8"))
        records = []
        for case in cases:
            case_id = case["id"]
            result_path = out_dir / f"{case_id}.json"
            pending_path = out_dir / f"{case_id}.pending.json"
            if result_path.exists():
                record = json.loads(result_path.read_text(encoding="utf-8"))
                if record.get("manifest_sha256") != run_hash or record.get("case_id") != case_id:
                    raise ValueError(f"{case_id}: saved result belongs to a different run")
                if record.get("payload_sha256") != _sha(canonical_json({key: value for key, value in record.items() if key != "payload_sha256"}).encode("utf-8")):
                    raise ValueError(f"{case_id}: saved result hash mismatch")
                pending_path.unlink(missing_ok=True)
            else:
                if pending_path.exists():
                    raise RuntimeError(f"{case_id}: prior request outcome is unknown. Preserve the pending file and investigate; automatic retry could duplicate charges.")
                _atomic_write(pending_path, _json_bytes({"case_id": case_id, "manifest_sha256": run_hash,
                              "started_at_utc": datetime.now(timezone.utc).isoformat(), "mode": mode}))
                started = time.perf_counter()
                result = analyze(case["jd"], case["profile"], knowledge, mode=mode,
                                 allow_external_processing=allow_external_processing, model=model)
                record = {"case_id": case_id, "manifest_sha256": run_hash,
                          "reference_kind": REFERENCE_KIND, "human_reviewed": False,
                          "elapsed_ms": round((time.perf_counter() - started) * 1000, 2), "result": result}
                record["payload_sha256"] = _sha(canonical_json(record).encode("utf-8"))
                _atomic_write(result_path, _json_bytes(record))
                pending_path.unlink(missing_ok=True)
            records.append(record)
            _atomic_write(out_dir / "progress.json", _json_bytes({"completed_count": len(records),
                          "case_count": len(cases), "manifest_sha256": run_hash, "reference_kind": REFERENCE_KIND,
                          "human_reviewed": False, "complete": len(records) == len(cases)}))
        summary = summarize(records, reference, mode, manifest)
        _atomic_write(out_dir / "summary.json", _json_bytes(summary))
        return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-reference agreement only; does not finalize or bypass the human-reviewed primary evaluation")
    parser.add_argument("--references", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["baseline", "ai"], default="baseline")
    parser.add_argument("--knowledge", type=Path, default=ROOT / "data" / "knowledge_notes.jsonl")
    parser.add_argument("--allow-external-processing", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--cases", type=Path, help="Custom frozen JSONL; requires --case-lock and --protocol")
    parser.add_argument("--case-lock", type=Path)
    parser.add_argument("--protocol", type=Path)
    args = parser.parse_args()
    summary = evaluate(args.references, args.out_dir, mode=args.mode, knowledge=args.knowledge,
                       allow_external_processing=args.allow_external_processing, model=args.model,
                       cases_path=args.cases, lock_path=args.case_lock, protocol_path=args.protocol)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
