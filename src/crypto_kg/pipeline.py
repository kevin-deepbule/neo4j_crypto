"""High-level extraction pipeline."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from crypto_kg.graph import export_cypher
from crypto_kg.mapping import SchemaMapper
from crypto_kg.models import Entity, ExtractionResult, Relation
from crypto_kg.normalization import EntityNormalizer
from crypto_kg.parsing import parse_document


def extract_kg(
    path: str | Path,
    *,
    system_id: str = "unknown-system",
    report_id: str | None = None,
) -> ExtractionResult:
    """Parse a report and extract ontology-aligned entities."""

    document = parse_document(path)
    mapper = SchemaMapper()
    normalizer = EntityNormalizer(system_id=system_id, report_id=report_id)

    entities_by_id: dict[str, Entity] = {}
    relations: list[Relation] = []
    mappings = []

    for section in document.sections:
        section_tables = section.tables or []
        if not section_tables:
            mapping = mapper.map_section(section)
            if mapping and section.content.strip():
                entity = normalizer.normalize_record(
                    mapping.schema,
                    {"name": section.title, "description": section.content},
                    source_section=section.section_no,
                )
                entities_by_id[entity.id] = merge_entities(entities_by_id.get(entity.id), entity)
                mappings.append(mapping)
            continue

        for table in section_tables:
            mapping = mapper.map_section(section, table)
            if not mapping:
                continue
            mappings.append(mapping)
            for record in table.to_records():
                entity = normalizer.normalize_record(mapping.schema, record, source_section=section.section_no)
                entities_by_id[entity.id] = merge_entities(entities_by_id.get(entity.id), entity)
                relations.extend(explicit_relations(entity))

    return ExtractionResult(
        document=document,
        entities=list(entities_by_id.values()),
        relations=relations,
        section_mappings=mappings,
    )


def extract_to_dict(path: str | Path, *, system_id: str = "unknown-system", report_id: str | None = None) -> dict[str, Any]:
    """Return a JSON-serializable extraction result for CryptoAgent tools."""

    result = extract_kg(path, system_id=system_id, report_id=report_id)
    return result_to_dict(result)


def result_to_dict(result: ExtractionResult) -> dict[str, Any]:
    """Return a JSON-serializable representation of an extraction result."""

    return {
        "document": {
            "path": str(result.document.path),
            "metadata": result.document.metadata,
            "sections": [asdict(section) for section in result.document.sections],
        },
        "entities": [asdict(entity) for entity in result.entities],
        "relations": [asdict(relation) for relation in result.relations],
        "section_mappings": [asdict(mapping) for mapping in result.section_mappings],
    }


def extract_to_cypher(path: str | Path, *, system_id: str = "unknown-system", report_id: str | None = None) -> str:
    return export_cypher(extract_kg(path, system_id=system_id, report_id=report_id))


def merge_entities(existing: Entity | None, incoming: Entity) -> Entity:
    if existing is None:
        return incoming
    labels = list(dict.fromkeys([*existing.labels, *incoming.labels]))
    properties = {**existing.properties, **incoming.properties}
    source_text = "\n".join(
        part for part in [existing.source_text, incoming.source_text] if part
    )
    return Entity(
        id=existing.id,
        labels=labels,
        name=existing.name,
        properties=properties,
        source_section=existing.source_section or incoming.source_section,
        source_text=source_text,
        confidence=max(existing.confidence, incoming.confidence),
    )


def explicit_relations(entity: Entity) -> list[Relation]:
    relations: list[Relation] = []
    algorithm_text = entity.properties.get("algorithm")
    if algorithm_text:
        for algorithm in split_values(str(algorithm_text)):
            if algorithm.upper() in {"SM2", "SM3", "SM4", "MAC"} or "TLS" in algorithm.upper() or "SSL" in algorithm.upper():
                relations.append(
                    Relation(
                        start_id=entity.id,
                        end_id=algorithm.upper() if algorithm.upper().startswith("SM") else algorithm,
                        type="USES_ALGORITHM",
                        properties={"confidence": entity.confidence, "source_section": entity.source_section},
                    )
                )
    return relations


def split_values(text: str) -> list[str]:
    return [item.strip() for item in text.replace("、", ",").replace("，", ",").replace("/", ",").split(",") if item.strip()]
