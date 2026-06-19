# 关系类型设计

关系命名使用大写下划线风格。关系建议保留来源字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `source_section` | string | 来源章节 |
| `source_text` | string | 来源原文 |
| `confidence` | float | 抽取置信度 |
| `remark` | string | 备注 |

关系规则定义允许的业务语义，但 Neo4j 不会自动按规则创建关系。`ontology/link_instances.cypher` 仅根据明确的 ID 引用创建可确定的实例关系。

## 测评项目关系

| 关系 | 起点 | 终点 | 含义 |
|---|---|---|---|
| `HAS_REPORT` | `EvaluationProject` | `Report` | 测评项目产生或包含报告 |
| `HAS_TARGET_SYSTEM` | `EvaluationProject` | `System` | 测评项目覆盖被测系统 |

## 报告与系统关系

| 关系 | 起点 | 终点 | 含义 |
|---|---|---|---|
| `EVALUATES` | `Report` | `System` | 报告测评某被测系统 |

## 可选报告结构与溯源关系

这些关系用于原文定位和抽取审核，不属于核心业务查询路径。

| 关系 | 起点 | 终点 | 含义 |
|---|---|---|---|
| `HAS_SECTION` | `Report` | `ReportSection` | 报告包含章节 |
| `HAS_FIELD` | `ReportSection` | `ReportField` | 章节包含字段 |
| `EXTRACTED_FROM` | 领域实例节点/`Evidence` | `ReportSection`/`ReportField` | 实体或证据抽取自某章节或字段 |

简单溯源优先使用节点或关系上的 `source_section`、`source_text` 属性。只有需要完整报告结构、精确字段定位或抽取审核时，才创建上述节点和关系。不要让核心领域关系依赖 `ReportSection` 或 `ReportField` 中转。

## 系统与资产关系

| 关系 | 起点 | 终点 | 含义 |
|---|---|---|---|
| `HAS_PHYSICAL_ENVIRONMENT` | `System` | `PhysicalEnvironment` | 系统具有物理环境 |
| `HAS_SECURITY_FACILITY` | `System` | `PhysicalSecurityFacility` | 系统具有物理安防设施 |
| `HAS_CRYPTO_PRODUCT` | `System` | `CryptoProduct` | 系统使用密码产品 |
| `HAS_SERVER` | `System` | `Server` | 系统包含服务器或存储设备 |
| `HAS_NETWORK_DEVICE` | `System` | `NetworkDevice` | 系统包含网络及安全设备 |
| `USES_DATABASE` | `System` | `DatabaseSystem` | 系统使用数据库 |
| `HAS_APPLICATION` | `System` | `BusinessApplication` | 系统包含业务应用 |
| `HAS_IMPORTANT_DATA` | `System` | `ImportantData` | 系统涉及重要数据 |
| `HAS_DOCUMENT` | `System` | `ManagementDocument` | 系统具有管理文档 |
| `HAS_PERSON` | `System` | `Person` | 系统相关人员 |
| `HAS_USER_ROLE` | `System` | `UserRole` | 系统定义用户或岗位角色 |
| `HAS_SECURITY_AREA` | `System` | `SecurityArea` | 系统包含物理或逻辑安全区域 |
| `HAS_NETWORK_LINK` | `System` | `NetworkLink` | 系统包含网络通信链路 |
| `HAS_MIDDLEWARE` | `System` | `Middleware` | 系统使用中间件 |
| `USES_CRYPTO_SERVICE` | `System` | `CryptoService` | 系统使用密码服务 |
| `HAS_CRYPTO_APPLICATION` | `System` | `CryptoApplication` | 系统具有密码应用措施 |

## 资产间关系

| 关系 | 起点 | 终点 | 含义 |
|---|---|---|---|
| `DEPLOYED_IN` | `PhysicalSecurityFacility`/`Server`/`NetworkDevice` | `PhysicalEnvironment` | 资产部署在物理环境 |
| `DEPLOYED_ON` | `BusinessApplication`/`DatabaseSystem` | `Server` | 应用或数据库部署在服务器 |
| `STORED_ON` | `ImportantData` | `Server` | 数据存储在服务器或存储设备 |
| `STORED_IN` | `ImportantData` | `DatabaseSystem` | 数据存储在数据库 |
| `BELONGS_TO` | `ImportantData` | `BusinessApplication` | 数据属于业务应用 |
| `CONNECTED_TO` | `NetworkDevice` | `NetworkDevice` | 网络设备连接关系 |
| `FROM_AREA` | `NetworkLink` | `SecurityArea` | 网络链路的源安全区域 |
| `TO_AREA` | `NetworkLink` | `SecurityArea` | 网络链路的目标安全区域 |
| `PROTECTS_BOUNDARY` | `NetworkDevice`/`CryptoProduct` | `SecurityArea`/`System` | 设备保护安全区域或系统边界 |

简单拓扑可直接使用 `CONNECTED_TO`；需要保存协议、端口、加密状态等链路属性时，应使用 `NetworkLink` 节点和 `FROM_AREA`、`TO_AREA` 关系。

## 测评过程关系

