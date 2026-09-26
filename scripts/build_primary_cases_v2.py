"""Freeze new blinded synthetic PM cases before any prediction is generated.

The pairing schedule is fixed here: PMJD01–10 map to RL-P11–15 and
RL-P21, RL-P22, RL-P26, RL-P24, RL-P25. These profiles did not occur in the
archived v1 pilot. Existing locks are never overwritten.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from project_core.evidence import verify_lock, write_lock  # noqa: E402
from rolelens.scope import check_scope  # noqa: E402
from rolelens.taxonomy import TAXONOMY_VERSION  # noqa: E402

CARDS = ROOT / "data" / "synthetic_jds_v2.json"
PROFILES = ROOT / "data" / "synthetic_profiles" / "profiles.json"
CASES = ROOT / "data" / "primary_cases_v2.jsonl"
LOCK = ROOT / "data" / "primary_cases_v2_lock.json"
PROTOCOL = ROOT / "data" / "primary_protocol_v2.json"
TAXONOMY_SOURCE = ROOT / "rolelens" / "taxonomy.py"
PROFILE_IDS = tuple([f"RL-P{i:02d}" for i in range(11, 16)] + ["RL-P21", "RL-P22", "RL-P26", "RL-P24", "RL-P25"])
CASE_IDS = tuple(f"RLV2F-{i:02d}" for i in range(1, 11))
CARD_IDS = tuple(f"PMJD{i:02d}" for i in range(1, 11))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if any(path.exists() for path in (CASES, LOCK, PROTOCOL)):
        if not all(path.exists() for path in (CASES, LOCK, PROTOCOL)):
            raise ValueError("Incomplete existing v2 freeze; inspect files manually")
        verify_lock(CASES, LOCK)
        protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        if protocol["source_cards_sha256"] != sha(CARDS) or protocol["source_profiles_sha256"] != sha(PROFILES):
            raise ValueError("Source fixture changed after freeze; use a new protocol version")
        if protocol["input_case_lock_sha256"] != sha(LOCK):
            raise ValueError("Input lock bytes changed after freeze")
        if protocol["taxonomy_sha256_at_freeze"] != sha(TAXONOMY_SOURCE):
            raise ValueError("Taxonomy code changed after freeze")
        print("Existing v2 input freeze verified; no files changed")
        return

    cards = json.loads(CARDS.read_text(encoding="utf-8"))
    profiles = {row["id"]: row for row in json.loads(PROFILES.read_text(encoding="utf-8"))}
    if not isinstance(cards, list) or tuple(card["id"] for card in cards) != CARD_IDS:
        raise ValueError("Expected ten new PMJD01–PMJD10 cards in fixed order")
    if [card["bucket"] for card in cards] != ["AI_PM"] * 5 + ["COMMERCIAL_PM"] * 5:
        raise ValueError("Expected five AI PM and five commercial PM cases")
    if len({card["source_url"] for card in cards}) != 10:
        raise ValueError("Each primary card needs its own public source URL")
    rows = []
    for case_id, card, profile_id in zip(CASE_IDS, cards, PROFILE_IDS):
        profile = profiles[profile_id]
        if card.get("synthetic") is not True or profile.get("synthetic") is not True:
            raise ValueError("Primary inputs must be fictional synthetic materials")
        if not card["source_url"].startswith("https://"):
            raise ValueError("Source URL must use HTTPS")
        if "product manager" not in card["jd_text"].splitlines()[0].lower():
            raise ValueError("Synthetic JD first line needs an explicit PM title")
        if not check_scope(card["jd_text"])[0]:
            raise ValueError("Synthetic JD failed the PM-only scope guard")
        if hashlib.sha256(profile["cv_text"].encode("utf-8")).hexdigest() != profile["sha256_cv_text"]:
            raise ValueError("Synthetic profile text hash mismatch")
        rows.append({
            "id": case_id,
            "bucket": card["bucket"],
            "synthetic_jd_card_id": card["id"],
            "profile_id": profile_id,
            "jd_source_company": card["source_company"],
            "jd_source_title": card["source_role_title"],
            "jd_source_url": card["source_url"],
            "jd": card["jd_text"],
            "profile": profile["cv_text"],
            "reference_status": "PENDING_STUDENT_REVIEW",
        })
    CASES.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8", newline="\n")
    write_lock(CASES, LOCK, dataset_name="RoleLens v2 blinded primary PM input cases", provenance="Ten original synthetic PM JDs paired by pre-registered ID with ten fictional CV profiles; no predictions or labels")
    protocol = {
        "protocol_version": "2.1",
        "freeze_date": "2026-09-26",
        "scope": "Five AI product manager and five commercialization or ads product manager fictional roles",
        "taxonomy_version_at_freeze": TAXONOMY_VERSION,
        "taxonomy_sha256_at_freeze": sha(TAXONOMY_SOURCE),
        "case_ids": list(CASE_IDS),
        "card_ids": list(CARD_IDS),
        "profile_ids": list(PROFILE_IDS),
        "pairing_rule": "Fixed source-card order; no selection by model or baseline outcome",
        "pre_evaluation_revision": "PMJD06 source title was corrected to an official Product Manager title, and PMJD08 was re-paired from engineer RL-P23 to unused product-coordinator RL-P26 for PM-career scope. The preliminary v2.0 lock was archived outside this repository before any prediction or student label; final case IDs are new.",
        "source_cards_sha256": sha(CARDS),
        "source_profiles_sha256": sha(PROFILES),
        "input_case_lock_sha256": sha(LOCK),
        "reference_status": "PENDING_STUDENT_REVIEW",
        "predictions_run_at_freeze": False,
    }
    PROTOCOL.write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Frozen {len(rows)} blinded v2 PM inputs at {CASES}; no predictions were computed")


if __name__ == "__main__":
    main()
