from __future__ import annotations

from typing import Any, Dict, List

from .contradiction_detector import ContradictionDetector
from .entity_builder import EntityBuilder
from .field_extractor import FieldExtractor
from .models import RawTableRow, to_jsonable


def parse_rows(payload: Dict[str, Any]) -> List[RawTableRow]:
    rows = []
    for item in payload.get("tables", []):
        schema_id = item["schema_id"]
        section = item.get("section", "")
        table_name = item.get("table_name", "")
        for idx, cells in enumerate(item.get("rows", []), start=1):
            rows.append(RawTableRow(
                schema_id=schema_id,
                section=section,
                table_name=table_name,
                row_index=idx,
                cells=cells,
            ))
    return rows


def run_pipeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    system_id = payload["system_id"]
    rows = parse_rows(payload)
    records = FieldExtractor().extract_rows(rows)
    entities, relationships = EntityBuilder(system_id=system_id).build(records)
    issues = ContradictionDetector().detect(records, entities, relationships)
    return {
        "system_id": system_id,
        "records": to_jsonable(records),
        "entities": to_jsonable(entities),
        "relationships": to_jsonable(relationships),
        "issues": to_jsonable(issues),
        "summary": {
            "record_count": len(records),
            "entity_count": len(entities),
            "relationship_count": len(relationships),
            "issue_count": len(issues),
        },
    }
