#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from crypto_kg_pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run field extraction, entity building and contradiction detection.")
    parser.add_argument("--input", required=True, help="Input JSON file produced by table schema mapping step.")
    parser.add_argument("--output", default="kg_pipeline_output.json", help="Output JSON path.")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = run_pipeline(payload)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()
