"""Read-only pooling of separately frozen exploratory phases; never calls an API.

Each --phase takes a saved run directory, its frozen JSONL inputs and its lock.
Historical source hashes are retained rather than compared to today's code.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from project_core.evidence import canonical_json, verify_lock
from .exploratory import (
    REFERENCE_KIND, _json_bytes, _reject_human_markers, _sha, _valid_gaps,
    summarize,
)


def pool_runs(phases: list[tuple[Path, Path, Path]], *,
              expected_case_count: int | None = None) -> dict:
    """Pool all cases with abstentions included, preserving each phase's results.

    The tuple is (saved run directory, frozen case file, frozen case lock).
    Different implementation hashes are disclosed, never silently homogenized.
    """
    if len(phases) < 2:
        raise ValueError("Pooling requires at least two independently saved phases")
    all_records, all_references, phase_results = [], [], []
    seen_cases, seen_profiles = set(), set()
    modes, models, knowledge_hashes, taxonomy_hashes = set(), set(), set(), set()
    phase_hashes, source_hashes, bucket_counts = [], [], Counter()
    for index, (directory, source, lock) in enumerate(phases, 1):
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        identity = manifest["identity"]
        if (manifest.get("labels_frozen_before_predictions") is not True
                or identity.get("reference_kind") != REFERENCE_KIND
                or identity.get("human_reviewed") is not False):
            raise ValueError("Each phase must preserve its frozen AI-reference provenance")
        cases = verify_lock(source, lock)
        if (_sha(source.read_bytes()) != identity.get("input_file_sha256")
                or _sha(lock.read_bytes()) != identity.get("input_lock_sha256")):
            raise ValueError("A phase does not match its saved input hashes")
        case_ids = {row["id"] for row in cases}
        profile_ids = {row["profile_id"] for row in cases}
        if len(profile_ids) != len(cases) or seen_cases & case_ids or seen_profiles & profile_ids:
            raise ValueError("Pooled phases must not repeat a case or a profile")
        seen_cases.update(case_ids)
        seen_profiles.update(profile_ids)
        expected_files = {f"{case_id}.json" for case_id in case_ids}
        metadata_files = {"manifest.json", "reference_snapshot.json", "summary.json", "progress.json"}
        if any(path.name not in expected_files | metadata_files for path in directory.glob("*.json")):
            raise ValueError("Unexpected or pending record in phase directory")
        reference_bytes = (directory / "reference_snapshot.json").read_bytes()
        if _sha(reference_bytes) != identity.get("reference_file_sha256"):
            raise ValueError("Frozen reference snapshot hash mismatch")
        reference = json.loads(reference_bytes.decode("utf-8-sig"))
        _reject_human_markers(reference)
        if (reference.get("reference_kind") != REFERENCE_KIND
                or reference.get("human_reviewed") is not False
                or reference.get("producer") != "Codex AI"
                or reference.get("input_file_sha256") != identity["input_file_sha256"]):
            raise ValueError("Frozen reference snapshot has invalid provenance")
        references = reference.get("cases", [])
        if (len(references) != len(cases) or {row.get("case_id") for row in references} != case_ids
                or any(not _valid_gaps(row.get("gap_ids")) for row in references)):
            raise ValueError("Frozen reference snapshot does not cover its phase exactly")
        manifest_hash = _sha(canonical_json(manifest).encode("utf-8"))
        records = []
        for case in cases:
            record = json.loads((directory / f"{case['id']}.json").read_text(encoding="utf-8"))
            if record.get("case_id") != case["id"] or record.get("manifest_sha256") != manifest_hash:
                raise ValueError("Saved record is bound to the wrong case or phase")
            payload = {key: value for key, value in record.items() if key != "payload_sha256"}
            if record.get("payload_sha256") != _sha(canonical_json(payload).encode("utf-8")):
                raise ValueError("Saved record payload hash mismatch")
            if record.get("reference_kind") != REFERENCE_KIND or record.get("human_reviewed") is not False:
                raise ValueError("Saved record has invalid reference provenance")
            records.append(record)
        mode = identity["mode"]
        if mode not in {"baseline", "ai"}:
            raise ValueError("Saved phase mode must be baseline or ai")
        modes.add(mode)
        models.add(identity.get("model"))
        knowledge_hashes.add(identity["knowledge_sha256"])
        taxonomy_hashes.add(identity["source_code_sha256"]["rolelens/taxonomy.py"])
        source_hashes.append(identity["source_code_sha256"])
        phase_hashes.append({"manifest_sha256": manifest_hash,
                             "input_file_sha256": identity["input_file_sha256"],
                             "reference_file_sha256": identity["reference_file_sha256"]})
        phase_buckets = Counter(row["bucket"] for row in cases)
        bucket_counts.update(phase_buckets)
        phase_results.append({
            "phase_id": identity.get("phase_id", f"historical_phase_{index}"),
            "case_count": len(cases),
            "bucket_counts": dict(phase_buckets),
            "freeze_recorded_at_utc": manifest["freeze_recorded_at_utc"],
            "source_code_sha256": identity["source_code_sha256"],
            "summary": summarize(records, reference, mode, manifest),
        })
        all_records.extend(records)
        all_references.extend(references)
    if len(modes) != 1 or len(models) != 1 or len(knowledge_hashes) != 1 or len(taxonomy_hashes) != 1:
        raise ValueError("Pool only phases with the same mode, model, knowledge and taxonomy")
    if expected_case_count is not None and len(all_records) != expected_case_count:
        raise ValueError("Pooled case count differs from the explicitly expected total")
    mode = next(iter(modes))
    aggregate_manifest = {
        "identity": {
            "input_file_sha256": _sha(canonical_json([row["input_file_sha256"] for row in phase_hashes]).encode("utf-8")),
            "reference_file_sha256": _sha(canonical_json([row["reference_file_sha256"] for row in phase_hashes]).encode("utf-8")),
            "phase_manifest_hashes": [row["manifest_sha256"] for row in phase_hashes],
        },
        "composition": "Descriptive pooling of separately frozen phases; not a single original preregistered batch",
    }
    result = summarize(all_records, {"cases": all_references}, mode, aggregate_manifest)
    result.update({
        "evaluation_type": "pooled_ai_reference_exploratory_" + mode,
        "aggregation": "All cases pooled at record level; abstentions contribute zero; phase percentages are not averaged",
        "phase_count": len(phases),
        "case_count": len(all_records),
        "bucket_counts": dict(bucket_counts),
        "unique_profile_count": len(seen_profiles),
        "phase_summaries": phase_results,
        "pooled_manifest": aggregate_manifest,
        "source_code_identical_across_phases": all(value == source_hashes[0] for value in source_hashes),
        "chronology_note": "Additional phases were frozen later. Report original and expansion results separately as well as pooled; pooled results are descriptive, not a new single frozen trial.",
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", nargs=3, action="append", metavar=("RUN_DIR", "CASES", "CASE_LOCK"), required=True)
    parser.add_argument("--expected-cases", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = pool_runs([tuple(Path(value) for value in phase) for phase in args.phase],
                        expected_case_count=args.expected_cases)
    # Exclusive create prevents accidentally replacing an earlier summary.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(_json_bytes(summary))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
