"""Validate ten student-entered references; this script never selects gap IDs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from project_core.evidence import canonical_json, verify_lock, write_lock  # noqa: E402
from rolelens.taxonomy import BY_ID  # noqa: E402

CASES = ROOT / "data" / "primary_cases_v2.jsonl"
LOCK = ROOT / "data" / "primary_cases_v2_lock.json"
PROTOCOL = ROOT / "data" / "primary_protocol_v2.json"
TAXONOMY_SOURCE = ROOT / "rolelens" / "taxonomy.py"
FIELDS = ["case_id", "gap_1", "gap_2", "gap_3", "review_reason", "review_date", "reviewer"]


def load_decisions(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError("Decision columns differ from the blind packet; do not add a baseline acceptance column")
        return list(reader)


def finalize(decisions_path: Path, packet_manifest_path: Path, out_dir: Path) -> Path:
    cases = verify_lock(CASES, LOCK)
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if protocol["taxonomy_sha256_at_freeze"] != hashlib.sha256(TAXONOMY_SOURCE.read_bytes()).hexdigest():
        raise ValueError("Taxonomy changed after the independent review protocol was frozen")
    packet = json.loads(packet_manifest_path.read_text(encoding="utf-8"))
    if packet.get("primary_lock_sha256") != hashlib.sha256(LOCK.read_bytes()).hexdigest():
        raise ValueError("Packet does not match the frozen primary input lock")
    packet_rows = packet.get("cases")
    if not isinstance(packet_rows, list) or len(packet_rows) != 10:
        raise ValueError("Packet manifest must contain ten cases")
    if any("candidate_top3" in row or "model_suggestion" in row for row in packet_rows):
        raise ValueError("Blind packet must not contain predictions")
    packet_by_id = {row["case_id"]: row for row in packet_rows}
    decisions = load_decisions(decisions_path)
    if len(decisions) != 10 or len({row["case_id"] for row in decisions}) != 10:
        raise ValueError("All ten distinct student decisions are required")
    decisions_by_id = {row["case_id"]: row for row in decisions}
    case_ids = {case["id"] for case in cases}
    if set(packet_by_id) != case_ids or set(decisions_by_id) != case_ids:
        raise ValueError("Decision or packet IDs differ from frozen primary inputs")
    finalized = []
    for case in cases:
        case_id = case["id"]
        row = decisions_by_id[case_id]
        case_hash = hashlib.sha256(canonical_json(case).encode("utf-8")).hexdigest()
        if packet_by_id[case_id]["frozen_case_sha256"] != case_hash:
            raise ValueError(f"{case_id}: input changed after the blind packet was built")
        selected = [row[f"gap_{i}"].strip() for i in (1, 2, 3)]
        if len(set(selected)) != 3 or any(identifier not in BY_ID for identifier in selected):
            raise ValueError(f"{case_id}: choose three distinct product-facing taxonomy IDs")
        reason = row["review_reason"].strip()
        if len(reason) < 12:
            raise ValueError(f"{case_id}: explain your independent evidence-based choice")
        reviewer = row["reviewer"].strip()
        if not reviewer:
            raise ValueError(f"{case_id}: enter the student reviewer name")
        try:
            reviewed_on = date.fromisoformat(row["review_date"].strip())
        except ValueError as exc:
            raise ValueError(f"{case_id}: enter a valid YYYY-MM-DD review date") from exc
        if reviewed_on < date(2026, 9, 26) or reviewed_on > date.today():
            raise ValueError(f"{case_id}: review date must be between freeze day and today")
        finalized.append({
            **case,
            "reference_status": "human_reviewed",
            "reference_gaps": selected,
            "review_reason": reason,
            "review_date": reviewed_on.isoformat(),
            "reviewer": reviewer,
            "reference_provenance": "Student-entered independent three-ID review of full fictional JD and CV pair",
        })
    output = out_dir / "human_reference_cases_v2.jsonl"
    output_lock = out_dir / "human_reference_cases_v2_lock.json"
    if output.exists() or output_lock.exists():
        raise FileExistsError("Refusing to overwrite an existing student-reviewed reference")
    out_dir.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in finalized), encoding="utf-8", newline="\n")
    write_lock(output, output_lock, dataset_name="RoleLens v2 ten student-reviewed fictional PM references", provenance="Student-entered blind review; see private dated decisions CSV")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--packet-manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "private" / "reviewed_reference_v2")
    args = parser.parse_args()
    output = finalize(args.decisions, args.packet_manifest, args.out_dir)
    print(f"Validated ten independent student decisions and locked {output}")


if __name__ == "__main__":
    main()
