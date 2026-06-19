# 实体类型设计

## 通用属性

所有实例节点建议包含以下通用属性：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `id` | string | 是 | 全局唯一 ID |
| `name` | string | 是 | 名称 |
| `report_id` | string | 否 | 所属报告 ID |
| `system_id` | string | 否 | 所属被测系统 ID |
| `source_section` | string | 否 | 来源章节，例如 `2.4.3` |
| `source_text` | string | 否 | 来源原文 |
| `confidence` | float | 否 | 抽取置信度，人工录入可为 `1.0` |
| `quality_flags` | list<string> | 否 | 数据质量标记 |
| `remark` | string | 否 | 备注 |
| `created_at` | datetime | 否 | 创建时间 |
| `updated_at` | datetime | 否 | 更新时间 |

## 类型名称映射

为避免同一概念使用不同标签重复建模，以下候选类型沿用已有实体类型：

| 候选类型 | 沿用类型 | 说明 |
|---|---|---|
| `TargetSystem` | `System` | 被测目标系统 |
| `ServerDevice` | `Server` | 服务器或存储设备 |
| `Database` | `DatabaseSystem` | 数据库管理系统 |
| `DataAsset` | `ImportantData` | 需要保护的重要数据资产 |

`BusinessApplication`、`NetworkDevice`、`CryptoProduct`、`CryptoService` 已存在，继续使用原标签。

## EvaluationProject

测评项目，用于描述一次测评工作的范围、状态和组织信息。一个测评项目可以产生一份或多份报告，并覆盖一个或多个被测系统。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 测评项目 ID |
| `name` | string | 测评项目名称 |
| `project_no` | string | 项目编号 |
| `evaluation_type` | string | 测评类型 |
| `status` | string | 项目状态 |
| `start_date` | date | 开始日期 |
| `end_date` | date | 结束日期 |
| `customer_organization` | string | 委托单位 |
| `evaluation_organization` | string | 测评机构 |

## Report

测评报告。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 报告 ID |
| `project_id` | string | 所属测评项目 ID |
| `name` | string | 报告名称 |
| `report_no` | string | 报告编号 |
| `evaluation_type` | string | 测评类型 |
| `evaluation_date` | date | 测评日期 |
| `version` | string | 报告版本 |
| `organization` | string | 被测单位或委托单位 |

## System

被测系统。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 系统 ID |
| `project_id` | string | 所属测评项目 ID |
| `report_id` | string | 所属报告 ID |
| `name` | string | 系统名称 |
| `deployment_env` | string | 部署环境 |
| `business_domain` | string | 业务领域 |
| `service_scope` | string | 服务对象和覆盖范围 |
| `description` | string | 系统概述 |
| `network_architecture` | string | 网络架构描述 |
| `is_dmz` | boolean | 是否位于 DMZ |

## PhysicalEnvironment

物理环境，例如专用机房。

| 字段 | 类型 | 说明 |
|---|---|---|
| `location` | string | 物理位置 |
| `area` | string | 面积 |
| `importance_level` | string | 重要程度 |
| `environment_type` | string | 机房、办公区、灾备机房等 |

## PhysicalSecurityFacility

物理安防设施，例如门禁、视频监控。

| 字段 | 类型 | 说明 |
|---|---|---|
| `vendor` | string | 生产厂商 |
| `model` | string | 型号 |
| `facility_type` | string | 门禁、视频监控、UPS、防雷等 |
| `importance_level` | string | 重要程度 |
| `asset_type` | string | 资产类型枚举值 |
| `authentication_method` | string | 身份鉴别方式 |
| `retention_period` | string | 记录保存时间 |

## CryptoProduct

密码产品，例如加密网关、UKey、加密服务器。

