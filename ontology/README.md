# 密码应用安全性评估报告知识图谱本体模型

本体模型用于描述不同被测系统的密评报告知识结构。设计目标是先形成稳定的领域模型，再向模型中填充不同报告、不同被测系统的实例数据。

## 分层设计

本体分为三层：

```text
本体层：实体类型、关系类型、属性字段、枚举和约束
实例层：某一份报告、某一个被测系统、某一组资产和密码应用实例
字典层：密码算法、安全需求、密码用途、威胁分类、产品类型、数据类别和测评指标等可复用标准节点
```

## 核心对象

第一版覆盖以下对象：

```text
EvaluationProject
Report
System
PhysicalEnvironment
PhysicalSecurityFacility
CryptoProduct
Server
NetworkDevice
DatabaseSystem
Middleware
BusinessApplication
ImportantData
ManagementDocument
Person
UserRole
SecurityArea
NetworkLink
CryptoService
CryptoApplication
CryptoAlgorithm
CryptoUsage
SecurityRequirement
ProductType
DataCategory
EvaluationCriterion
ComplianceItem
Finding
Evidence
Threat
```

可选的报告结构与溯源辅助对象：

```text
ReportSection
ReportField
```

`ReportSection` 和 `ReportField` 用于保留报告章节、字段和原文定位，不属于核心领域对象。核心业务实体及其关系不应依赖报告结构节点才能查询。

## 建模原则

1. 每份测评报告建立一个 `Report` 节点。
2. 每个被测系统建立一个 `System` 节点。
3. 资产、密码应用、人员、文档等实例节点必须归属于某个 `System` 或 `Report`。
4. 密码算法、密码用途、安全需求、安全威胁、密码产品类型、数据类别和测评指标作为全局字典节点复用。
5. 同一个实体可使用多标签，例如加密网关可同时是 `CryptoProduct` 和 `NetworkDevice`，加密服务器可同时是 `CryptoProduct` 和 `Server`。
6. 每个节点保留来源章节、来源文本和抽取置信度，便于校验与回溯。
7. 为避免同义标签重复建模，使用 `System`、`Server`、`DatabaseSystem`、`ImportantData` 分别表示候选类型 `TargetSystem`、`ServerDevice`、`Database`、`DataAsset`。
8. `ReportSection`、`ReportField` 仅在需要保留完整报告结构和精确溯源时创建；核心业务关系直接连接领域实体。

## 文件说明

```text
entity_types.md       实体类型和属性字段
relation_types.md     关系类型定义
enums.md              枚举值和字典建议
constraints.md        唯一性规则、命名规则和质量标记
neo4j_schema.cypher   Neo4j 约束和索引草案
link_instances.cypher 根据明确 ID 引用创建可确定的实例关系
sample_evaluation_data.cypher 脱敏的实际业务形态测评实例和明确语义关系
```
