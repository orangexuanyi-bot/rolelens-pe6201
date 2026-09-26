"""Versioned, product-facing AI PM and commercial PM capability vocabulary."""

from __future__ import annotations

import re

CAPABILITIES = (
    {"id": "PRODUCT_STRATEGY", "label": "Product strategy", "aliases": ("product strategy", "product vision", "market strategy", "product direction", "portfolio strategy")},
    {"id": "USER_DISCOVERY", "label": "User and customer discovery", "aliases": ("user research", "customer discovery", "user interviews", "customer interviews", "user needs", "customer needs", "market research")},
    {"id": "PRIORITIZATION", "label": "Roadmap and prioritization", "aliases": ("prioritization", "prioritisation", "roadmap", "product planning", "scope tradeoffs", "scope trade-offs", "feature priorities")},
    {"id": "METRICS_EXPERIMENTATION", "label": "Product metrics and experimentation", "aliases": ("metrics", "experimentation", "experiments", "a/b test", "ab testing", "kpi", "north star", "success measures")},
    {"id": "AI_PRODUCT_LITERACY", "label": "AI product literacy", "aliases": ("ai product", "generative ai", "genai", "large language model", "llm", "foundation model", "model capabilities", "ai use cases", "machine learning product")},
    {"id": "AI_EVALUATION", "label": "AI quality and evaluation", "aliases": ("model evaluation", "ai evaluation", "evals", "output quality", "human evaluation", "quality rubric", "benchmark", "model quality", "ai quality")},
    {"id": "DATA_DECISIONS", "label": "Data-informed product decisions", "aliases": ("product analytics", "data analysis", "data-informed", "funnel analysis", "cohort analysis", "dashboard", "customer insights", "data-driven")},
    {"id": "SAFETY_PRIVACY", "label": "Trust, safety and privacy", "aliases": ("safety", "privacy", "responsible ai", "trust and safety", "risk management", "compliance", "guardrails", "data protection")},
    {"id": "CROSS_FUNCTIONAL", "label": "Cross-functional product leadership", "aliases": ("cross-functional", "stakeholders", "engineering partners", "design partners", "design and engineering", "sales partners", "collaboration", "product leadership")},
    {"id": "MONETIZATION_PRICING", "label": "Monetization and pricing", "aliases": ("monetization", "monetisation", "pricing", "subscription", "paid plan", "paywall", "revenue model", "packaging", "arpu", "commercial model")},
    {"id": "ADS_ECOSYSTEM", "label": "Ads and advertiser products", "aliases": ("advertising", "ads product", "ad product", "advertiser", "campaign", "ad measurement", "roas", "cpm", "bidding", "sponsored content")},
    {"id": "GO_TO_MARKET", "label": "Go-to-market and positioning", "aliases": ("go-to-market", "gtm", "positioning", "market entry", "sales enablement", "product launch", "launch plan", "distribution strategy")},
    {"id": "GROWTH_LIFECYCLE", "label": "Growth and lifecycle", "aliases": ("growth", "activation", "acquisition", "retention", "lifecycle", "conversion", "onboarding", "engagement")},
    {"id": "COMMERCIAL_PARTNERSHIPS", "label": "Commercial partnerships", "aliases": ("partnerships", "business development", "partner ecosystem", "channel partners", "strategic alliances", "commercial partners")},
)

BY_ID = {item["id"]: item for item in CAPABILITIES}
TAXONOMY_VERSION = "2.0"
NEGATION = re.compile(r"\b(no|not|never|without|lack|lacks|lacking|neither|didn't|haven't|hasn't|don't|doesn't)\b", re.I)
CLAUSE_BREAK = re.compile(r"\b(?:but|however|although|whereas)\b|[;:]", re.I)


def sentences(text: str) -> list[str]:
    """Keep exact source substrings for quote verification."""
    return [part.strip(" \t\r\n-•") for part in re.split(r"(?<=[.!?])\s+|[\r\n]+", text) if part.strip(" \t\r\n-•")]


def _alias_matches(sentence: str, alias: str) -> list[re.Match[str]]:
    pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"
    return list(re.finditer(pattern, sentence, flags=re.I))


def evidence_for(text: str, capability: dict, *, ignore_negated: bool = False) -> list[dict]:
    evidence = []
    for sentence in sentences(text):
        matched = []
        for alias in capability["aliases"]:
            for match in _alias_matches(sentence, alias):
                preceding = sentence[:match.start()]
                clause = CLAUSE_BREAK.split(preceding)[-1]
                if ignore_negated and NEGATION.search(clause):
                    continue
                matched.append(alias)
                break
        if matched:
            evidence.append({"quote": sentence[:350], "aliases": matched})
    return evidence
