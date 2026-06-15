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

## 文档解析与结构化抽取

仓库提供 `crypto_kg` Python 包，用于把密评报告解析为章节、表格、实体和 Neo4j 关系。当前支持：

- Word `.docx`：提取段落章节和表格，依赖 `python-docx`。
- PDF `.pdf`：优先使用 `pdfplumber` 提取文本和表格；没有该依赖时回退到 PyMuPDF 文本解析。
- 文本 `.txt`/`.md`：识别编号章节和 Markdown/制表符表格。

章节和表格会映射到本体 schema，例如 `2.4.3 密码产品` 自动映射为 `CryptoProduct`，并生成 `System-[:HAS_CRYPTO_PRODUCT]->CryptoProduct`、`CryptoProduct-[:HAS_PRODUCT_TYPE]->ProductType` 等关系。实体标准化会处理多身份问题，例如“商用加密网关”“加密网关”“密码网关”统一为“加密网关”，并打上 `CryptoProduct`、`NetworkDevice` 多标签。

本地运行：

```bash
python -m crypto_kg.cli path/to/report.docx --system-id sys_001 --report-id report_001 --format json
python -m crypto_kg.cli path/to/report.docx --system-id sys_001 --format cypher -o import.cypher
python -m crypto_kg.cli path/to/report.docx --system-id sys_001 --write-neo4j --system-name "被测系统名称"
```

Windows 环境如果未配置 `python` 命令，可使用已安装解释器对应的 `py -3.12 -m crypto_kg.cli ...`，或在 CryptoAgent 的虚拟环境中执行。

接入 CryptoAgent 时，可把本仓库作为本地依赖安装，或直接把 `src` 加入 `PYTHONPATH`，然后在 report agent 的预处理/入库环节调用：

```python
from crypto_kg.integration import build_crypto_agent_payload

payload = build_crypto_agent_payload(
    file_path=r"C:\path\to\report.docx",
    system_id="sys_001",
    report_id="report_001",
)
```

`payload["entities"]`、`payload["relations"]` 可用于人工审核或后续 RAG；`payload["cypher"]` 可在审核后写入 Neo4j。

### 接入 CryptoAgent 工作流

推荐接入方式是在 CryptoAgent 现有 `report_generation/preprocessor/graph.py` 中，在 `parse_user_info` 之后、`update_state` 之前增加一个 KG 写入节点。原因是 `parse_user_info` 已经完成了大模型抽取和冲突合并，此时同时拥有：

- 原始文件文本：`state["file_content"]`
- 当前轮文件：`state["current_files"]`
- 结构化章节信息：`state["system_key_info_chapter2"]`
- 关键字段：`state["key_info"]`、`state["core_info"]`

工具节点示例：

```python
from crypto_kg.integration import ingest_structured_info_to_kg


async def kg_ingest_node(state, config):
    thread_id = config.get("configurable", {}).get("thread_id", "unknown-thread")
    system_name = state.get("key_info", {}).get("系统名称") or state.get("core_info", {}).get("systemName")
    system_id = f"chat:{thread_id}:system:{system_name or 'unknown'}"

    result = await ingest_structured_info_to_kg(
        state.get("system_key_info_chapter2", {}),
        system_id=system_id,
        report_id=f"chat:{thread_id}:report",
        system_name=system_name,
    )
    return {"kg_ingest_result": result, "kg_system_id": system_id}
```

如果希望直接从上传文件解析章节和表格后入库，可以调用：

```python
from crypto_kg.integration import ingest_document_to_kg

await ingest_document_to_kg(file_path, system_id=system_id, report_id=report_id, system_name=system_name)
```

查询阶段建议作为只读工具挂到报告生成或问答节点：

```python
from crypto_kg.integration import query_kg_context

facts = await query_kg_context(system_id=system_id, keywords=["密码产品", "加密网关"], limit=20)
```

这样信息抽取阶段负责“补图谱”，后续报告生成/问答阶段负责“查图谱补上下文”。图谱写入依赖环境变量：

```text
CRYPTO_KG_ENABLED=true
CRYPTO_KG_SRC=C:\Users\23883\Desktop\neo4j_crypto\src
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=crypto_neo4j_password
NEO4J_DATABASE=neo4j
```

CryptoAgent 的 report 包需要安装 `neo4j>=5.14`。本次已在 `packages/domain/report/pyproject.toml` 中补充该依赖；如果使用 `uv`，需要重新同步环境。

初始化 Neo4j schema 和字典节点：

```bash
source .env
docker exec -i crypto-neo4j cypher-shell -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" < ontology/neo4j_schema.cypher
docker exec -i crypto-neo4j cypher-shell -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" < ontology/seed_dictionary.cypher
docker exec -i crypto-neo4j cypher-shell -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" < ontology/link_instances.cypher
```

`link_instances.cypher` 只根据明确的 ID 引用创建关系，可重复执行。算法、威胁、保护对象等语义关系必须由报告内容或人工确认提供，脚本不会按标签猜测关联。

写入一套脱敏的实际业务形态测评数据：

```bash
scripts/load_sample_data.sh
```

该脚本依次应用 schema、全局字典、`ontology/sample_evaluation_data.cypher` 和实例自动关联脚本，可重复执行。样例包含一个政务服务平台，以及资产、密码产品、密码应用、重要数据、威胁、测评项、发现和证据。

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
