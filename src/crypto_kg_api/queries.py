from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from neo4j.graph import Node, Relationship

JsonDict = dict[str, Any]

ASSET_RELATIONSHIPS: dict[str, tuple[str, str]] = {
    "physical_environments": ("HAS_PHYSICAL_ENVIRONMENT", "PhysicalEnvironment"),
    "security_facilities": ("HAS_SECURITY_FACILITY", "PhysicalSecurityFacility"),
    "servers": ("HAS_SERVER", "Server"),
    "network_devices": ("HAS_NETWORK_DEVICE", "NetworkDevice"),
    "databases": ("USES_DATABASE", "DatabaseSystem"),
    "middlewares": ("HAS_MIDDLEWARE", "Middleware"),
    "business_applications": ("HAS_APPLICATION", "BusinessApplication"),
    "crypto_products": ("HAS_CRYPTO_PRODUCT", "CryptoProduct"),
    "important_data": ("HAS_IMPORTANT_DATA", "ImportantData"),
    "management_documents": ("HAS_DOCUMENT", "ManagementDocument"),
    "persons": ("HAS_PERSON", "Person"),
    "user_roles": ("HAS_USER_ROLE", "UserRole"),
    "security_areas": ("HAS_SECURITY_AREA", "SecurityArea"),
    "network_links": ("HAS_NETWORK_LINK", "NetworkLink"),
    "crypto_services": ("USES_CRYPTO_SERVICE", "CryptoService"),
}


def serialize_value(value: Any) -> Any:
    if isinstance(value, Node):
        return node_to_dict(value)
    if isinstance(value, Relationship):
        return relationship_to_dict(value)
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize_value(item) for key, item in value.items()}
    if hasattr(value, "iso_format"):
        return value.iso_format()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def node_properties(node: Node | None) -> JsonDict:
    if node is None:
        return {}
    properties = {str(key): serialize_value(value) for key, value in dict(node).items()}
    properties["labels"] = sorted(node.labels)
    return properties


def node_to_dict(node: Node | None) -> JsonDict:
    if node is None:
        return {}
    properties = node_properties(node)
    return {
        "id": properties.get("id") or properties.get("code") or properties.get("name"),
        "labels": sorted(node.labels),
        "properties": properties,
    }


def relationship_to_dict(relationship: Relationship | None) -> JsonDict:
    if relationship is None:
        return {}
    properties = {str(key): serialize_value(value) for key, value in dict(relationship).items()}
    return {
        "type": relationship.type,
        "start_id": _node_stable_id(relationship.start_node),
        "end_id": _node_stable_id(relationship.end_node),
        "properties": properties,
    }


def _node_stable_id(node: Node | None) -> str | None:
    if node is None:
        return None
    properties = dict(node)
    value = properties.get("id") or properties.get("code") or properties.get("name")
    return str(value) if value is not None else str(node.element_id)


def unique_nodes(nodes: Iterable[Node]) -> list[JsonDict]:
    seen: set[str] = set()
    output: list[JsonDict] = []
    for node in nodes:
        key = str(node.element_id)
        if key in seen:
            continue
        seen.add(key)
        output.append(node_to_dict(node))
    return output


def unique_relationships(relationships: Iterable[Relationship]) -> list[JsonDict]:
    seen: set[str] = set()
    output: list[JsonDict] = []
    for relationship in relationships:
        key = str(relationship.element_id)
        if key in seen:
            continue
        seen.add(key)
        output.append(relationship_to_dict(relationship))
    return output


