# Report 智能体字段到 Neo4j 图谱映射

本文档定义 `CryptoAgent_QingDao` report 智能体结构化抽取结果与本仓库 Neo4j 本体之间的对接关系。本阶段 `neo4j_crypto` 仅提供图谱存储和 HTTP 查询能力，不直接修改 report 智能体。

## 对接原则

1. report 智能体输出是图谱导入的上游结构化材料，不在本仓库重新解析 Word/PDF。
2. 系统内实例节点必须带 `Entity` 标签，`id` 推荐为 `{system_id}:{entity_type}:{normalized_name}`。
3. 字典节点跨报告复用：算法按 `name`，产品类型、数据类别、测评指标和威胁按 `code`。
4. 只根据明确字段生成确定性关系，不根据名称、标签或描述文本猜测语义关系。
5. 保留 `source_section`、`source_text`、`confidence`、`quality_flags`，不得用后处理清洗覆盖原始占位值。

## 核心字段映射

| report 智能体字段 | Neo4j 标签 | 属性映射 | 自动关系 |
|---|---|---|---|
| `bSystemName` | `System` | `name` | `Report -[:EVALUATES]-> System` |
| `bServiceScope` | `System` | `service_scope` | 无 |
| `bServiceField` | `System` | `business_domain` | 无 |
| `bNetType`、`bNetCoverage` | `System` | `network_architecture` 或补充说明 | 无 |
| `dSystemAssetPhysicalEnvironment` | `Entity:PhysicalEnvironment` | `name`、`location`、`importance_level`、`remark` | `System -[:HAS_PHYSICAL_ENVIRONMENT]-> PhysicalEnvironment` |
| `dSystemAssetSecurityFacilities` | `Entity:PhysicalSecurityFacility` | `name`、`vendor`、`model`、`importance_level`、`remark` | `System -[:HAS_SECURITY_FACILITY]-> PhysicalSecurityFacility` |
| `dSystemAssetPasswordProducts` | `Entity:CryptoProduct` | `name`、`vendor`、`model`、`certificate_no`、`quantity`、`purpose`、`remark` | `System -[:HAS_CRYPTO_PRODUCT]-> CryptoProduct` |
| `dSystemAssetServers` | `Entity:Server` | `name`、`vendor`、`model`、`os_version`、`is_virtual`、`purpose`、`quantity`、`importance_level` | `System -[:HAS_SERVER]-> Server` |
| `dSystemAssetNetworkSecurityDevices` | `Entity:NetworkDevice` | `name`、`vendor`、`model`、`purpose`、`quantity`、`importance_level` | `System -[:HAS_NETWORK_DEVICE]-> NetworkDevice` |
| `dSystemAssetDatabaseManagementSystem` | `Entity:DatabaseSystem` | `name`、`version`、`deploy_location`、`main_function`、`importance_level` | `System -[:USES_DATABASE]-> DatabaseSystem` |
| `dSystemAssetCriticalBusinessApplications` | `Entity:BusinessApplication` | `name`、`version`、`deploy_location`、`main_function` | `System -[:HAS_APPLICATION]-> BusinessApplication` |
| `dSystemAssetSystemImportantData` | `Entity:ImportantData` | `name`、`description`、`storage_location`、`security_needs`、`importance_level` | `System -[:HAS_IMPORTANT_DATA]-> ImportantData` |
| `dSystemAssetSecurityManagementDocuments` | `Entity:ManagementDocument` | `name`、`main_content`、`remark` | `System -[:HAS_DOCUMENT]-> ManagementDocument` |
| `dSystemAssetPersonnelManagement` | `Entity:Person` | `name`、`role`、`responsibility`、`contact` | `System -[:HAS_PERSON]-> Person` |
| `eSystemAssetPasswordServiceProvider` | `Entity:CryptoService` | `name`、`provider`、`service_type` | `System -[:USES_CRYPTO_SERVICE]-> CryptoService` |
| `bAlgGroup`、`bAlgAsym`、`bAlgHash`、`bAlgSeries` | `CryptoAlgorithm` | `name`、`algorithm_type` | 仅在明确应用主体时创建 `USES_ALGORITHM` |

## 字典字段映射

| 来源字段 | 字典节点 | 唯一键 | 说明 |
|---|---|---|---|
| 密码产品类型 | `ProductType` | `code` | 写入 `CryptoProduct.product_type_code` 后可创建 `HAS_PRODUCT_TYPE` |
| 重要数据类别 | `DataCategory` | `code` | 写入 `ImportantData.data_category_code` 后可创建 `HAS_DATA_CATEGORY` |
| 测评指标编码 | `EvaluationCriterion` | `code` | 写入 `ComplianceItem.criterion_code` 后可创建 `BASED_ON` |
| 算法名称 | `CryptoAlgorithm` | `name` | 只复用明确算法名，不从产品名称猜测 |

## 自动建边边界

可根据明确 ID 或编码自动创建：

```text
project_id          -> HAS_REPORT / HAS_TARGET_SYSTEM
report_id           -> EVALUATES / HAS_COMPLIANCE_ITEM / HAS_FINDING / HAS_EVIDENCE
system_id           -> 系统与资产、角色、区域、链路、密码服务、密码应用的归属关系
product_type_code   -> HAS_PRODUCT_TYPE
data_category_code  -> HAS_DATA_CATEGORY
criterion_code      -> BASED_ON
compliance_item_id  -> HAS_FINDING / SUPPORTED_BY
finding_id          -> SUPPORTED_BY
```

不得自动猜测：

```text
USES_PRODUCT / USES_ALGORITHM / HAS_USAGE / SATISFIES
PROTECTS_DATA / PROTECTS_ASSET / PROVIDES_SERVICE
HAS_THREAT / AFFECTS_ASSET / AFFECTS_DATA / MITIGATED_BY / RELATED_TO_REQUIREMENT
DEPLOYED_IN / DEPLOYED_ON / STORED_IN / STORED_ON / BELONGS_TO
REGULATES / RESPONSIBLE_FOR / MANAGES / OPERATES
```

这些关系必须来自 report 智能体的明确结构化字段、报告原文证据或人工确认。
