# Crypto Neo4j

密码安全应用测评报告知识图谱项目。

## 本体模型

密评报告知识图谱的本体模型放在 `ontology/` 目录：

```text
ontology/README.md
ontology/entity_types.md
ontology/relation_types.md
ontology/enums.md
ontology/constraints.md
ontology/neo4j_schema.cypher
ontology/link_instances.cypher
```

本体设计采用“报告实例 + 被测系统实例 + 全局字典”的结构。不同报告中的资产、密码应用、人员、文档等实例挂到对应 `System` 节点下；密码算法、安全需求、密码用途、安全威胁、密码产品类型、数据类别和测评指标作为全局字典节点复用。

简单状态和分类提示使用属性枚举，例如 `AssetType`、`NetworkZoneType`、`ComplianceResult`；需要跨报告复用并与其他知识建立关系的概念使用字典节点，例如 `ProductType`、`DataCategory`、`EvaluationCriterion`。

`ReportSection` 和 `ReportField` 是可选的报告结构与溯源辅助节点，不属于图谱核心。核心业务实体直接建立关系；仅在需要完整报告结构或精确原文定位时创建章节、字段和 `EXTRACTED_FROM` 关系。

初始化 Neo4j schema 和字典节点：

```bash
source .env
docker exec -i crypto-neo4j cypher-shell -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" < ontology/neo4j_schema.cypher
docker exec -i crypto-neo4j cypher-shell -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" < ontology/seed_dictionary.cypher
docker exec -i crypto-neo4j cypher-shell -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" < ontology/link_instances.cypher
```

`link_instances.cypher` 只根据明确字段或 ID 引用创建关系，可重复执行。脚本支持从 `algorithm_name` / `algorithm_names`、`business_application_id` / `business_application_ids`、`server_id` / `server_ids`、`database_system_id` / `database_system_ids` / `database_id` / `database_ids` 自动创建已定义关系；不会按名称、描述或存储位置模糊猜测关联。`未明确`、`未提供`、`XX`、`N/A`、`NA`、`无` 和空值不会创建正常业务关系。

写入一套脱敏的实际业务形态测评数据：

```bash
scripts/load_sample_data.sh
```

该脚本依次应用 schema、全局字典、`ontology/sample_evaluation_data.cypher` 和实例自动关联脚本，可重复执行。样例包含一个政务服务平台，以及资产、密码产品、密码应用、重要数据、威胁、测评项、发现和证据。

执行缺失字段检测，并把数据质量问题写回为 `Finding`：

```bash
chmod +x scripts/detect_missing_fields.sh
scripts/detect_missing_fields.sh
```

也可以直接执行 Cypher：

```bash
source .env
docker exec -i crypto-neo4j cypher-shell -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" < ontology/detect_missing_fields.cypher
```

缺失字段检测会检查关键字段是否为空、空列表或占位值，并保留原始值；检测结果写入已有报告模型：`Report -[:HAS_FINDING]-> Finding`、`ComplianceItem -[:HAS_FINDING]-> Finding`、`Finding -[:SUPPORTED_BY]-> Evidence`。Finding 使用稳定 ID，可重复执行，不会生成重复问题记录。

### 验收查询

规则生成的算法关系：

```cypher
MATCH (n)-[:USES_ALGORITHM]->(algorithm:CryptoAlgorithm)
WHERE n:CryptoProduct OR n:CryptoApplication OR n:CryptoService
RETURN labels(n) AS labels, n.name AS source, collect(algorithm.name) AS algorithms
ORDER BY source;
```

规则生成的数据归属和存储关系：

```cypher
MATCH (data:ImportantData)
OPTIONAL MATCH (data)-[:BELONGS_TO]->(app:BusinessApplication)
OPTIONAL MATCH (data)-[:STORED_ON]->(server:Server)
OPTIONAL MATCH (data)-[:STORED_IN]->(database:DatabaseSystem)
RETURN data.name AS data,
       collect(DISTINCT app.name) AS applications,
       collect(DISTINCT server.name) AS servers,
       collect(DISTINCT database.name) AS databases
ORDER BY data;
```

某个报告下的数据质量 Finding：

```cypher
MATCH (report:Report {id: "rpt_20260610_gov_service"})-[:HAS_FINDING]->(finding:Finding)
WHERE finding.finding_type = "数据质量问题"
RETURN finding.target_node_id AS node_id,
       finding.target_field AS field,
       finding.original_value AS original_value,
       finding.description AS description
ORDER BY node_id, field;
```

重复执行后的关系和 Finding 去重检查：

```cypher
MATCH (a)-[r]->(b)
WHERE type(r) IN ["USES_ALGORITHM", "BELONGS_TO", "STORED_ON", "STORED_IN"]
WITH elementId(a) AS start_id, type(r) AS relationship_type, elementId(b) AS end_id, count(*) AS count
WHERE count > 1
RETURN start_id, relationship_type, end_id, count;

MATCH (finding:Finding {finding_type: "数据质量问题"})
WITH finding.id AS id, count(*) AS count
WHERE count > 1
RETURN id, count;
```

## Neo4j 本地部署

本项目推荐使用 Docker Compose 部署 Neo4j，便于后续和 FastAPI、Vue 3 + TypeScript 一起组成完整开发环境。

### 启动

```bash
chmod +x scripts/neo4j.sh
scripts/neo4j.sh up
```

首次运行会自动从 `.env.example` 生成 `.env`。本地默认账号：

```text
username: neo4j
password: crypto_neo4j_password
```

### 访问

```text
Neo4j Browser: http://localhost:7474
Bolt URI:       bolt://localhost:7687
```

### 常用命令

```bash
scripts/neo4j.sh up       # 启动 Neo4j
scripts/neo4j.sh logs     # 查看日志
scripts/neo4j.sh shell    # 进入 cypher-shell
scripts/neo4j.sh status   # 查看状态
scripts/neo4j.sh down     # 停止服务
scripts/neo4j.sh clean    # 停止并删除数据卷
```

`clean` 会删除 Neo4j 数据卷，只建议在本地重置开发环境时使用。

### 环境变量

配置项在 `.env` 中维护，常用项：

```text
NEO4J_IMAGE=neo4j:5.26-community
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=crypto_neo4j_password
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
```

非本地环境请修改 `NEO4J_PASSWORD`。
