# 约束和实例命名规则

## 节点唯一性

### EvaluationProject

`EvaluationProject.id` 全局唯一。

建议 ID：

```text
prj_{date}_{hash}
```

### Report

`Report.id` 全局唯一。

建议 ID：

```text
rpt_{date}_{hash}
```

### System

`System.id` 全局唯一。

建议 ID：

```text
sys_{report_id}_{normalized_system_name}
```

### 系统内实例节点

资产、人员、文档、密码应用等属于某个系统，不建议只按名称全局唯一。不同系统可以都有“数据库服务器”“加密网关”。

建议 ID：

```text
{system_id}:{entity_type}:{normalized_name}
```

示例：

```text
sys_001:Server:数据库服务器
sys_001:CryptoProduct:商用加密网关
sys_002:Server:数据库服务器
```

### 全局字典节点

以下节点可按名称或编号全局唯一：

| 节点 | 唯一字段 |
|---|---|
| `CryptoAlgorithm` | `name` |
| `CryptoUsage` | `name` |
| `SecurityRequirement` | `name` |
| `Threat` | `code` |
| `ProductType` | `code` |
| `DataCategory` | `code` |
| `EvaluationCriterion` | `code` |

## 多标签规则

同一实体如果具备多个身份，不重复建节点，使用多标签。例如加密网关可同时是密码产品和网络设备，加密服务器可同时是密码产品和服务器资产。

示例：

```cypher
(:Entity:CryptoProduct:NetworkDevice {
  id: "sys_001:CryptoProduct:商用加密网关",
  name: "商用加密网关",
  model: "XX商用加密网关V3.0"
})
```

## 必填字段建议

| 节点 | 必填字段 |
|---|---|
| `EvaluationProject` | `id`、`name` |
| `Report` | `id`、`name` |
| `System` | `id`、`name` |
| `PhysicalEnvironment` | `id`、`name`、`system_id` |
| `CryptoProduct` | `id`、`name`、`system_id` |
| `Server` | `id`、`name`、`system_id` |
| `NetworkDevice` | `id`、`name`、`system_id` |
| `DatabaseSystem` | `id`、`name`、`system_id` |
| `Middleware` | `id`、`name`、`system_id` |
| `BusinessApplication` | `id`、`name`、`system_id` |
| `ImportantData` | `id`、`name`、`system_id` |
| `UserRole` | `id`、`name`、`system_id` |
| `SecurityArea` | `id`、`name`、`system_id` |
| `NetworkLink` | `id`、`name`、`system_id` |
| `CryptoApplication` | `id`、`name`、`system_id`、`domain` |
| `ComplianceItem` | `id`、`name`、`report_id` |
| `Finding` | `id`、`name`、`report_id` |
| `Evidence` | `id`、`name`、`report_id` |
| `ReportSection` | `id`、`report_id`、`section_no`、`title` |
| `ReportField` | `id`、`report_id`、`section_id`、`key`、`name` |
| `CryptoAlgorithm` | `name` |
| `Threat` | `code`、`domain`、`description` |
| `ProductType` | `code`、`name` |
| `DataCategory` | `code`、`name` |
| `EvaluationCriterion` | `code`、`name`、`source_standard`、`clause_no` |

`ReportSection` 和 `ReportField` 是可选溯源辅助节点；不要求每份报告都创建。创建时应满足上表必填字段，核心业务实体之间的关系不得依赖它们中转。

## 缺失值处理

不要把 `未明确`、`未提供`、`XX` 直接当作可信值。

建议处理方式：

```text
属性值保留原文
quality_flags 增加对应质量标记
confidence 降低
```

示例：

```text
vendor: "未明确"
quality_flags: ["MISSING_VENDOR"]
confidence: 0.7
```

## 关系唯一性建议

Neo4j 关系本身不适合强制唯一。建议导入时按以下键去重：

```text
start_node_id + relationship_type + end_node_id
```

如果同一关系来自多个章节，可在关系上追加：

```text
source_sections: ["2.2", "2.4.5"]
source_texts: [...]
```
