"""RoleLens CLI. It never writes a pasted profile to disk."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from project_core.evidence import verify_lock
from project_core.metrics import gap_agreement_at_k, latency_summary

from .pipeline import analyze
from .taxonomy import BY_ID

REVIEWED_DATASET_NAME = "RoleLens v2 ten student-reviewed fictional PM references"
REVIEWED_PROVENANCE = "Student-entered blind review; see private dated decisions CSV"
REVIEW_ROW_PROVENANCE = "Student-entered independent three-ID review of full fictional JD and CV pair"


def _read_text(path: Path) -> str:
    if path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader  # optional only for local PDF extraction

        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    raise ValueError("Input must be a local .txt, .md or text-layer .pdf; image files need local OCR first")


def _private_cv(args: argparse.Namespace) -> None:
    if args.mode != "baseline":
        raise ValueError("--private-cv only permits local baseline mode")
    profile = _read_text(args.private_cv)
    jd = _read_text(args.jd)
    result = analyze(jd, profile, args.knowledge, mode="baseline")
    # Minimal aggregate output: no profile text, quotes, or per-capability data.
    baseline = result.get("baseline", {})
    print(json.dumps({
        "evaluation_type": "private_cv_local_sanity",
        "status": result["status"],
        "reason_codes": result["reason_codes"],
        "capability_count": len(baseline.get("capabilities", [])),
        "returned_three_gaps": len(baseline.get("top_gaps", [])) == 3,
        "external_model_called": False,
        "profile_saved": False,
    }, indent=2))


def _require_review_structure(cases: list[dict], lock_path: Path) -> None:
    """Check finalizer fields; metadata cannot prove who actually reviewed a case."""
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("dataset_name") != REVIEWED_DATASET_NAME or lock.get("provenance") != REVIEWED_PROVENANCE:
        raise ValueError("Evaluation requires the v2 student-review finalizer lock")
    for case in cases:
        selected = case.get("reference_gaps")
        if not isinstance(selected, list) or len(selected) != 3 or any(not isinstance(item, str) or item not in BY_ID for item in selected) or len(set(selected)) != 3:
            raise ValueError(f"{case['id']}: need three unique valid reviewed gap IDs")
        if case.get("reference_provenance") != REVIEW_ROW_PROVENANCE:
            raise ValueError(f"{case['id']}: missing independent-review provenance")
        if not isinstance(case.get("review_reason"), str) or len(case["review_reason"].strip()) < 12:
            raise ValueError(f"{case['id']}: missing student review reason")
        if not isinstance(case.get("reviewer"), str) or not case["reviewer"].strip():
            raise ValueError(f"{case['id']}: missing reviewer")
        try:
            reviewed_on = date.fromisoformat(case["review_date"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{case['id']}: invalid student review date") from exc
        if reviewed_on < date(2026, 9, 26) or reviewed_on > date.today():
            raise ValueError(f"{case['id']}: review date outside protocol window")


def _evaluate(args: argparse.Namespace) -> None:
    cases = verify_lock(args.cases, args.lock)
    human_reviewed = all(case.get("reference_status") == "human_reviewed" for case in cases)
    if not human_reviewed:
        raise ValueError("Primary evaluation is locked until the student independently reviews all ten cases")
    _require_review_structure(cases, args.lock)
    original = {row["id"]: row for row in verify_lock(
        Path(__file__).resolve().parents[1] / "data" / "primary_cases_v2.jsonl",
        Path(__file__).resolve().parents[1] / "data" / "primary_cases_v2_lock.json",
    )}
    if len(cases) != 10 or {case["id"] for case in cases} != set(original):
        raise ValueError("Evaluation only accepts the ten frozen v2 synthetic cases")
    if any(case["jd"] != original[case["id"]]["jd"] or case["profile"] != original[case["id"]]["profile"] for case in cases):
        raise ValueError("Evaluation inputs differ from frozen v2 synthetic cases")
    if args.mode == "ai" and not args.allow_external_processing:
        raise ValueError("AI evaluation requires --allow-external-processing")
    references: list[list[str]] = []
    baseline_predictions: list[list[str] | None] = []
    ai_predictions: list[list[str] | None] = []
    latencies = []
    baseline_case_status = []
    per_case = []
    estimated_costs = []
    response_costs = []
    import time

    for case in cases:
        started = time.perf_counter()
        result = analyze(
            case["jd"], case["profile"], args.knowledge,
            mode=args.mode, allow_external_processing=args.allow_external_processing,
        )
        latencies.append((time.perf_counter() - started) * 1000)
        baseline = result.get("baseline", {})
        baseline_predictions.append(baseline.get("top_gaps") if len(baseline.get("top_gaps", [])) == 3 else None)
        baseline_case_status.append({"id": case["id"], "returned_gap_count": len(baseline.get("top_gaps", [])), "abstained": len(baseline.get("top_gaps", [])) != 3})
        if args.mode == "ai":
            analysis = result.get("analysis", {})
            ai_predictions.append([item["capability_id"] for item in analysis["top_gaps"]] if result["status"] == "ok" else None)
            model_run = result.get("model_run", {})
            if isinstance(model_run.get("estimated_cost_usd"), (int, float)):
                estimated_costs.append(model_run["estimated_cost_usd"])
            if isinstance(model_run.get("billed_cost_usd"), (int, float)):
                response_costs.append(model_run["billed_cost_usd"])
            per_case.append({
                "id": case["id"],
                "status": result["status"],
                "reason_codes": result["reason_codes"],
                "latency_ms": round(latencies[-1], 2),
                "usage": model_run.get("usage"),
                "estimated_cost_usd": model_run.get("estimated_cost_usd"),
                "response_reported_billed_cost_usd": model_run.get("billed_cost_usd"),
                "provider_error": model_run.get("provider_error"),
            })
        references.append(case["reference_gaps"])
    output = {
        "evaluation_type": "locked_case_set_" + args.mode,
        "case_count": len(cases),
        "reference_status": "student_entered_human_reviewed_synthetic_reference",
        "review_structure_verified": True,
        "review_authenticity_limitation": "Field and hash checks do not independently prove who made the human judgments.",
        "latency": latency_summary(latencies),
        "baseline_coverage": sum(value is not None for value in baseline_predictions) / len(cases),
        "baseline_cases": baseline_case_status,
        "baseline_top3_gap_agreement": gap_agreement_at_k(references, baseline_predictions),
        "ai_top3_gap_agreement": gap_agreement_at_k(references, ai_predictions) if args.mode == "ai" else "NOT_RUN",
        "ai_coverage": sum(value is not None for value in ai_predictions) / len(cases) if args.mode == "ai" else "NOT_RUN",
        "model_cases": per_case if args.mode == "ai" else "NOT_RUN",
        "total_estimated_cost_usd_with_usage": round(sum(estimated_costs), 8) if estimated_costs else None,
        "total_response_reported_billed_cost_usd": round(sum(response_costs), 8) if response_costs else None,
        "cost_note": "Response-reported cost, if present, is preferred over listed-rate estimates; neither substitutes for a provider invoice.",
        "external_model_requested": args.mode == "ai",
        "raw_inputs_exported": False,
    }
    print(json.dumps(output, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence-linked AI and commercial product manager preparation")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze_cmd = sub.add_parser("analyze")
    analyze_cmd.add_argument("--jd", required=True, type=Path)
    analyze_cmd.add_argument("--profile", type=Path)
    analyze_cmd.add_argument("--private-cv", type=Path, help="Local only; never sends text to an API")
    analyze_cmd.add_argument("--knowledge", required=True, type=Path)
    analyze_cmd.add_argument("--mode", choices=["baseline", "ai"], default="baseline")
    analyze_cmd.add_argument("--allow-external-processing", action="store_true")
    eval_cmd = sub.add_parser("evaluate")
    eval_cmd.add_argument("--cases", required=True, type=Path)
    eval_cmd.add_argument("--lock", required=True, type=Path)
    eval_cmd.add_argument("--knowledge", required=True, type=Path)
    eval_cmd.add_argument("--mode", choices=["baseline", "ai"], default="baseline")
    eval_cmd.add_argument("--allow-external-processing", action="store_true")
    args = parser.parse_args()
    if args.command == "analyze":
        if args.private_cv:
            _private_cv(args)
            return
        if not args.profile:
            parser.error("analyze needs --profile or --private-cv")
        result = analyze(
            _read_text(args.jd),
            _read_text(args.profile),
            args.knowledge,
            mode=args.mode,
            allow_external_processing=args.allow_external_processing,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _evaluate(args)


if __name__ == "__main__":
    main()