| 字段 | 类型 | 说明 |
|---|---|---|
| `vendor` | string | 生产厂商 |
| `model` | string | 产品型号 |
| `certificate_no` | string | 商密产品认证证书编号 |
| `quantity` | integer | 数量 |
| `purpose` | string | 用途 |
| `importance_level` | string | 重要程度 |
| `product_type` | string | 密码产品类型便捷值，应与关联的 `ProductType.name` 一致 |
| `product_type_code` | string | 关联的全局密码产品类型编码 |
| `algorithm_name` | string | 明确抽取的单个算法名称，可用于自动创建 `USES_ALGORITHM` |
| `algorithm_names` | list<string> | 明确抽取的算法名称列表，可用于自动创建 `USES_ALGORITHM` |
| `asset_type` | string | 资产类型枚举值 |
| `is_certified` | boolean | 是否具备认证证书 |

## Server

服务器或存储设备。

| 字段 | 类型 | 说明 |
|---|---|---|
| `vendor` | string | 生产厂商 |
| `model` | string | 型号 |
| `os_version` | string | 操作系统版本 |
| `is_virtual` | boolean | 是否虚拟设备 |
| `purpose` | string | 用途 |
| `quantity` | integer | 数量 |
| `importance_level` | string | 重要程度 |
| `server_type` | string | 应用服务器、数据库服务器、日志审计服务器等 |
| `asset_type` | string | 资产类型枚举值 |

## NetworkDevice

网络及安全设备。

| 字段 | 类型 | 说明 |
|---|---|---|
| `vendor` | string | 生产厂商 |
| `model` | string | 型号 |
| `device_type` | string | 防火墙、交换机、IDS、加密网关等 |
| `purpose` | string | 用途 |
| `quantity` | integer | 数量 |
| `importance_level` | string | 重要程度 |
| `network_layer` | string | 核心层、汇聚层、接入层、边界等 |
| `asset_type` | string | 资产类型枚举值 |

## DatabaseSystem

数据库管理系统。

| 字段 | 类型 | 说明 |
|---|---|---|
| `version` | string | 数据库版本 |
| `deploy_location` | string | 部署位置 |
| `main_function` | string | 主要功能 |
| `importance_level` | string | 重要程度 |
| `architecture` | string | 主从、集群、单机等 |
| `asset_type` | string | 资产类型枚举值 |

## Middleware

支撑业务应用运行的中间件，例如应用服务器、消息中间件、缓存和 API 网关。

| 字段 | 类型 | 说明 |
|---|---|---|
| `middleware_type` | string | 应用服务器、消息队列、缓存、API 网关等 |
| `vendor` | string | 生产厂商 |
| `version` | string | 版本 |
| `deploy_location` | string | 部署位置 |
| `main_function` | string | 主要功能 |
| `importance_level` | string | 重要程度 |
| `asset_type` | string | 资产类型枚举值 |

## BusinessApplication

关键业务应用。

| 字段 | 类型 | 说明 |
|---|---|---|
| `version` | string | 应用版本 |
| `deploy_location` | string | 部署位置 |
| `main_function` | string | 主要功能 |
| `business_process` | string | 业务流程 |
| `importance_level` | string | 重要程度 |
| `asset_type` | string | 资产类型枚举值 |

## ImportantData

重要数据。

| 字段 | 类型 | 说明 |
|---|---|---|
| `description` | string | 数据描述 |
| `data_type` | string | 数据类别便捷值，应与关联的 `DataCategory.name` 一致 |
| `data_category_code` | string | 关联的全局数据类别编码 |
| `business_application_id` | string | 明确抽取的所属业务应用 ID，可用于自动创建 `BELONGS_TO` |
| `business_application_ids` | list<string> | 明确抽取的所属业务应用 ID 列表，可用于自动创建 `BELONGS_TO` |
| `server_id` | string | 明确抽取的存储服务器 ID，可用于自动创建 `STORED_ON` |
| `server_ids` | list<string> | 明确抽取的存储服务器 ID 列表，可用于自动创建 `STORED_ON` |
| `database_system_id` | string | 明确抽取的存储数据库 ID，可用于自动创建 `STORED_IN` |
| `database_system_ids` | list<string> | 明确抽取的存储数据库 ID 列表，可用于自动创建 `STORED_IN` |
| `database_id` | string | `database_system_id` 的兼容字段 |
| `database_ids` | list<string> | `database_system_ids` 的兼容字段 |
| `storage_location` | string | 存储位置 |
| `security_needs` | list<string> | 安全需求 |
| `importance_level` | string | 重要程度 |
| `asset_type` | string | 资产类型枚举值 |

