"""Reject JDs outside AI or commercial product management roles."""

from __future__ import annotations

import re

PM_TITLE = re.compile(r"\b(product manager|product management|product lead|AI PM|ads PM|commercial PM)\b", re.I)
AI_TOPIC = re.compile(r"\b(AI|LLM|generative AI|GenAI|foundation model|machine learning|model evaluation|AI product)\b", re.I)
COMMERCIAL_TOPIC = re.compile(r"\b(monetiz\w+|monetis\w+|pricing|subscription|revenue|advertis\w+|ads|advertiser|commercial|go-to-market|growth)\b", re.I)


def check_scope(jd: str) -> tuple[bool, str]:
    title = next((line.strip() for line in jd.splitlines() if line.strip()), "")
    if not PM_TITLE.search(title):
        return False, "NOT_A_PRODUCT_MANAGER_ROLE"
    ai = bool(AI_TOPIC.search(jd))
    commercial = bool(COMMERCIAL_TOPIC.search(jd))
    if ai and commercial:
        return True, "AI_AND_COMMERCIAL_PM"
    if ai:
        return True, "AI_PM"
    if commercial:
        return True, "COMMERCIAL_PM"
    return False, "PM_ROLE_OUTSIDE_AI_OR_COMMERCIAL_SCOPE"
