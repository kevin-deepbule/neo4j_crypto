"""Small adapter functions intended for CryptoAgent tools/workflows."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from crypto_kg.graph import Neo4jConfig, Neo4jKnowledgeGraphStore, export_cypher
from crypto_kg.mapping import SchemaMapper
from crypto_kg.models import ExtractionResult, ParsedDocument, Section, Table
from crypto_kg.normalization import EntityNormalizer
from crypto_kg.pipeline import explicit_relations, extract_kg, result_to_dict


def build_crypto_agent_payload(
    file_path: str | Path,
    *,
    system_id: str,
    report_id: str | None = None,
    include_cypher: bool = True,
) -> dict[str, Any]:
    """Return parsed KG data that CryptoAgent can store, inspect or write to Neo4j."""

    result = extract_kg(file_path, system_id=system_id, report_id=report_id)
    payload = result_to_dict(result)
    payload["target_system_id"] = system_id
    payload["target_report_id"] = report_id
    if include_cypher:
        payload["cypher"] = export_cypher(result)
    return payload


async def ingest_document_to_kg(
    file_path: str | Path,
    *,
    system_id: str,
    report_id: str | None = None,
    system_name: str | None = None,
    neo4j_config: Neo4jConfig | None = None,
) -> dict[str, Any]:
    """Async adapter: parse a document and upsert extracted facts into Neo4j."""

    def _run() -> dict[str, Any]:
        result = extract_kg(file_path, system_id=system_id, report_id=report_id)
        store = Neo4jKnowledgeGraphStore(neo4j_config)
        try:
            counters = store.upsert_extraction(result, system_name=system_name)
        finally:
            store.close()
        return {
            "document": str(file_path),
            "system_id": system_id,
            "report_id": report_id,
            "counters": counters,
            "entities": [asdict(entity) for entity in result.entities],
            "relations": [asdict(relation) for relation in result.relations],
            "section_mappings": [asdict(mapping) for mapping in result.section_mappings],
        }

    return await asyncio.to_thread(_run)


async def ingest_structured_info_to_kg(
    structured_info: dict[str, Any],
    *,
    system_id: str,
    report_id: str | None = None,
    system_name: str | None = None,
    neo4j_config: Neo4jConfig | None = None,
) -> dict[str, Any]:
    """Async adapter: write existing CryptoAgent extracted chapter info to Neo4j."""

    def _run() -> dict[str, Any]:
        result = extraction_from_structured_info(
            structured_info,
            system_id=system_id,
            report_id=report_id,
        )
        store = Neo4jKnowledgeGraphStore(neo4j_config)
        try:
            counters = store.upsert_extraction(result, system_name=system_name)
        finally:
            store.close()
        return {
            "system_id": system_id,
            "report_id": report_id,
            "counters": counters,
            "entities": [asdict(entity) for entity in result.entities],
            "relations": [asdict(relation) for relation in result.relations],
            "section_mappings": [asdict(mapping) for mapping in result.section_mappings],
        }

    return await asyncio.to_thread(_run)


async def query_kg_context(
    *,
    system_id: str,
    keywords: list[str] | None = None,
    limit: int = 30,
    neo4j_config: Neo4jConfig | None = None,
) -> list[dict[str, Any]]:
    """Async read-only adapter for report generation and QA context retrieval."""

    def _run() -> list[dict[str, Any]]:
        store = Neo4jKnowledgeGraphStore(neo4j_config)
        try:
            return store.query_system_context(system_id, keywords=keywords, limit=limit)
        finally:
            store.close()

    return await asyncio.to_thread(_run)


def extraction_from_structured_info(
    structured_info: dict[str, Any],
    *,
    system_id: str,
    report_id: str | None = None,
) -> ExtractionResult:
    """Convert CryptoAgent's existing extracted chapter dict into KG entities."""

    document = ParsedDocument(path=Path("<crypto-agent-structured-info>"), metadata={"parser": "crypto_agent"})
    mapper = SchemaMapper()
    normalizer = EntityNormalizer(system_id=system_id, report_id=report_id)
    entities = {}
    relations = []
    mappings = []

    for section_no, payload in iter_structured_sections(structured_info):
        section = Section(section_no=section_no, title=section_title(section_no), level=section_no.count(".") + 1)
        records = payload_to_records(payload)
        table = Table(rows=[list(records[0].keys()), *[list(record.values()) for record in records]], section_no=section_no) if records else None
        mapping = mapper.map_section(section, table)
        if not mapping:
            continue
        mappings.append(mapping)
        document.sections.append(section)
        for record in records:
            entity = normalizer.normalize_record(mapping.schema, record, source_section=section_no)
            entities[entity.id] = entity
            relations.extend(explicit_relations(entity))

    return ExtractionResult(document=document, entities=list(entities.values()), relations=relations, section_mappings=mappings)


def iter_structured_sections(structured_info: dict[str, Any]):
    for key, value in structured_info.items():
        if not value:
            continue
        section_no = normalize_section_key(str(key))
        if section_no:
            yield section_no, value


def normalize_section_key(key: str) -> str | None:
    if key.startswith("section_"):
        return key.removeprefix("section_").replace("_", ".")
    if key.count(".") >= 1 and key[0].isdigit():
        return key
    return None


def payload_to_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, str):
        parsed = parse_json_value(payload)
        if parsed is not payload:
            return payload_to_records(parsed)
        return [{"name": payload, "description": payload}] if payload.strip() else []
    if isinstance(payload, list):
        records: list[dict[str, Any]] = []
        for item in payload:
            if isinstance(item, dict):
                records.append(item)
            elif isinstance(item, str):
                records.extend(payload_to_records(item))
        return records
    if isinstance(payload, dict):
        records: list[dict[str, Any]] = []
        for key, value in payload.items():
            parsed = parse_json_value(value) if isinstance(value, str) else value
            if key in CRYPTO_AGENT_FIELD_ALIASES:
                records.extend(payload_to_records(parsed))
            elif isinstance(parsed, list):
                records.extend(item for item in parsed if isinstance(item, dict))
            elif isinstance(parsed, dict):
                records.append(parsed)
            elif parsed:
                records.append({"name": str(parsed), "description": str(parsed)})
        return records
    if payload:
        return [{"name": str(payload), "description": str(payload)}]
    return []


def parse_json_value(value: str) -> Any:
    text = value.strip()
    if not text or text[0] not in "[{":
        return value
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return value


CRYPTO_AGENT_FIELD_ALIASES = {
    "dSystemAssetPasswordProducts": "records",
    "dSystemAssetServers": "records",
    "dSystemAssetNetworkSecurityDevices": "records",
    "dSystemAssetDatabaseManagementSystem": "records",
    "dSystemAssetCriticalBusinessApplications": "records",
    "dSystemAssetSystemImportantData": "records",
    "dSystemAssetSecurityManagementDocuments": "records",
    "dSystemAssetPersonnelManagement": "records",
}


def section_title(section_no: str) -> str:
    titles = {
        "2.4.1": "物理环境",
        "2.4.2": "物理安防设施",
        "2.4.3": "密码产品",
        "2.4.4": "服务器和存储设备",
        "2.4.5": "网络及安全设备",
        "2.4.6": "数据库管理系统",
        "2.4.7": "关键业务应用",
        "2.4.8": "重要数据",
        "2.4.9": "安全管理文档",
        "2.4.10": "人员管理",
    }
    return titles.get(section_no, "")
