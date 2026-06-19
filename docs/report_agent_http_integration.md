# Report 智能体 HTTP 对接说明

本仓库提供面向 `CryptoAgent_QingDao` report 智能体的知识图谱查询 API。当前阶段只在 `neo4j_crypto` 中提供 HTTP 服务，不修改 report 智能体代码。

## 启动顺序

```bash
sudo scripts/neo4j.sh up
sudo scripts/load_sample_data.sh
uv run uvicorn crypto_kg_api.main:app --host 0.0.0.0 --port 8000
```

## 健康检查

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/ready
```

`health` 只表示 API 进程存活；`ready` 会检查 Neo4j 是否可连接。

## 报告生成上下文接口

report 智能体后续优先调用：

```bash
curl http://localhost:8000/api/v1/reports/rpt_20260610_gov_service/generation-context
```

返回结构：

```json
{
  "found": true,
  "report": {},
  "system": {},
  "assets": {},
  "crypto_applications": [],
  "data_protection": {"nodes": [], "relationships": []},
  "findings": [],
  "evidences": [],
  "quality_flags": []
}
```

## 字段使用建议

| 返回字段 | 建议用于报告章节 |
|---|---|
| `report` | 报告基本信息 |
| `system` | 被测系统情况 |
| `assets` | 系统资产、测评对象范围 |
| `assets.crypto_products` | 密码产品使用情况 |
| `assets.important_data` | 重要数据清单 |
| `crypto_applications` | 密码应用情况 |
| `data_protection` | 重要数据保护关系 |
| `findings` | 测评发现、风险分析 |
| `evidences` | 证据引用 |
| `quality_flags` | 缺失值、占位值、低置信度提示 |

## 上层处理要求

1. `found=false` 时，report 智能体应提示当前报告未入库或 `report_id` 不匹配。
2. `ready` 返回 503 时，report 智能体应提示知识图谱服务不可用，不应编造图谱结论。
3. 空数组表示图中没有明确关系或节点，不代表报告中一定不存在对应事实。
4. `data_protection.relationships` 只包含图中已有显式关系，不做名称匹配或文本推断。
5. `quality_flags` 应作为写作和审核提示保留，不应被自动清洗为可信值。
