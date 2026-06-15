"""Map report section headings and table headers to ontology schemas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from crypto_kg.models import SchemaMapping, Section, Table


@dataclass(frozen=True, slots=True)
class SectionRule:
    schema: str
    relation: str
    section_prefixes: tuple[str, ...]
    title_keywords: tuple[str, ...]
    header_keywords: tuple[str, ...] = ()
    multi_labels: tuple[str, ...] = ()


DEFAULT_SECTION_RULES: tuple[SectionRule, ...] = (
    SectionRule("PhysicalEnvironment", "HAS_PHYSICAL_ENVIRONMENT", ("2.4.1",), ("物理", "环境", "机房")),
    SectionRule("PhysicalSecurityFacility", "HAS_SECURITY_FACILITY", ("2.4.2",), ("物理安防", "门禁", "监控")),
    SectionRule(
        "CryptoProduct",
        "HAS_CRYPTO_PRODUCT",
        ("2.4.3",),
        ("密码产品", "商用密码产品", "加密网关", "密码设备"),
        ("证书", "算法", "用途", "厂商", "产品"),
        ("CryptoProduct",),
    ),
    SectionRule("Server", "HAS_SERVER", ("2.4.4",), ("服务器", "存储设备", "主机"), ("操作系统", "服务器")),
    SectionRule("NetworkDevice", "HAS_NETWORK_DEVICE", ("2.4.5",), ("网络设备", "安全设备"), ("设备类型", "型号")),
    SectionRule("DatabaseSystem", "USES_DATABASE", ("2.4.6",), ("数据库",), ("数据库", "版本")),
    SectionRule("BusinessApplication", "HAS_APPLICATION", ("2.4.7",), ("业务应用", "关键业务应用", "应用系统"), ("应用", "功能")),
    SectionRule("Middleware", "HAS_MIDDLEWARE", ("2.4.7",), ("中间件",), ("中间件", "版本")),
    SectionRule("ImportantData", "HAS_IMPORTANT_DATA", ("2.4.8",), ("重要数据", "数据资产"), ("数据", "安全需求")),
    SectionRule("ManagementDocument", "HAS_DOCUMENT", ("2.4.9", "7.", "8."), ("管理制度", "管理文档", "应急预案")),
    SectionRule("Person", "HAS_PERSON", ("2.4.10", "7.", "8."), ("人员", "岗位", "职责"), ("姓名", "角色", "职责")),
    SectionRule("CryptoApplication", "HAS_CRYPTO_APPLICATION", ("3.", "4.", "5.", "6."), ("密码应用", "应用措施", "保护措施")),
    SectionRule("ComplianceItem", "HAS_COMPLIANCE_ITEM", ("3.", "4.", "5.", "6.", "7.", "8."), ("测评", "符合性", "适用性")),
)


class SchemaMapper:
    """Rule-based schema mapper with explicit section precedence."""

    def __init__(self, rules: Iterable[SectionRule] = DEFAULT_SECTION_RULES) -> None:
        self.rules = tuple(rules)

    def map_section(self, section: Section, table: Table | None = None) -> SchemaMapping | None:
        return map_section_to_schema(section, table, self.rules)


def map_section_to_schema(
    section: Section,
    table: Table | None = None,
    rules: Iterable[SectionRule] = DEFAULT_SECTION_RULES,
) -> SchemaMapping | None:
    heading = f"{section.section_no} {section.title}".lower()
    headers = " ".join(table.headers if table else []).lower()
    candidates: list[tuple[float, SectionRule, str]] = []

    for rule in rules:
        score = 0.0
        reasons: list[str] = []
        if any(section.section_no.startswith(prefix) for prefix in rule.section_prefixes):
            score += 0.70
            reasons.append(f"section={section.section_no}")
        if any(keyword.lower() in heading for keyword in rule.title_keywords):
            score += 0.25
            reasons.append("title")
        if headers and any(keyword.lower() in headers for keyword in rule.header_keywords):
            score += 0.15
            reasons.append("headers")
        if score:
            candidates.append((score, rule, "+".join(reasons)))

    if not candidates:
        return None
    score, rule, reason = sorted(candidates, key=lambda item: item[0], reverse=True)[0]
    return SchemaMapping(
        schema=rule.schema,
        relation=rule.relation,
        section_no=section.section_no,
        section_title=section.title,
        confidence=min(score, 1.0),
        reason=reason,
        multi_labels=rule.multi_labels,
    )
