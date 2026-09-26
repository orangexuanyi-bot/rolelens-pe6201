"""Command line utility to create a reviewable hash lock for JSONL data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_core.evidence import write_lock  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--provenance", required=True)
    args = parser.parse_args()
    write_lock(args.data, args.lock, dataset_name=args.name, provenance=args.provenance)
    print(f"Locked {args.data} -> {args.lock}")


if __name__ == "__main__":
    main()
