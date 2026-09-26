"""Convert AI and commercial official-source metadata into 30 short notes.

Only author-written summaries are indexed. No source article text is copied.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI_SOURCE = ROOT / "data" / "source_manifests" / "ai_docs.json"
COMMERCIAL_SOURCE = ROOT / "data" / "source_manifests" / "commercial_knowledge_sources.json"
OUTPUT = ROOT / "data" / "knowledge_notes.jsonl"


def main() -> None:
    ai_sources = json.loads(AI_SOURCE.read_text(encoding="utf-8"))
    commercial_sources = json.loads(COMMERCIAL_SOURCE.read_text(encoding="utf-8"))
    if len(ai_sources) != 20 or len({item["id"] for item in ai_sources}) != 20:
        raise ValueError("Expected 20 unique official document links")
    if len(commercial_sources) != 10 or len({item["id"] for item in commercial_sources}) != 10:
        raise ValueError("Expected 10 unique commercial document links")
    ai_notes = [
        {
            "id": item["id"],
            "title": item["title"],
            "url": item["url"],
            "accessed_at": item["checked_at_utc"][:10],
            "text": item["summary_own_words"],
            "domain": "ai_product",
            "note_provenance": "author-written summary of linked official page; not a verbatim quote",
        }
        for item in ai_sources
    ]
    commercial_notes = [
        {
            "id": item["id"],
            "title": item["title"],
            "url": item["url"],
            "accessed_at": item["checked_at_utc"][:10],
            "text": item["summary"],
            "domain": "commercial_product",
            "publisher": item["publisher"],
            "topic": item["topic"],
            "note_provenance": "author-written summary of linked official page; not a verbatim quote",
        }
        for item in commercial_sources
    ]
    notes = ai_notes + commercial_notes
    if len({item["id"] for item in notes}) != 30:
        raise ValueError("Knowledge note IDs must be unique across both families")
    OUTPUT.write_text("".join(json.dumps(note, ensure_ascii=False) + "\n" for note in notes), encoding="utf-8", newline="\n")
    print(f"Wrote {len(notes)} knowledge notes to {OUTPUT}")


if __name__ == "__main__":
    main()
