from pathlib import Path

from crypto_kg.graph import export_cypher
from crypto_kg.pipeline import extract_kg


FIXTURE = Path(__file__).parent / "fixtures" / "sample_report.txt"


def test_extracts_243_crypto_product_table() -> None:
    result = extract_kg(FIXTURE, system_id="sys_001", report_id="report_001")

    schemas = {mapping.section_no: mapping.schema for mapping in result.section_mappings}
    assert schemas["2.4.3"] == "CryptoProduct"

    gateway = next(entity for entity in result.entities if entity.name == "加密网关")
    assert "CryptoProduct" in gateway.labels
    assert "NetworkDevice" in gateway.labels
    assert gateway.properties["product_type_code"] == "CRYPTO_GATEWAY"
    assert gateway.properties["system_id"] == "sys_001"

    crypto_server = next(entity for entity in result.entities if entity.name == "加密服务器")
    assert "CryptoProduct" in crypto_server.labels
    assert "Server" in crypto_server.labels


def test_exports_dictionary_relationships() -> None:
    result = extract_kg(FIXTURE, system_id="sys_001")
    cypher = export_cypher(result)

    assert "MATCH (t:ProductType {code: \"CRYPTO_GATEWAY\"})" in cypher
    assert "MERGE (n)-[:HAS_PRODUCT_TYPE]->(t);" in cypher
    assert "MATCH (b:CryptoAlgorithm {name: \"SM2\"})" in cypher