## ManagementDocument

安全管理文档。

| 字段 | 类型 | 说明 |
|---|---|---|
| `main_content` | string | 主要内容 |
| `management_topic` | string | 管理主题 |
| `effective_status` | string | 生效状态 |
| `revision_cycle` | string | 修订周期 |

## Person

相关人员。

| 字段 | 类型 | 说明 |
|---|---|---|
| `role` | string | 岗位或角色 |
| `responsibility` | string | 职责说明 |
| `contact` | string | 联系方式 |
| `department` | string | 所属部门 |

## UserRole

系统中的用户角色或岗位角色，不表示某个具体人员。

| 字段 | 类型 | 说明 |
|---|---|---|
| `role_code` | string | 角色编码 |
| `description` | string | 角色说明 |
| `responsibilities` | list<string> | 职责列表 |
| `permissions` | list<string> | 权限列表 |
| `role_type` | string | 业务、管理、运维、审计等角色类型 |

## SecurityArea

系统的物理或逻辑安全区域，例如机房、互联网区、DMZ、核心业务区。

| 字段 | 类型 | 说明 |
|---|---|---|
| `area_type` | string | 区域形态，例如物理区域、网络安全域 |
| `zone_type` | string | 网络区域类型枚举值 |
| `security_level` | string | 安全等级 |
| `location` | string | 物理位置或逻辑位置 |
| `boundary_description` | string | 区域边界描述 |
| `protection_requirements` | list<string> | 区域保护要求 |

## NetworkLink

系统内或系统间的网络通信链路。

| 字段 | 类型 | 说明 |
|---|---|---|
| `source_endpoint` | string | 源端点描述 |
| `target_endpoint` | string | 目标端点描述 |
| `protocol` | string | 通信协议 |
| `port` | string | 端口或端口范围 |
| `link_type` | string | 专线、互联网、内部网络等 |
| `encryption_status` | string | 链路加密状态 |
| `boundary_crossing` | boolean | 是否跨越安全区域边界 |

## CryptoService

密码服务。

| 字段 | 类型 | 说明 |
|---|---|---|
| `provider` | string | 服务提供商 |
| `service_type` | string | 电子印章、时间戳、CA 等 |
| `purpose` | string | 服务用途 |
| `algorithm_name` | string | 明确抽取的单个算法名称，可用于自动创建 `USES_ALGORITHM` |
| `algorithm_names` | list<string> | 明确抽取的算法名称列表，可用于自动创建 `USES_ALGORITHM` |

## CryptoApplication

密码应用措施或密码应用场景。

| 字段 | 类型 | 说明 |
|---|---|---|
| `domain` | string | 密码应用域 |
| `scenario` | string | 应用场景 |
| `description` | string | 具体描述 |
| `mechanism` | string | 技术机制 |
| `algorithm_name` | string | 明确抽取的单个算法名称，可用于自动创建 `USES_ALGORITHM` |
| `algorithm_names` | list<string> | 明确抽取的算法名称列表，可用于自动创建 `USES_ALGORITHM` |
| `frequency` | string | 校验或执行频率 |
| `compliance_statement` | string | 合规性说明 |

## CryptoAlgorithm

密码算法，全局字典节点。

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | 算法名称，例如 SM2 |
| `algorithm_type` | string | 对称、非对称、杂凑、协议、MAC 等 |
| `standard` | string | 标准或说明 |

