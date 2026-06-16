from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class SchemaSpec:
    schema_id: str
    entity_type: str
    required_fields: List[str]
    aliases: Dict[str, List[str]]
    list_fields: List[str]
    relation_fields: Dict[str, str]


SCHEMAS: Dict[str, SchemaSpec] = {
    "CryptoProductSchema": SchemaSpec(
        schema_id="CryptoProductSchema",
        entity_type="CryptoProduct",
        required_fields=["name"],
        aliases={
            "name": ["密码产品名称", "产品名称", "设备名称", "名称"],
            "product_type": ["产品类型", "设备类型", "类型"],
            "vendor": ["厂商", "生产厂商", "厂家"],
            "model": ["型号", "产品型号"],
            "version": ["版本", "软件版本", "固件版本"],
            "algorithms": ["密码算法", "算法", "使用算法", "支持算法"],
            "usage": ["密码用途", "用途", "使用场景"],
            "deployment_location": ["部署位置", "部署区域", "所在位置"],
            "ip_address": ["IP地址", "管理地址", "设备地址"],
        },
        list_fields=["algorithms", "usage"],
        relation_fields={"algorithms": "USES_ALGORITHM"},
    ),
    "ServerDeviceSchema": SchemaSpec(
        schema_id="ServerDeviceSchema",
        entity_type="ServerDevice",
        required_fields=["name"],
        aliases={
            "name": ["服务器名称", "设备名称", "主机名称", "名称"],
            "ip_address": ["IP地址", "服务器地址", "内网地址", "主机地址"],
            "os": ["操作系统", "系统版本", "OS"],
            "deployment_location": ["部署位置", "机房位置", "区域"],
            "business_system": ["所属系统", "承载系统", "业务系统"],
        },
        list_fields=[],
        relation_fields={},
    ),
    "DataAssetSchema": SchemaSpec(
        schema_id="DataAssetSchema",
        entity_type="DataAsset",
        required_fields=["name"],
        aliases={
            "name": ["数据名称", "数据资产名称", "重要数据", "名称"],
            "data_category": ["数据类别", "类别"],
            "sensitivity_level": ["敏感级别", "重要程度", "等级"],
            "stored_on": ["存储位置", "所在服务器", "存储服务器", "数据库服务器"],
            "database_name": ["数据库", "数据库名称"],
            "protection_requirement": ["保护需求", "安全需求", "密码保护需求"],
        },
        list_fields=["protection_requirement"],
        relation_fields={"stored_on": "STORED_ON"},
    ),
    "CryptoApplicationSchema": SchemaSpec(
        schema_id="CryptoApplicationSchema",
        entity_type="CryptoApplication",
        required_fields=["name"],
        aliases={
            "name": ["密码应用名称", "应用名称", "场景名称", "名称"],
            "usage": ["密码用途", "应用场景", "用途"],
            "product_name": ["密码产品", "使用产品", "产品名称"],
            "data_asset": ["保护对象", "重要数据", "保护数据"],
            "algorithms": ["密码算法", "使用算法", "算法"],
            "security_requirement": ["安全需求", "测评要求", "密码应用要求"],
        },
        list_fields=["algorithms", "security_requirement"],
        relation_fields={
            "product_name": "USES_PRODUCT",
            "data_asset": "PROTECTS_DATA",
            "algorithms": "USES_ALGORITHM",
            "security_requirement": "SATISFIES_REQUIREMENT",
        },
    ),
    "PersonSchema": SchemaSpec(
        schema_id="PersonSchema",
        entity_type="Person",
        required_fields=["name"],
        aliases={
            "name": ["姓名", "人员姓名", "负责人", "联系人", "名称"],
            "department": ["部门", "所属部门", "单位"],
            "role": ["角色", "岗位", "职责"],
            "phone": ["电话", "手机号", "联系方式"],
            "email": ["邮箱", "电子邮箱"],
            "responsible_for": ["负责对象", "负责系统", "负责资产"],
        },
        list_fields=["responsible_for"],
        relation_fields={"responsible_for": "RESPONSIBLE_FOR"},
    ),
}


def get_schema(schema_id: str) -> SchemaSpec:
    try:
        return SCHEMAS[schema_id]
    except KeyError as exc:
        supported = ", ".join(sorted(SCHEMAS))
        raise ValueError(f"Unsupported schema_id={schema_id!r}. Supported: {supported}") from exc
