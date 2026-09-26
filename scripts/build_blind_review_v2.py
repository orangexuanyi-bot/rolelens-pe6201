"""Create the private, prediction-free packet for ten student reference decisions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from project_core.evidence import canonical_json, verify_lock  # noqa: E402
from rolelens.taxonomy import BY_ID  # noqa: E402

CASES = ROOT / "data" / "primary_cases_v2.jsonl"
LOCK = ROOT / "data" / "primary_cases_v2_lock.json"
PROTOCOL = ROOT / "data" / "primary_protocol_v2.json"
CARDS = ROOT / "data" / "synthetic_jds_v2.json"
PROFILES = ROOT / "data" / "synthetic_profiles" / "profiles.json"
TAXONOMY_SOURCE = ROOT / "rolelens" / "taxonomy.py"
FIELDS = ["case_id", "gap_1", "gap_2", "gap_3", "review_reason", "review_date", "reviewer"]


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a blinded packet; no baseline or AI prediction is computed")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "private" / "review_packet_v2")
    args = parser.parse_args()
    cases = verify_lock(CASES, LOCK)
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if len(cases) != 10 or protocol["input_case_lock_sha256"] != hash_file(LOCK):
        raise ValueError("Primary case count or protocol lock mismatch")
    if protocol["source_cards_sha256"] != hash_file(CARDS) or protocol["source_profiles_sha256"] != hash_file(PROFILES):
        raise ValueError("Source fixtures changed after freeze")
    if protocol["taxonomy_sha256_at_freeze"] != hash_file(TAXONOMY_SOURCE):
        raise ValueError("Taxonomy changed after freeze")
    cards = {row["id"]: row for row in json.loads(CARDS.read_text(encoding="utf-8"))}
    profiles = {row["id"]: row for row in json.loads(PROFILES.read_text(encoding="utf-8"))}
    decision_path = args.out_dir / "decisions.csv"
    if decision_path.exists():
        raise FileExistsError(f"Refusing to overwrite student decisions: {decision_path}")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    markdown = [
        "# RoleLens v2: blinded ten-case student review",
        "",
        "The ten JD cards and CVs below are original fictional inputs. The linked employer pages supply role-family context; these cards are not official JD wording or live vacancies. Read each complete pair and, if available, check the linked source page. Independently choose the three most important preparation-gap capability IDs for the fictional candidate. Explain your reasoning and record your own name and date in `decisions.csv`. No baseline prediction, AI answer, proposed gap or reference label is included in this packet.",
        "",
        "A gap means a role-relevant preparation area with limited positive evidence in this fictional profile. Missing wording does not prove lack of ability. Do not infer protected characteristics, make a hiring decision, or require coding proficiency merely because the PM works with engineers.",
        "",
        "## Shared capability vocabulary",
        "",
        *[f"- `{identifier}` — {item['label']}" for identifier, item in BY_ID.items()],
        "",
    ]
    packet_cases = []
    decisions = []
    for case in cases:
        card = cards.get(case["synthetic_jd_card_id"])
        profile = profiles.get(case["profile_id"])
        if not card or card.get("synthetic") is not True or card["jd_text"] != case["jd"]:
            raise ValueError(f"{case['id']}: JD is not the frozen fictional card")
        if not profile or profile.get("synthetic") is not True or profile["cv_text"] != case["profile"]:
            raise ValueError(f"{case['id']}: profile is not the frozen fictional CV")
        case_hash = hashlib.sha256(canonical_json(case).encode("utf-8")).hexdigest()
        markdown.extend([
            f"## {case['id']} — {case['bucket']}",
            "",
            f"Source employer and role: {case['jd_source_company']} — {case['jd_source_title']}",
            f"Source URL: {case['jd_source_url']}",
            f"Original fictional card: {case['synthetic_jd_card_id']}; fictional CV: {case['profile_id']}",
            f"Frozen case SHA-256: `{case_hash}`",
            "",
            "### Complete fictional JD card",
            "",
            "```text",
            case["jd"],
            "```",
            "",
            "### Complete fictional candidate profile",
            "",
            "```text",
            case["profile"],
            "```",
            "",
            "Your independent gap IDs: __________ / __________ / __________",
            "Your evidence-based reason: ______________________________________________",
            "",
        ])
        decisions.append({field: case["id"] if field == "case_id" else "" for field in FIELDS})
        packet_cases.append({
            "case_id": case["id"],
            "frozen_case_sha256": case_hash,
            "reference_status": "PENDING_STUDENT_REVIEW",
            "synthetic": True,
        })
    (args.out_dir / "review_packet.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    with decision_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(decisions)
    manifest = {"protocol_version": protocol["protocol_version"], "primary_lock_sha256": hash_file(LOCK), "cases": packet_cases}
    (args.out_dir / "packet_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created ten blinded fictional review cards and empty decisions at {args.out_dir}")


if __name__ == "__main__":
    main()
