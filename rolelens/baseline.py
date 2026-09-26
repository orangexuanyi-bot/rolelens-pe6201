"""A deliberately simple, deterministic non-AI comparison."""

from __future__ import annotations

import re

from .taxonomy import CAPABILITIES, TAXONOMY_VERSION, evidence_for, sentences

REQUIREMENT_MARKERS = re.compile(r"\b(required|must|need|experience|expertise|proficient|essential)\b", re.I)
OUTCOME_MARKERS = re.compile(r"\b(built|shipped|launched|led|owned|measured|evaluated|improved|designed|delivered)\b|\d+%", re.I)
RESPONSIBILITY_MARKERS = re.compile(r"\b(own|lead|build|drive|partner|deliver|define|manage|develop)\b", re.I)


def keyword_baseline(jd: str, profile: str) -> dict:
    """Rank gaps using JD alias hits and profile keyword evidence.

    The status is a lexical proxy and does not establish actual ability.
    """
    capabilities = []
    for item in CAPABILITIES:
        jd_evidence = evidence_for(jd, item)
        if not jd_evidence:
            continue
        profile_evidence = evidence_for(profile, item, ignore_negated=True)
        if not profile_evidence:
            status = "not_evidenced"
        elif any(OUTCOME_MARKERS.search(entry["quote"]) for entry in profile_evidence):
            status = "strong_keyword_evidence"
        else:
            status = "partial_keyword_evidence"
        priority = sum(2 if REQUIREMENT_MARKERS.search(entry["quote"]) else 1 for entry in jd_evidence)
        capabilities.append(
            {
                "capability_id": item["id"],
                "label": item["label"],
                "jd_quote": jd_evidence[0]["quote"],
                "profile_status": status,
                "profile_quote": profile_evidence[0]["quote"] if profile_evidence else "",
                "keyword_priority_score": priority,
            }
        )
    gap_candidates = [row for row in capabilities if row["profile_status"] != "strong_keyword_evidence"]
    gap_candidates.sort(key=lambda row: (-row["keyword_priority_score"], row["profile_status"] != "not_evidenced", row["capability_id"]))
    responsibilities = [sentence for sentence in sentences(jd) if RESPONSIBILITY_MARKERS.search(sentence)][:3]
    return {
        "method": "weighted_keyword_overlap",
        "taxonomy_version": TAXONOMY_VERSION,
        "responsibilities": responsibilities,
        "capabilities": capabilities,
        "top_gaps": [row["capability_id"] for row in gap_candidates[:3]],
        "abstained": len(gap_candidates) < 3,
        "abstain_reason": "FEWER_THAN_THREE_EVIDENCED_JD_GAPS" if len(gap_candidates) < 3 else None,
        "limitation": "Keyword evidence is a proxy. Missing words do not prove missing skill; positive words do not prove proficiency.",
    }
