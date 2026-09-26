"""Deterministic evidence checks for model-generated role analysis."""

from __future__ import annotations

from .taxonomy import BY_ID

VALID_STATUS = {"strong", "partial", "not_evidenced"}
EXPECTED_KEYS = {"summary", "responsibilities", "capabilities", "top_gaps", "knowledge_citations", "limitations"}


def _text(value: object, *, max_length: int = 800) -> bool:
    return isinstance(value, str) and 0 < len(value.strip()) <= max_length


def validate_analysis(report: object, jd: str, profile: str, retrieved: list[dict]) -> list[str]:
    """Return machine-readable error codes. No output is accepted on failure."""
    errors: list[str] = []
    if not isinstance(report, dict) or set(report) != EXPECTED_KEYS:
        return ["SCHEMA_TOP_LEVEL"]
    if not _text(report["summary"], max_length=1200):
        errors.append("SUMMARY_INVALID")
    responsibilities = report["responsibilities"]
    if not isinstance(responsibilities, list) or not 1 <= len(responsibilities) <= 5:
        errors.append("RESPONSIBILITIES_COUNT")
    else:
        for item in responsibilities:
            if not isinstance(item, dict) or set(item) != {"statement", "jd_quote"}:
                errors.append("RESPONSIBILITY_SCHEMA")
                continue
            if not _text(item["statement"]) or not _text(item["jd_quote"], max_length=350) or item["jd_quote"] not in jd:
                errors.append("RESPONSIBILITY_JD_QUOTE")
    capabilities = report["capabilities"]
    seen: set[str] = set()
    statuses: dict[str, str] = {}
    if not isinstance(capabilities, list) or not 3 <= len(capabilities) <= len(BY_ID):
        errors.append("CAPABILITIES_COUNT")
    else:
        for item in capabilities:
            if not isinstance(item, dict) or set(item) != {"capability_id", "jd_quote", "profile_status", "profile_quote"}:
                errors.append("CAPABILITY_SCHEMA")
                continue
            identifier = item["capability_id"]
            if not isinstance(identifier, str) or identifier not in BY_ID or identifier in seen:
                errors.append("CAPABILITY_ID")
                continue
            seen.add(identifier)
            status = item["profile_status"]
            if not isinstance(status, str) or status not in VALID_STATUS:
                errors.append("PROFILE_STATUS")
                continue
            statuses[identifier] = status
            if not _text(item["jd_quote"], max_length=350) or item["jd_quote"] not in jd:
                errors.append("CAPABILITY_JD_QUOTE")
            profile_quote = item["profile_quote"]
            if status == "not_evidenced" and profile_quote != "":
                errors.append("UNSUPPORTED_PROFILE_QUOTE")
            if status in {"strong", "partial"} and (not _text(profile_quote, max_length=350) or profile_quote not in profile):
                errors.append("PROFILE_QUOTE")
    gaps = report["top_gaps"]
    if not isinstance(gaps, list) or len(gaps) != 3:
        errors.append("GAPS_COUNT")
    else:
        gap_ids = []
        for item in gaps:
            if not isinstance(item, dict) or set(item) != {"capability_id", "why_now", "prep_action"}:
                errors.append("GAP_SCHEMA")
                continue
            identifier = item["capability_id"]
            if not isinstance(identifier, str):
                errors.append("GAP_UNSUPPORTED")
                continue
            gap_ids.append(identifier)
            if identifier not in statuses or statuses.get(identifier) == "strong":
                errors.append("GAP_UNSUPPORTED")
            if not _text(item["why_now"]) or not _text(item["prep_action"]):
                errors.append("GAP_TEXT")
        if len(set(gap_ids)) != len(gap_ids):
            errors.append("GAP_DUPLICATE")
    citations = report["knowledge_citations"]
    docs = {doc["id"]: doc for doc in retrieved}
    if not isinstance(citations, list) or not 1 <= len(citations) <= len(retrieved):
        errors.append("CITATIONS_COUNT")
    else:
        cited_ids = set()
        for item in citations:
            if not isinstance(item, dict) or set(item) != {"doc_id", "quote"}:
                errors.append("CITATION_SCHEMA")
                continue
            identifier = item["doc_id"]
            if not isinstance(identifier, str) or identifier not in docs or identifier in cited_ids:
                errors.append("CITATION_DOC_ID")
                continue
            cited_ids.add(identifier)
            if not _text(item["quote"], max_length=350) or item["quote"] not in docs[identifier]["text"]:
                errors.append("CITATION_QUOTE")
    limitations = report["limitations"]
    if not isinstance(limitations, list) or not all(_text(item, max_length=400) for item in limitations):
        errors.append("LIMITATIONS_SCHEMA")
    return sorted(set(errors))
