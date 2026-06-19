// Detect missing or placeholder key fields and write data-quality Findings.
// This script is idempotent: rerunning it updates the same Finding/Evidence nodes.

WITH
  ["未明确", "未提供", "XX", "N/A", "NA", "无", ""] AS placeholders,
  [
    {label: "CryptoProduct", field: "vendor", fields: ["vendor"], name: "生产厂商"},
    {label: "CryptoProduct", field: "model", fields: ["model"], name: "产品型号"},
    {label: "CryptoProduct", field: "certificate_no", fields: ["certificate_no"], name: "商密产品认证证书编号"},
    {label: "CryptoProduct", field: "algorithm_names", fields: ["algorithm_name", "algorithm_names"], name: "使用算法名称列表"},
    {label: "Server", field: "vendor", fields: ["vendor"], name: "生产厂商"},
    {label: "Server", field: "model", fields: ["model"], name: "型号"},
    {label: "Server", field: "os_version", fields: ["os_version"], name: "操作系统版本"},
    {label: "DatabaseSystem", field: "version", fields: ["version"], name: "数据库版本"},
    {label: "DatabaseSystem", field: "deploy_location", fields: ["deploy_location"], name: "部署位置"},
    {label: "BusinessApplication", field: "version", fields: ["version"], name: "应用版本"},
    {label: "BusinessApplication", field: "deploy_location", fields: ["deploy_location"], name: "部署位置"},
    {label: "ImportantData", field: "data_category_code", fields: ["data_category_code"], name: "数据类别编码"},
    {label: "ImportantData", field: "business_application_id", fields: ["business_application_id", "business_application_ids"], name: "所属业务应用 ID"},
    {label: "ImportantData", field: "server_id", fields: ["server_id", "server_ids"], name: "存储服务器 ID"},
    {label: "ImportantData", field: "database_system_id", fields: ["database_system_id", "database_system_ids", "database_id", "database_ids"], name: "存储数据库 ID"},
    {label: "ImportantData", field: "storage_location", fields: ["storage_location"], name: "存储位置"},
    {label: "CryptoApplication", field: "domain", fields: ["domain"], name: "密码应用域"},
    {label: "CryptoApplication", field: "mechanism", fields: ["mechanism"], name: "技术机制"},
    {label: "CryptoApplication", field: "algorithm_names", fields: ["algorithm_name", "algorithm_names"], name: "使用算法名称列表"},
    {label: "CryptoService", field: "provider", fields: ["provider"], name: "服务提供商"},
    {label: "CryptoService", field: "service_type", fields: ["service_type"], name: "服务类型"},
    {label: "CryptoService", field: "algorithm_names", fields: ["algorithm_name", "algorithm_names"], name: "使用算法名称列表"}
  ] AS rules
UNWIND rules AS rule
MATCH (n:Entity)
WHERE rule.label IN labels(n) AND n.id IS NOT NULL
OPTIONAL MATCH (system:System {id: n.system_id})
WITH placeholders, rule, n, coalesce(n.report_id, system.report_id) AS report_id
WHERE report_id IS NOT NULL
UNWIND rule.fields AS candidate_field
WITH placeholders, rule, n, report_id, collect({field: candidate_field, value: n[candidate_field]}) AS raw_entries
WITH placeholders, rule, n, report_id, raw_entries,
  reduce(values = [], entry IN raw_entries |
    values + CASE
      WHEN entry.value IS NULL THEN []
      WHEN valueType(entry.value) STARTS WITH "LIST" THEN entry.value
      ELSE [entry.value]
    END
  ) AS values,
  [entry IN raw_entries WHERE entry.value IS NOT NULL |
    entry.field + "=" + CASE
      WHEN valueType(entry.value) STARTS WITH "LIST" THEN
        "[" + reduce(text = "", item IN entry.value |
          text + CASE WHEN text = "" THEN "" ELSE ", " END + toString(item)
        ) + "]"
      ELSE toString(entry.value)
    END
  ] AS original_values
