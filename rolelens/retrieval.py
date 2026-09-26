"""Local lexical retrieval over curated knowledge notes with source links."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z][a-z0-9]{2,}")
STOP = frozenset("the and for with that from this have will your into their about can are what how why which".split())


def tokenize(text: str) -> list[str]:
    return [word for word in TOKEN_RE.findall(text.lower()) if word not in STOP]


def load_knowledge(path: Path) -> list[dict]:
    documents = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                documents.append(json.loads(line))
    ids = [doc.get("id") for doc in documents]
    if not documents or len(ids) != len(set(ids)):
        raise ValueError("Knowledge notes missing or have duplicate IDs")
    for doc in documents:
        if not all(isinstance(doc.get(key), str) and doc[key].strip() for key in ("id", "title", "url", "text", "accessed_at")):
            raise ValueError("Knowledge note needs id, title, url, text, accessed_at")
        if not doc["url"].startswith("https://"):
            raise ValueError("Knowledge note URL must use HTTPS")
        if doc.get("domain") not in {"ai_product", "commercial_product"}:
            raise ValueError("Knowledge note needs an explicit product-role domain")
    return documents


def retrieve(query: str, documents: list[dict], *, k: int = 3, role_family: str | None = None) -> list[dict]:
    if not documents:
        return []
    if role_family == "AI_PM":
        documents = [doc for doc in documents if doc["domain"] == "ai_product"]
    elif role_family == "COMMERCIAL_PM":
        documents = [doc for doc in documents if doc["domain"] == "commercial_product"]
    if not documents:
        return []
    tokenized = [Counter(tokenize(doc["title"] + " " + doc["text"])) for doc in documents]
    query_counts = Counter(tokenize(query))
    if not query_counts:
        return []
    df = Counter()
    for counts in tokenized:
        df.update(counts.keys())
    n = len(documents)
    scores = []
    for doc, counts in zip(documents, tokenized):
        score = sum(
            (1 + math.log(counts[word])) * (1 + math.log(query_counts[word])) * math.log((n + 1) / (df[word] + 1))
            for word in query_counts.keys() & counts.keys()
        )
        scores.append((score, doc))
    scores.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    positive = [(score, doc) for score, doc in scores if score > 0]
    if role_family == "AI_AND_COMMERCIAL_PM" and k >= 2:
        # Reserve one note from each relevant family, then fill by lexical score.
        chosen = []
        for domain in ("ai_product", "commercial_product"):
            first = next(((score, doc) for score, doc in positive if doc["domain"] == domain), None)
            if first:
                chosen.append(first)
        selected_ids = {doc["id"] for _, doc in chosen}
        chosen.extend((score, doc) for score, doc in positive if doc["id"] not in selected_ids)
        positive = chosen
    return [{**doc, "retrieval_score": round(score, 6)} for score, doc in positive[:k]]