class KnowledgeGraphQueries:
    def __init__(self, client: Any) -> None:
        self.client = client

    def system_overview(self, system_id: str) -> JsonDict:
        def work(tx: Any) -> JsonDict:
            record = tx.run(
                """
                MATCH (system:System {id: $system_id})
                OPTIONAL MATCH (report:Report)-[:EVALUATES]->(system)
                OPTIONAL MATCH (project:EvaluationProject)-[:HAS_TARGET_SYSTEM]->(system)
                RETURN system, report, project
                LIMIT 1
                """,
                system_id=system_id,
            ).single()
            if record is None:
                return {"found": False, "system": {}, "report": {}, "project": {}}
            return {
                "found": True,
                "system": node_properties(record["system"]),
                "report": node_properties(record["report"]),
                "project": node_properties(record["project"]),
            }

        return self.client.execute_read(work)

    def system_assets(self, system_id: str) -> JsonDict:
        overview = self.system_overview(system_id)
        if not overview["found"]:
            return {"found": False, "system": {}, "assets": empty_assets()}

        relationship_to_key = {relationship_type: key for key, (relationship_type, _) in ASSET_RELATIONSHIPS.items()}

        def work(tx: Any) -> JsonDict:
            assets: dict[str, list[JsonDict]] = empty_assets()
            seen_by_key: dict[str, set[str]] = {key: set() for key in assets}
            records = tx.run(
                """
                MATCH (:System {id: $system_id})-[relationship]->(node)
                WHERE type(relationship) IN $relationship_types
                RETURN type(relationship) AS relationship_type, node
                ORDER BY coalesce(node.name, node.id)
                """,
                system_id=system_id,
                relationship_types=list(relationship_to_key),
            )
            for record in records:
                key = relationship_to_key.get(record["relationship_type"])
                if key is None:
                    continue
                node = record["node"]
                node_key = str(node.element_id)
                if node_key in seen_by_key[key]:
                    continue
                seen_by_key[key].add(node_key)
                assets[key].append(node_properties(node))
            return {"found": True, "system": overview["system"], "assets": assets}

        return self.client.execute_read(work)

    def crypto_products(self, system_id: str) -> JsonDict:
        def work(tx: Any) -> JsonDict:
            records = list(
                tx.run(
                    """
                    MATCH (system:System {id: $system_id})
                    OPTIONAL MATCH (system)-[:HAS_CRYPTO_PRODUCT]->(product:CryptoProduct)
                    OPTIONAL MATCH (product)-[:HAS_PRODUCT_TYPE]->(product_type:ProductType)
                    WITH system, product, collect(DISTINCT product_type) AS product_types
                    RETURN system, product, product_types
                    ORDER BY coalesce(product.name, product.id)
                    """,
                    system_id=system_id,
                )
            )
            if not records:
                return {"found": False, "system": {}, "crypto_products": []}
            products = []
            for record in records:
                product = record["product"]
                if product is None:
                    continue
                item = node_properties(product)
                item["product_types"] = [node_properties(node) for node in record["product_types"]]
                products.append(item)
            return {"found": True, "system": node_properties(records[0]["system"]), "crypto_products": products}

        return self.client.execute_read(work)

    def important_data(self, system_id: str) -> JsonDict:
        def work(tx: Any) -> JsonDict:
            records = list(
                tx.run(
                    """
                    MATCH (system:System {id: $system_id})
                    OPTIONAL MATCH (system)-[:HAS_IMPORTANT_DATA]->(data:ImportantData)
                    OPTIONAL MATCH (data)-[:HAS_DATA_CATEGORY]->(category:DataCategory)
                    WITH system, data, collect(DISTINCT category) AS categories
                    RETURN system, data, categories
                    ORDER BY coalesce(data.name, data.id)
                    """,
                    system_id=system_id,
                )
            )
            if not records:
                return {"found": False, "system": {}, "important_data": []}
            data_items = []
            for record in records:
                data = record["data"]
                if data is None:
                    continue
                item = node_properties(data)
                item["data_categories"] = [node_properties(node) for node in record["categories"]]
                data_items.append(item)
            return {"found": True, "system": node_properties(records[0]["system"]), "important_data": data_items}

        return self.client.execute_read(work)

    def crypto_applications(self, system_id: str) -> JsonDict:
        def work(tx: Any) -> JsonDict:
            records = list(
                tx.run(
                    """
                    MATCH (system:System {id: $system_id})
                    OPTIONAL MATCH (system)-[:HAS_CRYPTO_APPLICATION]->(application:CryptoApplication)
                    OPTIONAL MATCH (application)-[:USES_PRODUCT]->(product:CryptoProduct)
                    OPTIONAL MATCH (application)-[:USES_ALGORITHM]->(algorithm:CryptoAlgorithm)
                    OPTIONAL MATCH (application)-[:HAS_USAGE]->(usage:CryptoUsage)
                    OPTIONAL MATCH (application)-[:SATISFIES]->(requirement:SecurityRequirement)
                    OPTIONAL MATCH (application)-[:PROTECTS_DATA]->(data:ImportantData)
                    WITH system, application,
                         collect(DISTINCT product) AS products,
                         collect(DISTINCT algorithm) AS algorithms,
                         collect(DISTINCT usage) AS usages,
                         collect(DISTINCT requirement) AS requirements,
                         collect(DISTINCT data) AS protected_data
                    RETURN system, application, products, algorithms, usages, requirements, protected_data
                    ORDER BY coalesce(application.name, application.id)
                    """,
                    system_id=system_id,
                )
            )
            if not records:
                return {"found": False, "system": {}, "crypto_applications": []}
            applications = []
            for record in records:
                application = record["application"]
                if application is None:
                    continue
                item = node_properties(application)
                item["products"] = [node_properties(node) for node in record["products"]]
                item["algorithms"] = [node_properties(node) for node in record["algorithms"]]
                item["usages"] = [node_properties(node) for node in record["usages"]]
                item["requirements"] = [node_properties(node) for node in record["requirements"]]
                item["protected_data"] = [node_properties(node) for node in record["protected_data"]]
                applications.append(item)
            return {"found": True, "system": node_properties(records[0]["system"]), "crypto_applications": applications}

        return self.client.execute_read(work)

    def data_protection(self, system_id: str) -> JsonDict:
        overview = self.system_overview(system_id)
        if not overview["found"]:
            return {"found": False, "system": {}, "data_protection": {"nodes": [], "relationships": []}}

        def work(tx: Any) -> JsonDict:
            records = list(
                tx.run(
                    """
                    MATCH (:System {id: $system_id})-[:HAS_CRYPTO_APPLICATION]->(application:CryptoApplication)
                    MATCH (application)-[protection]->(protected)
                    WHERE type(protection) IN ['PROTECTS_DATA', 'PROTECTS_ASSET']
                    OPTIONAL MATCH (application)-[context_relationship]->(context)
                    WHERE type(context_relationship) IN ['USES_PRODUCT', 'USES_ALGORITHM', 'HAS_USAGE', 'SATISFIES']
                    WITH application, protected, protection,
                         collect(DISTINCT context) AS context_nodes,
                         collect(DISTINCT context_relationship) AS context_relationships
                    RETURN [application, protected] + context_nodes AS nodes,
                           [protection] + context_relationships AS relationships
                    """,
                    system_id=system_id,
                )
            )
            nodes: list[Node] = []
            relationships: list[Relationship] = []
            for record in records:
                nodes.extend(record["nodes"])
                relationships.extend(record["relationships"])
            return {
                "found": True,
                "system": overview["system"],
                "data_protection": {
                    "nodes": unique_nodes(nodes),
                    "relationships": unique_relationships(relationships),
                },
            }

        return self.client.execute_read(work)

    def report_findings(self, report_id: str) -> JsonDict:
        def work(tx: Any) -> JsonDict:
            report = tx.run(
                "MATCH (report:Report {id: $report_id}) RETURN report LIMIT 1",
                report_id=report_id,
            ).single()
            if report is None:
                return {"found": False, "report": {}, "findings": [], "evidences": []}
            finding_records = list(
                tx.run(
                    """
                    MATCH (:Report {id: $report_id})-[:HAS_FINDING]->(finding:Finding)
                    OPTIONAL MATCH (item:ComplianceItem)-[:HAS_FINDING]->(finding)
                    OPTIONAL MATCH (finding)-[:SUPPORTED_BY]->(evidence:Evidence)
                    WITH finding, collect(DISTINCT item) AS compliance_items, collect(DISTINCT evidence) AS evidences
                    RETURN finding, compliance_items, evidences
                    ORDER BY coalesce(finding.severity, ''), coalesce(finding.name, finding.id)
                    """,
                    report_id=report_id,
                )
            )
            findings = []
            evidence_by_id: dict[str, JsonDict] = {}
            for record in finding_records:
                item = node_properties(record["finding"])
                item["compliance_items"] = [node_properties(node) for node in record["compliance_items"]]
                item["evidences"] = [node_properties(node) for node in record["evidences"]]
                findings.append(item)
                for evidence in item["evidences"]:
                    evidence_id = str(evidence.get("id") or evidence.get("name") or len(evidence_by_id))
                    evidence_by_id[evidence_id] = evidence
            evidence_records = tx.run(
                """
                MATCH (:Report {id: $report_id})-[:HAS_EVIDENCE]->(evidence:Evidence)
                RETURN evidence
                ORDER BY coalesce(evidence.name, evidence.id)
                """,
                report_id=report_id,
            )
            for record in evidence_records:
                evidence = node_properties(record["evidence"])
                evidence_id = str(evidence.get("id") or evidence.get("name") or len(evidence_by_id))
                evidence_by_id[evidence_id] = evidence
            return {
                "found": True,
                "report": node_properties(report["report"]),
                "findings": findings,
                "evidences": list(evidence_by_id.values()),
            }

        return self.client.execute_read(work)

    def generation_context(self, report_id: str) -> JsonDict:
        overview = self._overview_by_report(report_id)
        if not overview["found"]:
            return generation_context_empty(found=False)
        system_id = str(overview["system"].get("id") or "")
        assets = self.system_assets(system_id)["assets"] if system_id else empty_assets()
        crypto_applications = self.crypto_applications(system_id)["crypto_applications"] if system_id else []
        data_protection = self.data_protection(system_id)["data_protection"] if system_id else {"nodes": [], "relationships": []}
        findings = self.report_findings(report_id)
        quality_flags = collect_quality_flags(assets, crypto_applications, findings["findings"], findings["evidences"])
        return {
            "found": True,
            "report": overview["report"],
            "system": overview["system"],
            "assets": assets,
            "crypto_applications": crypto_applications,
            "data_protection": data_protection,
            "findings": findings["findings"],
            "evidences": findings["evidences"],
            "quality_flags": quality_flags,
        }

    def search_entities(self, query: str) -> JsonDict:
        def work(tx: Any) -> JsonDict:
            records = tx.run(
                """
                CALL db.index.fulltext.queryNodes('entity_text', $search_query)
                YIELD node, score
                RETURN node, score
                ORDER BY score DESC
                LIMIT 20
                """,
                search_query=plain_text_fulltext_query(query),
            )
            entities = []
            for record in records:
                item = node_to_dict(record["node"])
                item["score"] = record["score"]
                entities.append(item)
            return {"query": query, "entities": entities}

        return self.client.execute_read(work)

    def _overview_by_report(self, report_id: str) -> JsonDict:
        def work(tx: Any) -> JsonDict:
            record = tx.run(
                """
                MATCH (report:Report {id: $report_id})
                OPTIONAL MATCH (report)-[:EVALUATES]->(system:System)
                RETURN report, system
                ORDER BY coalesce(system.name, system.id)
                LIMIT 1
                """,
                report_id=report_id,
            ).single()
            if record is None:
                return {"found": False, "report": {}, "system": {}}
            return {
                "found": True,
                "report": node_properties(record["report"]),
                "system": node_properties(record["system"]),
            }

        return self.client.execute_read(work)


def empty_assets() -> dict[str, list[JsonDict]]:
    return {key: [] for key in ASSET_RELATIONSHIPS}


def generation_context_empty(*, found: bool) -> JsonDict:
    return {
        "found": found,
        "report": {},
        "system": {},
        "assets": empty_assets(),
        "crypto_applications": [],
        "data_protection": {"nodes": [], "relationships": []},
        "findings": [],
        "evidences": [],
        "quality_flags": [],
    }


def plain_text_fulltext_query(query: str) -> str:
    terms = [term for term in str(query).split() if term]
    if not terms:
        return '""'
    return " AND ".join(f'"{_escape_lucene_phrase(term)}"' for term in terms)


def _escape_lucene_phrase(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def collect_quality_flags(*groups: Any) -> list[JsonDict]:
    output: list[JsonDict] = []
    for group in groups:
        for item in walk_dicts(group):
            flags = item.get("quality_flags")
            if not flags:
                continue
            output.append(
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "quality_flags": flags,
                    "source_section": item.get("source_section"),
                }
            )
    return output


def walk_dicts(value: Any) -> Iterable[JsonDict]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)