WITH placeholders, rule, n, report_id, original_values, values,
  [value IN values WHERE NOT trim(toString(value)) IN placeholders] AS valid_values
WHERE size(values) = 0 OR size(valid_values) = 0
MATCH (report:Report {id: report_id})
WITH report, rule, n,
  CASE
    WHEN size(original_values) = 0 THEN null
    ELSE reduce(text = "", item IN original_values | text + CASE WHEN text = "" THEN "" ELSE "; " END + item)
  END AS raw_value,
  "MISSING_" + toUpper(rule.field) AS quality_flag,
  report.id + ":ComplianceItem:DATA_QUALITY" AS item_id,
  report.id + ":Finding:DATA_QUALITY:" + n.id + ":" + rule.field AS finding_id,
  report.id + ":Evidence:DATA_QUALITY:" + n.id + ":" + rule.field AS evidence_id
SET n.quality_flags = [flag IN coalesce(n.quality_flags, []) WHERE flag <> quality_flag] + [quality_flag],
    n.data_quality_missing_fields = [field IN coalesce(n.data_quality_missing_fields, []) WHERE field <> rule.field] + [rule.field]
MERGE (item:Entity:ComplianceItem {id: item_id})
SET item.report_id = report.id,
    item.name = "数据质量字段完整性检查",
    item.code = "DATA_QUALITY",
    item.domain = "数据质量",
    item.evaluation_method = "规则检测",
    item.applicability = "适用",
    item.result = "存在问题",
    item.source_section = "自动检测",
    item.confidence = 1.0
MERGE (finding:Entity:Finding {id: finding_id})
SET finding.report_id = report.id,
    finding.compliance_item_id = item.id,
    finding.name = rule.label + "." + rule.field + " 字段缺失或为占位值",
    finding.finding_type = "数据质量问题",
    finding.quality_issue_type = "MISSING_FIELD",
    finding.target_node_id = n.id,
    finding.target_node_label = rule.label,
    finding.target_field = rule.field,
    finding.target_field_name = rule.name,
    finding.original_value = raw_value,
    finding.description = "节点 " + n.id + " 的关键字段 " + rule.field + " 缺失、为空或为占位值，需补充明确取值。",
    finding.severity = "低",
    finding.status = "待补充",
    finding.impact = "字段不明确会影响规则关系构建、资产识别或测评结论追溯。",
    finding.recommendation = "补充 " + rule.name + " 的明确值；如无法确认，应保留原文并持续标记为数据质量问题。",
    finding.source_section = coalesce(n.source_section, "自动检测"),
    finding.confidence = 1.0
MERGE (evidence:Entity:Evidence {id: evidence_id})
ON CREATE SET evidence.collected_at = datetime()
SET evidence.report_id = report.id,
    evidence.name = rule.label + "." + rule.field + " 字段质量证据",
    evidence.compliance_item_id = item.id,
    evidence.finding_id = finding.id,
    evidence.evidence_type = "规则检测",
    evidence.description = "字段缺失或占位值检测证据",
    evidence.content = "target_node_id=" + n.id + "; field=" + rule.field + "; original_value=" + coalesce(raw_value, "<NULL>"),
    evidence.source = "detect_missing_fields.cypher"
MERGE (report)-[:HAS_COMPLIANCE_ITEM]->(item)
MERGE (report)-[:HAS_FINDING]->(finding)
MERGE (report)-[:HAS_EVIDENCE]->(evidence)
MERGE (item)-[:HAS_FINDING]->(finding)
MERGE (item)-[:SUPPORTED_BY]->(evidence)
MERGE (finding)-[:SUPPORTED_BY]->(evidence);

MATCH (finding:Finding {finding_type: "数据质量问题"})
RETURN finding.report_id AS report_id, count(finding) AS data_quality_findings
ORDER BY report_id;
