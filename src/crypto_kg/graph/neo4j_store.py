"""Neo4j write/query API for extracted crypto knowledge graphs."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

from crypto_kg.graph.cypher import relation_types_for_entity
from crypto_kg.models import Entity, ExtractionResult, Relation

LABEL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class Neo4jConfig:
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "crypto_neo4j_password"
    database: str | None = None

    @classmethod
    def from_env(cls) -> "Neo4jConfig":
        return cls(
            uri=os.getenv("NEO4J_URI") or os.getenv("NEO4J_BOLT_URI") or "bolt://localhost:7687",
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "crypto_neo4j_password"),
            database=os.getenv("NEO4J_DATABASE") or None,
        )


class Neo4jKnowledgeGraphStore:
    """Small repository layer for inserting and querying ontology data."""

    def __init__(self, config: Neo4jConfig | None = None) -> None:
        try:
            from neo4j import GraphDatabase
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("neo4j Python driver is required. Install crypto-kg[neo4j].") from exc

        self.config = config or Neo4jConfig.from_env()
        self.driver = GraphDatabase.driver(self.config.uri, auth=(self.config.username, self.config.password))

    def close(self) -> None:
        self.driver.close()

    def upsert_extraction(
        self,
        result: ExtractionResult,
        *,
        ensure_system: bool = True,
        system_name: str | None = None,
    ) -> dict[str, int]:
        """Write extracted entities and explicit relationships to Neo4j."""

        counters = {"entities": 0, "relations": 0}
        with self.driver.session(database=self.config.database) as session:
            for entity in result.entities:
                if ensure_system and entity.properties.get("system_id"):
                    session.execute_write(
                        self._merge_system,
                        entity.properties["system_id"],
                        system_name or entity.properties.get("system_name") or entity.properties["system_id"],
                    )
                session.execute_write(self._merge_entity, entity)
                counters["entities"] += 1
                for relation_type in relation_types_for_entity(entity):
                    if entity.properties.get("system_id"):
                        session.execute_write(
                            self._merge_system_relation,
                            entity.properties["system_id"],
                            entity.id,
                            relation_type,
                            entity.source_section,
                            entity.confidence,
                        )
                        counters["relations"] += 1
                if entity.properties.get("product_type_code") and "CryptoProduct" in entity.labels:
                    session.execute_write(self._merge_product_type_relation, entity.id, entity.properties["product_type_code"])
                    counters["relations"] += 1
                if entity.properties.get("data_category_code") and "ImportantData" in entity.labels:
                    session.execute_write(self._merge_data_category_relation, entity.id, entity.properties["data_category_code"])
                    counters["relations"] += 1

            for relation in dedupe_relations(result.relations):
                session.execute_write(self._merge_relation, relation)
                counters["relations"] += 1
        return counters

    def query(self, cypher: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with self.driver.session(database=self.config.database) as session:
            records = session.run(cypher, parameters or {})
            return [record.data() for record in records]

    def query_system_context(self, system_id: str, *, keywords: list[str] | None = None, limit: int = 30) -> list[dict[str, Any]]:
        """Read compact graph facts for downstream report/QA context."""

        cypher = """
        MATCH (s:System {id: $system_id})-[r]->(n:Entity)
        WHERE $keywords = [] OR any(k IN $keywords WHERE n.name CONTAINS k OR coalesce(n.source_text, '') CONTAINS k)
        OPTIONAL MATCH (n)-[dr]->(d)
        WHERE type(dr) IN ['HAS_PRODUCT_TYPE', 'HAS_DATA_CATEGORY', 'USES_ALGORITHM', 'HAS_USAGE', 'SATISFIES']
        RETURN labels(n) AS labels,
               n.id AS id,
               n.name AS name,
               type(r) AS system_relation,
               properties(n) AS properties,
               collect({type: type(dr), target_labels: labels(d), target: properties(d)}) AS dictionary_relations
        LIMIT $limit
        """
        return self.query(cypher, {"system_id": system_id, "keywords": keywords or [], "limit": limit})

    @staticmethod
    def _merge_system(tx, system_id: str, system_name: str) -> None:
        tx.run(
            "MERGE (s:System {id: $id}) SET s.name = coalesce(s.name, $name)",
            id=system_id,
            name=system_name,
        )

    @staticmethod
    def _merge_entity(tx, entity: Entity) -> None:
        labels = safe_labels(entity.labels)
        tx.run(
            f"MERGE (n:{labels} {{id: $id}}) SET n += $props",
            id=entity.id,
            props=entity.all_properties(),
        )

    @staticmethod
    def _merge_system_relation(
        tx,
        system_id: str,
        entity_id: str,
        relation_type: str,
        source_section: str | None,
        confidence: float,
    ) -> None:
        rel = safe_token(relation_type)
        tx.run(
            f"""
            MATCH (s:System {{id: $system_id}})
            MATCH (n:Entity {{id: $entity_id}})
            MERGE (s)-[r:{rel}]->(n)
            SET r.source_section = coalesce(r.source_section, $source_section),
                r.confidence = coalesce(r.confidence, $confidence)
            """,
            system_id=system_id,
            entity_id=entity_id,
            source_section=source_section,
            confidence=confidence,
        )

    @staticmethod
    def _merge_product_type_relation(tx, entity_id: str, code: str) -> None:
        tx.run(
            """
            MATCH (n:Entity {id: $entity_id})
            MATCH (t:ProductType {code: $code})
            MERGE (n)-[:HAS_PRODUCT_TYPE]->(t)
            """,
            entity_id=entity_id,
            code=code,
        )

    @staticmethod
    def _merge_data_category_relation(tx, entity_id: str, code: str) -> None:
        tx.run(
            """
            MATCH (n:Entity {id: $entity_id})
            MATCH (t:DataCategory {code: $code})
            MERGE (n)-[:HAS_DATA_CATEGORY]->(t)
            """,
            entity_id=entity_id,
            code=code,
        )

    @staticmethod
    def _merge_relation(tx, relation: Relation) -> None:
        rel = safe_token(relation.type)
        if relation.type == "USES_ALGORITHM":
            end_match = "MATCH (b:CryptoAlgorithm {name: $end_id})"
        elif relation.type == "HAS_USAGE":
            end_match = "MATCH (b:CryptoUsage {name: $end_id})"
        elif relation.type == "SATISFIES":
            end_match = "MATCH (b:SecurityRequirement {name: $end_id})"
        else:
            end_match = "MATCH (b {id: $end_id})"
        tx.run(
            f"""
            MATCH (a:Entity {{id: $start_id}})
            {end_match}
            MERGE (a)-[r:{rel}]->(b)
            SET r += $props
            """,
            start_id=relation.start_id,
            end_id=relation.end_id,
            props=relation.properties,
        )


def safe_labels(labels: list[str]) -> str:
    return ":".join(safe_token(label) for label in labels)


def safe_token(value: str) -> str:
    if not LABEL_RE.fullmatch(value):
        raise ValueError(f"Unsafe Neo4j token: {value}")
    return value


def dedupe_relations(relations: list[Relation]) -> list[Relation]:
    seen: set[tuple[str, str, str]] = set()
    result: list[Relation] = []
    for relation in relations:
        key = (relation.start_id, relation.type, relation.end_id)
        if key in seen:
            continue
        seen.add(key)
        result.append(relation)
    return result
