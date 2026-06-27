"""Normalize entity names, aliases and multi-label identities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from crypto_kg.models import Entity


PRODUCT_TYPE_ALIASES: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "CRYPTO_GATEWAY": ("密码网关", "加密网关|密码网关|安全网关|VPN|SSL网关", ("CryptoProduct", "NetworkDevice")),
    "SIGNATURE_SERVER": ("签名验签服务器", "签名验签|签验|签名服务器|验签服务器", ("CryptoProduct", "CryptoService")),
    "TIMESTAMP_SERVER": ("时间戳服务器", "时间戳", ("CryptoProduct", "CryptoService")),
    "CRYPTO_MACHINE": ("密码机", "密码机|加密机|加密服务器|服务器密码机|金融数据密码机", ("CryptoProduct", "Server")),
    "KEY_MANAGEMENT_SYSTEM": ("密钥管理系统", "密钥管理|KMS", ("CryptoProduct", "CryptoService")),
    "CA_SYSTEM": ("CA 系统", "CA|证书认证|认证系统", ("CryptoService",)),
    "UKEY": ("UKey", "UKey|USBKey|智能密码钥匙|动态令牌", ("CryptoProduct",)),
}

GENERIC_PREFIXES = ("商用", "通用", "国产", "国密", "专用")


@dataclass(slots=True)
class EntityNormalizer:
    """Normalize names and merge multi-identity entities within one system."""

    system_id: str = "unknown-system"
    report_id: str | None = None

    def normalize_record(self, schema: str, record: dict[str, Any], source_section: str | None = None) -> Entity:
        canonical_record = canonicalize_record_keys(record)
        raw_name = pick_name(canonical_record, schema)
        name = normalize_name(raw_name)
        labels = ["Entity", schema]
        properties = dict(canonical_record)
        properties.pop("name", None)

        if schema == "CryptoProduct":
            product_type_code, product_type, extra_labels = infer_product_type(name, properties)
            labels.extend(extra_labels)
            properties["product_type_code"] = product_type_code
            properties["product_type"] = product_type
            properties["asset_type"] = "密码产品"
            if product_type_code == "CRYPTO_GATEWAY":
                properties.setdefault("device_type", "加密网关")
        elif schema == "NetworkDevice" and looks_like_crypto_gateway(name):
            labels.append("CryptoProduct")
            properties["product_type_code"] = "CRYPTO_GATEWAY"
            properties["product_type"] = "密码网关"
            properties.setdefault("asset_type", "密码产品")
        elif schema == "ImportantData":
            code, category = infer_data_category(name, properties)
            if code:
                properties["data_category_code"] = code
                properties["data_type"] = category

        properties["system_id"] = self.system_id
        if self.report_id:
            properties["report_id"] = self.report_id
        entity_id = build_entity_id(self.system_id, primary_label(labels), name)
        return Entity(
            id=entity_id,
            labels=dedupe(labels),
            name=name,
            properties=properties,
            source_section=source_section,
            source_text=record_to_source_text(record),
            confidence=0.86,
        )


def normalize_name(value: Any) -> str:
    text = " ".join(str(value or "").replace("\u3000", " ").split())
    text = text.strip(" ,，;；:：。")
    for prefix in GENERIC_PREFIXES:
        if text.startswith(prefix) and len(text) > len(prefix) + 2:
            text = text[len(prefix) :]
    return text or "未命名实体"


def canonicalize_record_keys(record: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in record.items():
        normalized_key = re.sub(r"\s+", "", str(key))
        target = FIELD_ALIASES.get(normalized_key, normalized_key)
        if value not in (None, ""):
            result[target] = value
    return result


FIELD_ALIASES = {
    "名称": "name",
    "产品名称": "name",
    "密码产品名称": "name",
    "设备名称": "name",
    "服务器名称": "name",
    "系统名称": "name",
    "数据名称": "name",
    "厂商": "vendor",
    "生产厂商": "vendor",
    "厂家": "vendor",
    "制造商": "vendor",
    "manufacturer": "vendor",
    "certificateNumber": "certificate_no",
    "securityRequirements": "security_needs",
    "storageLocation": "storage_location",
    "osVersion": "os_version",
    "isVirtual": "is_virtual",
    "isEvaluation": "is_evaluation",
    "function": "main_function",
    "location": "deploy_location",
    "content": "main_content",
    "importance": "importance_level",
    "型号": "model",
    "产品型号": "model",
    "证书编号": "certificate_no",
    "商密产品认证证书编号": "certificate_no",
    "认证证书编号": "certificate_no",
    "数量": "quantity",
    "用途": "purpose",
    "备注": "remark",
    "算法": "algorithm",
    "使用算法": "algorithm",
    "使用的密码算法": "algorithm",
    "版本": "version",
    "操作系统": "os_version",
    "部署位置": "deploy_location",
    "主要功能": "main_function",
    "重要程度": "importance_level",
}


def pick_name(record: dict[str, Any], schema: str) -> str:
    for key in ("name", "model", "device_type", "server_type", "main_function", "purpose"):
        value = record.get(key)
        if value:
            return str(value)
    return schema


def infer_product_type(name: str, properties: dict[str, Any]) -> tuple[str, str, tuple[str, ...]]:
    haystack = " ".join(str(value) for value in [name, *properties.values()] if value)
    for code, (canonical_name, pattern, labels) in PRODUCT_TYPE_ALIASES.items():
        if re.search(pattern, haystack, flags=re.I):
            return code, canonical_name, labels
    return "CRYPTO_MACHINE", "密码机", ("CryptoProduct",)


def looks_like_crypto_gateway(name: str) -> bool:
    return bool(re.search(r"加密网关|密码网关|VPN|SSL网关", name, flags=re.I))


def infer_data_category(name: str, properties: dict[str, Any]) -> tuple[str | None, str | None]:
    haystack = " ".join(str(value) for value in [name, *properties.values()] if value)
    if re.search("身份|认证|鉴别|口令|账号", haystack):
        return "AUTHENTICATION_DATA", "身份鉴别数据"
    if re.search("日志|审计", haystack):
        return "LOG_DATA", "日志数据"
    if re.search("个人|敏感", haystack):
        return "PERSONAL_SENSITIVE_DATA", "个人敏感信息"
    if re.search("密钥|证书", haystack):
        return "KEY_DATA", "密钥数据"
    if re.search("配置|策略", haystack):
        return "CONFIGURATION_DATA", "配置数据"
    if re.search("业务|交易|订单", haystack):
        return "BUSINESS_DATA", "业务数据"
    return None, None


def build_entity_id(system_id: str, schema: str, name: str) -> str:
    slug = re.sub(r"[\s:/\\]+", "_", name)
    return f"{system_id}:{schema}:{slug}"


def primary_label(labels: list[str]) -> str:
    for label in labels:
        if label != "Entity":
            return label
    return "Entity"


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def record_to_source_text(record: dict[str, Any]) -> str:
    return "; ".join(f"{key}={value}" for key, value in record.items() if value not in (None, ""))
