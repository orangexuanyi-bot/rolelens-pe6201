"""Freeze, verify and summarize evaluation data without copying private text.

Freeze a data file before model tuning. The lock records a byte hash, record
IDs and record hashes. Evaluation refuses changed or duplicate data.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL line {line_no} in {path}") from exc
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise ValueError(f"Line {line_no} needs a string id")
            records.append(item)
    ids = [item["id"] for item in records]
    if not records or len(set(ids)) != len(ids):
        raise ValueError("Dataset is empty or contains duplicate IDs")
    return records


def make_lock(path: Path, *, dataset_name: str, provenance: str) -> dict:
    records = load_jsonl(path)
    return {
        "schema_version": 1,
        "dataset_name": dataset_name,
        "provenance": provenance,
        "source_file_sha256": sha256_bytes(path.read_bytes()),
        "record_count": len(records),
        "records": [
            {"id": item["id"], "sha256": sha256_bytes(canonical_json(item).encode("utf-8"))}
            for item in records
        ],
    }


def verify_lock(path: Path, lock_path: Path) -> list[dict]:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    current = make_lock(
        path,
        dataset_name=lock["dataset_name"],
        provenance=lock["provenance"],
    )
    if current != lock:
        raise ValueError(f"Dataset does not match frozen lock: {path}")
    return load_jsonl(path)


def write_lock(path: Path, lock_path: Path, *, dataset_name: str, provenance: str) -> None:
    lock = make_lock(path, dataset_name=dataset_name, provenance=provenance)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