## CryptoUsage

密码用途，全局字典节点。

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | 用途名称 |
| `description` | string | 用途说明 |

## SecurityRequirement

安全需求，全局字典节点。

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | 需求名称 |
| `description` | string | 需求说明 |

## ProductType

密码产品类型，全局字典节点。用于统一不同报告中的产品类型命名，并可进一步关联适用标准、算法和密码用途。

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 全局唯一类型编码 |
| `name` | string | 类型名称 |
| `description` | string | 类型说明 |

## DataCategory

数据类别，全局字典节点。用于统一不同报告中的数据分类，并支持关联安全需求、威胁和保护措施。

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 全局唯一类别编码 |
| `name` | string | 类别名称 |
| `description` | string | 类别说明 |

## EvaluationCriterion

标准化测评指标或条款，全局字典节点。不同报告中的 `ComplianceItem` 应关联到同一指标节点。

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 全局唯一指标编码 |
| `name` | string | 指标名称 |
| `domain` | string | 所属测评域 |
| `requirement_text` | string | 标准要求内容 |
| `source_standard` | string | 来源标准 |
| `clause_no` | string | 来源条款编号 |
| `description` | string | 补充说明 |

## ComplianceItem

某份报告中对标准化测评指标的实际测评记录。

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 合规检查项编码 |
| `criterion_code` | string | 关联的全局测评指标编码 |
| `domain` | string | 所属测评域 |
| `requirement_text` | string | 要求内容 |
| `evaluation_method` | string | 测评方法 |
| `applicability` | string | 适用性说明 |
| `result` | string | 合规结果枚举值 |

## Finding

测评过程中发现的问题、缺陷或不符合项。

| 字段 | 类型 | 说明 |
|---|---|---|
| `compliance_item_id` | string | 关联的合规检查项 ID |
| `finding_type` | string | 问题、不符合项、观察项等 |
| `description` | string | 发现内容 |
| `severity` | string | 严重程度 |
| `status` | string | 处理状态 |
| `impact` | string | 影响说明 |
| `recommendation` | string | 整改建议 |

## Evidence

支持测评判断或发现结论的证据。

| 字段 | 类型 | 说明 |
|---|---|---|
| `compliance_item_id` | string | 直接支持的合规检查项 ID |
| `finding_id` | string | 直接支持的发现 ID |
| `evidence_type` | string | 文档、截图、访谈、配置、日志等 |
| `description` | string | 证据说明 |
| `content` | string | 证据文本内容 |
| `source` | string | 证据来源 |
| `collected_at` | datetime | 采集时间 |
| `file_reference` | string | 外部文件引用 |

## Threat

安全威胁，全局字典节点。

| 字段 | 类型 | 说明 |
|---|---|---|
| `code` | string | 威胁编号，例如 TP1 |
| `domain` | string | 威胁层面 |
| `category` | string | 威胁分类 |
| `description` | string | 威胁描述 |

## 可选溯源辅助类型

以下类型用于保留完整报告结构和精确来源定位，不属于核心领域实体。只需要简单溯源时，优先使用通用属性 `source_section` 和 `source_text`，无需创建这些节点。

### ReportSection

报告章节，可选创建。

| 字段 | 类型 | 说明 |
|---|---|---|
| `report_id` | string | 所属报告 ID |
| `section_no` | string | 章节号，例如 `2.4.3` |
| `title` | string | 章节标题 |
| `content` | string | 章节内容 |

### ReportField

报告字段，可选创建。

| 字段 | 类型 | 说明 |
|---|---|---|
| `report_id` | string | 所属报告 ID |
| `section_id` | string | 所属报告章节 ID |
| `key` | string | 字段编码 |
| `name` | string | 字段名称 |
| `field_type` | string | 文本、表格、图片等 |
| `value` | string | 字段值 |
| `required` | boolean | 是否必填 |
