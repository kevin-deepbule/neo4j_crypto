"""Command line interface for local extraction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crypto_kg.graph import Neo4jKnowledgeGraphStore
from crypto_kg.graph import export_cypher
from crypto_kg.pipeline import extract_kg, result_to_dict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract crypto evaluation report data to JSON or Cypher.")
    parser.add_argument("document", help="Path to .docx, .pdf or .txt report")
    parser.add_argument("--system-id", default="unknown-system", help="Target System.id used for entity IDs")
    parser.add_argument("--report-id", default=None, help="Optional Report.id")
    parser.add_argument("--format", choices=("json", "cypher"), default="json")
    parser.add_argument("--output", "-o", default=None, help="Output file path")
    parser.add_argument("--write-neo4j", action="store_true", help="Write extracted entities and relations to Neo4j")
    parser.add_argument("--system-name", default=None, help="System.name used when --write-neo4j creates the System node")
    args = parser.parse_args(argv)

    result = extract_kg(args.document, system_id=args.system_id, report_id=args.report_id)
    if args.write_neo4j:
        store = Neo4jKnowledgeGraphStore()
        try:
            counters = store.upsert_extraction(result, system_name=args.system_name)
        finally:
            store.close()
        print(f"Wrote Neo4j entities={counters['entities']} relations={counters['relations']}")

    if args.format == "json":
        data = result_to_dict(result)
        content = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        content = export_cypher(result)

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
