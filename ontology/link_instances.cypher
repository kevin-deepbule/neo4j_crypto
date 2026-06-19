// Create only relationships that can be determined from explicit ID references.
// This script is idempotent: rerunning it does not create duplicate relationships.

// Evaluation project ownership.
MATCH (project:EvaluationProject)
MATCH (report:Report {project_id: project.id})
MERGE (project)-[:HAS_REPORT]->(report);

MATCH (project:EvaluationProject)
MATCH (system:System {project_id: project.id})
MERGE (project)-[:HAS_TARGET_SYSTEM]->(system);

// Evaluated systems.
MATCH (report:Report)
MATCH (system:System {report_id: report.id})
MERGE (report)-[:EVALUATES]->(system);

// Optional report structure. These relationships are created only when
// ReportSection and ReportField source nodes have been imported.
MATCH (report:Report)
MATCH (section:ReportSection {report_id: report.id})
MERGE (report)-[:HAS_SECTION]->(section);

MATCH (section:ReportSection)
MATCH (field:ReportField {section_id: section.id})
MERGE (section)-[:HAS_FIELD]->(field);

// System-owned instances.
MATCH (system:System)
MATCH (node:PhysicalEnvironment {system_id: system.id})
MERGE (system)-[:HAS_PHYSICAL_ENVIRONMENT]->(node);

MATCH (system:System)
MATCH (node:PhysicalSecurityFacility {system_id: system.id})
MERGE (system)-[:HAS_SECURITY_FACILITY]->(node);

MATCH (system:System)
MATCH (node:CryptoProduct {system_id: system.id})
MERGE (system)-[:HAS_CRYPTO_PRODUCT]->(node);

MATCH (system:System)
MATCH (node:Server {system_id: system.id})
MERGE (system)-[:HAS_SERVER]->(node);

MATCH (system:System)
MATCH (node:NetworkDevice {system_id: system.id})
MERGE (system)-[:HAS_NETWORK_DEVICE]->(node);

MATCH (system:System)
MATCH (node:DatabaseSystem {system_id: system.id})
MERGE (system)-[:USES_DATABASE]->(node);

MATCH (system:System)
MATCH (node:Middleware {system_id: system.id})
MERGE (system)-[:HAS_MIDDLEWARE]->(node);

MATCH (system:System)
MATCH (node:BusinessApplication {system_id: system.id})
MERGE (system)-[:HAS_APPLICATION]->(node);

MATCH (system:System)
MATCH (node:ImportantData {system_id: system.id})
MERGE (system)-[:HAS_IMPORTANT_DATA]->(node);

MATCH (system:System)
MATCH (node:ManagementDocument {system_id: system.id})
MERGE (system)-[:HAS_DOCUMENT]->(node);

MATCH (system:System)
MATCH (node:Person {system_id: system.id})
MERGE (system)-[:HAS_PERSON]->(node);

MATCH (system:System)
MATCH (node:UserRole {system_id: system.id})
MERGE (system)-[:HAS_USER_ROLE]->(node);

MATCH (system:System)
MATCH (node:SecurityArea {system_id: system.id})
MERGE (system)-[:HAS_SECURITY_AREA]->(node);

MATCH (system:System)
MATCH (node:NetworkLink {system_id: system.id})
MERGE (system)-[:HAS_NETWORK_LINK]->(node);

MATCH (system:System)
MATCH (node:CryptoService {system_id: system.id})
MERGE (system)-[:USES_CRYPTO_SERVICE]->(node);

MATCH (system:System)
MATCH (node:CryptoApplication {system_id: system.id})
MERGE (system)-[:HAS_CRYPTO_APPLICATION]->(node);

// Report-owned assessment instances.
MATCH (report:Report)
MATCH (item:ComplianceItem {report_id: report.id})
MERGE (report)-[:HAS_COMPLIANCE_ITEM]->(item);

MATCH (report:Report)
MATCH (finding:Finding {report_id: report.id})
MERGE (report)-[:HAS_FINDING]->(finding);

MATCH (report:Report)
MATCH (evidence:Evidence {report_id: report.id})
MERGE (report)-[:HAS_EVIDENCE]->(evidence);

MATCH (item:ComplianceItem)
MATCH (finding:Finding {compliance_item_id: item.id})
MERGE (item)-[:HAS_FINDING]->(finding);

MATCH (item:ComplianceItem)
MATCH (evidence:Evidence {compliance_item_id: item.id})
MERGE (item)-[:SUPPORTED_BY]->(evidence);

