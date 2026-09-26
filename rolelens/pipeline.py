"""RoleLens orchestration with a visible baseline and fail-closed AI mode."""

from __future__ import annotations

import re
from pathlib import Path

from .baseline import keyword_baseline
from .provider import DEFAULT_MODEL, call_openrouter
from .retrieval import load_knowledge, retrieve
from .scope import check_scope
from .validation import validate_analysis

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[ .()-]?){9,}(?!\d)")


def has_obvious_contact_details(value: str) -> bool:
    return bool(EMAIL_RE.search(value) or PHONE_RE.search(value))


def analyze(
    jd: str,
    profile: str,
    knowledge_path: Path,
    *,
    mode: str = "baseline",
    allow_external_processing: bool = False,
    model: str = DEFAULT_MODEL,
) -> dict:
    if mode not in {"baseline", "ai"}:
        raise ValueError("mode must be baseline or ai")
    if not 80 <= len(jd.strip()) <= 20000:
        return {"status": "abstain", "reason_codes": ["JD_LENGTH_OUT_OF_RANGE"], "mode": mode}
    if not 30 <= len(profile.strip()) <= 12000:
        return {"status": "abstain", "reason_codes": ["PROFILE_LENGTH_OUT_OF_RANGE"], "mode": mode}
    in_scope, scope_bucket = check_scope(jd)
    if not in_scope:
        return {"status": "abstain", "reason_codes": [scope_bucket], "mode": mode, "scope_bucket": "OUT_OF_SCOPE"}
    baseline = keyword_baseline(jd, profile)
    documents = load_knowledge(knowledge_path)
    query = jd[:6000]
    retrieved = retrieve(query, documents, k=3, role_family=scope_bucket)
    public_retrieval = [
        {"id": doc["id"], "title": doc["title"], "url": doc["url"], "accessed_at": doc["accessed_at"], "domain": doc["domain"], "score": doc["retrieval_score"]}
        for doc in retrieved
    ]
    result = {
        "mode": mode,
        "scope_bucket": scope_bucket,
        "status": "ok",
        "baseline": baseline,
        "retrieved_knowledge": public_retrieval,
        "reason_codes": [],
        "privacy": "Inputs are processed in memory and are not saved by this program.",
    }
    if mode == "baseline":
        if baseline["abstained"]:
            result["status"] = "abstain"
            result["reason_codes"] = [baseline["abstain_reason"]]
        return result
    if not allow_external_processing:
        result.update(status="abstain", reason_codes=["EXTERNAL_PROCESSING_NOT_AUTHORIZED"])
        return result
    if has_obvious_contact_details(profile):
        result.update(status="abstain", reason_codes=["PROFILE_CONTACT_DETAILS_DETECTED"])
        return result
    if len(retrieved) < 3:
        result.update(status="abstain", reason_codes=["INSUFFICIENT_KNOWLEDGE_RETRIEVAL"])
        return result
    try:
        report, metadata = call_openrouter(jd, profile, retrieved, model=model)
    except RuntimeError as exc:
        result.update(status="abstain", reason_codes=[str(exc)])
        return result
    result["model_run"] = metadata
    if metadata.get("provider_error"):
        result.update(status="abstain", reason_codes=[metadata["provider_error"]])
        return result
    errors = validate_analysis(report, jd, profile, retrieved)
    if errors:
        result.update(status="abstain", reason_codes=errors)
        return result
    docs = {doc["id"]: doc for doc in retrieved}
    for citation in report["knowledge_citations"]:
        citation["title"] = docs[citation["doc_id"]]["title"]
        citation["url"] = docs[citation["doc_id"]]["url"]
        citation["accessed_at"] = docs[citation["doc_id"]]["accessed_at"]
    result["analysis"] = report
    return result