| 关系 | 起点 | 终点 | 含义 |
|---|---|---|---|
| `HAS_COMPLIANCE_ITEM` | `Report` | `ComplianceItem` | 报告包含合规检查项 |
| `HAS_FINDING` | `Report` | `Finding` | 报告包含测评发现 |
| `HAS_EVIDENCE` | `Report` | `Evidence` | 报告包含测评证据 |
| `BASED_ON` | `ComplianceItem` | `EvaluationCriterion` | 报告测评记录依据标准化测评指标 |
| `HAS_FINDING` | `ComplianceItem` | `Finding` | 合规检查项产生或关联发现 |
| `SUPPORTED_BY` | `ComplianceItem`/`Finding` | `Evidence` | 判断或发现由证据支持 |

## 密码应用关系

| 关系 | 起点 | 终点 | 含义 |
|---|---|---|---|
| `USES_PRODUCT` | `CryptoApplication`/`CryptoService` | `CryptoProduct` | 密码应用或服务使用产品 |
| `HAS_PRODUCT_TYPE` | `CryptoProduct` | `ProductType` | 密码产品属于标准化产品类型 |
| `USES_ALGORITHM` | `CryptoApplication`/`CryptoProduct`/`CryptoService` | `CryptoAlgorithm` | 使用密码算法 |
| `HAS_USAGE` | `CryptoApplication`/`CryptoProduct` | `CryptoUsage` | 具备密码用途 |
| `SATISFIES` | `CryptoApplication` | `SecurityRequirement` | 满足安全需求 |
| `PROTECTS_DATA` | `CryptoApplication` | `ImportantData` | 保护重要数据 |
| `PROTECTS_ASSET` | `CryptoApplication` | 资产节点 | 保护具体资产 |
| `PROVIDES_SERVICE` | `CryptoProduct` | `CryptoService` | 密码产品提供密码服务能力 |

## 数据分类关系

| 关系 | 起点 | 终点 | 含义 |
|---|---|---|---|
| `HAS_DATA_CATEGORY` | `ImportantData` | `DataCategory` | 重要数据属于标准化数据类别 |

## 威胁关系

| 关系 | 起点 | 终点 | 含义 |
|---|---|---|---|
| `HAS_THREAT` | `System` | `Threat` | 系统涉及某类威胁 |
| `AFFECTS_ASSET` | `Threat` | 资产节点 | 威胁影响具体资产 |
| `AFFECTS_DATA` | `Threat` | `ImportantData` | 威胁影响重要数据 |
| `MITIGATED_BY` | `Threat` | `CryptoApplication` | 威胁由密码应用缓解 |
| `RELATED_TO_REQUIREMENT` | `Threat` | `SecurityRequirement` | 威胁关联安全需求 |

## 管理关系

| 关系 | 起点 | 终点 | 含义 |
|---|---|---|---|
| `REGULATES` | `ManagementDocument` | `CryptoProduct`/`CryptoApplication`/`CryptoService` | 管理文档规范对象 |
| `RESPONSIBLE_FOR` | `Person` | `System` | 人员负责系统 |
| `MANAGES` | `Person` | `CryptoProduct`/`CryptoService` | 人员管理产品或服务 |
| `OPERATES` | `Person` | `Server`/`NetworkDevice`/`BusinessApplication` | 人员操作资产或应用 |

## 自动关联边界

可根据明确引用自动创建的关系：

```text
project_id          -> HAS_REPORT / HAS_TARGET_SYSTEM
report_id           -> EVALUATES / HAS_SECTION / HAS_COMPLIANCE_ITEM / HAS_FINDING / HAS_EVIDENCE
section_id          -> HAS_FIELD
system_id           -> 系统与资产、角色、区域、链路等归属关系
compliance_item_id  -> HAS_FINDING / SUPPORTED_BY
finding_id          -> SUPPORTED_BY
product_type_code   -> HAS_PRODUCT_TYPE
data_category_code  -> HAS_DATA_CATEGORY
criterion_code      -> BASED_ON
algorithm_name(s)   -> USES_ALGORITHM
business_application_id(s) -> BELONGS_TO
server_id(s)        -> STORED_ON
database_system_id(s) / database_id(s) -> STORED_IN
```

以下关系必须来自报告原文、结构化导入映射或人工确认，不能只按标签批量连接：

```text
EXTRACTED_FROM
DEPLOYED_IN / DEPLOYED_ON / STORED_ON / STORED_IN / BELONGS_TO
CONNECTED_TO / FROM_AREA / TO_AREA / PROTECTS_BOUNDARY
USES_PRODUCT / USES_ALGORITHM / HAS_USAGE / SATISFIES
PROTECTS_DATA / PROTECTS_ASSET / PROVIDES_SERVICE
HAS_THREAT / AFFECTS_ASSET / AFFECTS_DATA / MITIGATED_BY / RELATED_TO_REQUIREMENT
REGULATES / RESPONSIBLE_FOR / MANAGES / OPERATES
```

当上述关系由 `link_instances.cypher` 自动创建时，必须满足以下边界：

- 只使用明确字段或本地 ID，不按名称、描述、存储位置等文本模糊猜测。
- 单值字段优先遵循已有命名，例如 `server_id`、`database_system_id`、`business_application_id`；多值场景可兼容 `server_ids`、`database_system_ids`、`business_application_ids`。
- `未明确`、`未提供`、`XX`、`N/A`、`NA`、`无`、空字符串和空列表不创建正常业务关系，应由数据质量检测形成 `Finding`。