MATCH (finding:Finding)
MATCH (evidence:Evidence {finding_id: finding.id})
MERGE (finding)-[:SUPPORTED_BY]->(evidence);

// Explicit references to reusable dictionary knowledge.
MATCH (product:CryptoProduct)
MATCH (type:ProductType {code: product.product_type_code})
MERGE (product)-[:HAS_PRODUCT_TYPE]->(type);

MATCH (data:ImportantData)
MATCH (category:DataCategory {code: data.data_category_code})
MERGE (data)-[:HAS_DATA_CATEGORY]->(category);

MATCH (item:ComplianceItem)
MATCH (criterion:EvaluationCriterion {code: item.criterion_code})
MERGE (item)-[:BASED_ON]->(criterion);

// Rule-based relationships from explicit extraction fields.
// Placeholder values are ignored here and handled by data quality checks.
WITH ["未明确", "未提供", "XX", "N/A", "NA", "无", ""] AS placeholders
MATCH (product:CryptoProduct)
UNWIND coalesce(product.algorithm_names, []) +
  CASE WHEN product.algorithm_name IS NULL THEN [] ELSE [product.algorithm_name] END AS raw_algorithm
WITH product, trim(toString(raw_algorithm)) AS algorithm_name, placeholders
WHERE NOT algorithm_name IN placeholders
MATCH (algorithm:CryptoAlgorithm {name: algorithm_name})
MERGE (product)-[:USES_ALGORITHM]->(algorithm);

WITH ["未明确", "未提供", "XX", "N/A", "NA", "无", ""] AS placeholders
MATCH (app:CryptoApplication)
UNWIND coalesce(app.algorithm_names, []) +
  CASE WHEN app.algorithm_name IS NULL THEN [] ELSE [app.algorithm_name] END AS raw_algorithm
WITH app, trim(toString(raw_algorithm)) AS algorithm_name, placeholders
WHERE NOT algorithm_name IN placeholders
MATCH (algorithm:CryptoAlgorithm {name: algorithm_name})
MERGE (app)-[:USES_ALGORITHM]->(algorithm);

WITH ["未明确", "未提供", "XX", "N/A", "NA", "无", ""] AS placeholders
MATCH (service:CryptoService)
UNWIND coalesce(service.algorithm_names, []) +
  CASE WHEN service.algorithm_name IS NULL THEN [] ELSE [service.algorithm_name] END AS raw_algorithm
WITH service, trim(toString(raw_algorithm)) AS algorithm_name, placeholders
WHERE NOT algorithm_name IN placeholders
MATCH (algorithm:CryptoAlgorithm {name: algorithm_name})
MERGE (service)-[:USES_ALGORITHM]->(algorithm);

WITH ["未明确", "未提供", "XX", "N/A", "NA", "无", ""] AS placeholders
MATCH (data:ImportantData)
UNWIND coalesce(data.business_application_ids, []) +
  CASE WHEN data.business_application_id IS NULL THEN [] ELSE [data.business_application_id] END AS raw_app_id
WITH data, trim(toString(raw_app_id)) AS app_id, placeholders
WHERE NOT app_id IN placeholders
MATCH (app:BusinessApplication {id: app_id})
MERGE (data)-[:BELONGS_TO]->(app);

WITH ["未明确", "未提供", "XX", "N/A", "NA", "无", ""] AS placeholders
MATCH (data:ImportantData)
UNWIND coalesce(data.server_ids, []) +
  CASE WHEN data.server_id IS NULL THEN [] ELSE [data.server_id] END AS raw_server_id
WITH data, trim(toString(raw_server_id)) AS server_id, placeholders
WHERE NOT server_id IN placeholders
MATCH (server:Server {id: server_id})
MERGE (data)-[:STORED_ON]->(server);

WITH ["未明确", "未提供", "XX", "N/A", "NA", "无", ""] AS placeholders
MATCH (data:ImportantData)
UNWIND coalesce(data.database_system_ids, []) +
  coalesce(data.database_ids, []) +
  CASE WHEN data.database_system_id IS NULL THEN [] ELSE [data.database_system_id] END +
  CASE WHEN data.database_id IS NULL THEN [] ELSE [data.database_id] END AS raw_database_id
WITH data, trim(toString(raw_database_id)) AS database_id, placeholders
WHERE NOT database_id IN placeholders
MATCH (database:DatabaseSystem {id: database_id})
MERGE (data)-[:STORED_IN]->(database);

// Execution summary.
MATCH ()-[relationship]->()
RETURN type(relationship) AS relationship_type, count(*) AS count
ORDER BY relationship_type;
