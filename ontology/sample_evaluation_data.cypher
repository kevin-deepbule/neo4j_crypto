// 脱敏的密码应用安全性评估实例数据。
// 本脚本可重复执行；节点和关系均使用稳定唯一键 MERGE。

MERGE (project:EvaluationProject {id: "prj_20260610_gov_service"})
SET project.name = "某市政务服务平台密码应用安全性评估项目",
    project.project_no = "MYP-2026-001",
    project.evaluation_type = "密码应用安全性评估",
    project.status = "已完成",
    project.start_date = date("2026-05-11"),
    project.end_date = date("2026-05-29"),
    project.customer_organization = "某市政务服务管理机构",
    project.evaluation_organization = "某密码测评机构";

MERGE (report:Report {id: "rpt_20260610_gov_service"})
SET report.project_id = "prj_20260610_gov_service",
    report.name = "某市政务服务平台密码应用安全性评估报告",
    report.report_no = "MYP-2026-001-R1",
    report.evaluation_type = "密码应用安全性评估",
    report.evaluation_date = date("2026-05-29"),
    report.version = "V1.0",
    report.organization = "某市政务服务管理机构";

MERGE (system:System {id: "sys_gov_service"})
SET system.project_id = "prj_20260610_gov_service",
    system.report_id = "rpt_20260610_gov_service",
    system.name = "某市政务服务平台",
    system.deployment_env = "政务云生产环境",
    system.business_domain = "政务服务",
    system.service_scope = "面向市民和政务工作人员提供在线事项申报、审批与查询服务",
    system.description = "采用互联网区、DMZ、业务区和数据库区分区部署的政务服务平台",
    system.network_architecture = "互联网访问经边界防火墙和国密 SSL VPN 进入 DMZ，再访问业务区和数据库区",
    system.is_dmz = false;

UNWIND [
  {
    id: "sys_gov_service:SecurityArea:互联网区", name: "互联网区",
    zone_type: "互联网区", security_level: "外部网络",
    boundary_description: "公众用户通过互联网访问平台"
  },
  {
    id: "sys_gov_service:SecurityArea:DMZ", name: "DMZ",
    zone_type: "DMZ", security_level: "边界接入区",
    boundary_description: "部署接入网关和 Web 服务"
  },
  {
    id: "sys_gov_service:SecurityArea:业务区", name: "业务区",
    zone_type: "业务区", security_level: "核心业务区",
    boundary_description: "部署政务服务应用"
  },
  {
    id: "sys_gov_service:SecurityArea:数据库区", name: "数据库区",
    zone_type: "数据库区", security_level: "核心数据区",
    boundary_description: "部署数据库和密码服务"
  }
] AS item
MERGE (n:Entity:SecurityArea {id: item.id})
SET n.system_id = "sys_gov_service",
    n.name = item.name,
    n.area_type = "网络安全域",
    n.zone_type = item.zone_type,
    n.security_level = item.security_level,
    n.boundary_description = item.boundary_description,
    n.protection_requirements = ["边界访问控制", "安全审计"],
    n.source_section = "2.2",
    n.confidence = 1.0;

MERGE (room:Entity:PhysicalEnvironment {id: "sys_gov_service:PhysicalEnvironment:政务云主机房"})
SET room.system_id = "sys_gov_service",
    room.name = "政务云主机房",
    room.location = "某市政务云数据中心",
    room.area = "核心机房区域",
    room.importance_level = "关键",
    room.environment_type = "机房",
    room.source_section = "2.3.1",
    room.confidence = 1.0;

MERGE (access:Entity:PhysicalSecurityFacility {id: "sys_gov_service:PhysicalSecurityFacility:机房门禁系统"})
SET access.system_id = "sys_gov_service",
    access.name = "机房门禁系统",
    access.vendor = "已脱敏",
    access.model = "已脱敏",
    access.facility_type = "门禁",
    access.authentication_method = "智能密码钥匙与人员卡双因素鉴别",
    access.retention_period = "180 天",
    access.importance_level = "重要",
    access.asset_type = "物理安防设施",
    access.quality_flags = ["PLACEHOLDER_VALUE"],
    access.source_section = "3.1.1",
    access.confidence = 0.9;

MERGE (web:Entity:Server {id: "sys_gov_service:Server:Web服务器"})
SET web.system_id = "sys_gov_service",
    web.name = "Web服务器",
    web.vendor = "已脱敏",
    web.model = "云主机",
    web.os_version = "Linux",
    web.is_virtual = true,
    web.purpose = "提供互联网 Web 接入",
    web.quantity = 2,
    web.importance_level = "重要",
    web.server_type = "Web服务器",
    web.asset_type = "服务器",
    web.source_section = "2.4.1",
    web.confidence = 1.0;

MERGE (app_server:Entity:Server {id: "sys_gov_service:Server:应用服务器"})
SET app_server.system_id = "sys_gov_service",
    app_server.name = "应用服务器",
    app_server.vendor = "已脱敏",
    app_server.model = "云主机",
    app_server.os_version = "Linux",
    app_server.is_virtual = true,
    app_server.purpose = "运行政务服务应用",
    app_server.quantity = 2,
    app_server.importance_level = "关键",
    app_server.server_type = "应用服务器",
    app_server.asset_type = "服务器",
    app_server.source_section = "2.4.1",
    app_server.confidence = 1.0;

MERGE (db_server:Entity:Server {id: "sys_gov_service:Server:数据库服务器"})
SET db_server.system_id = "sys_gov_service",
    db_server.name = "数据库服务器",
    db_server.vendor = "已脱敏",
    db_server.model = "云主机",
    db_server.os_version = "Linux",
    db_server.is_virtual = true,
    db_server.purpose = "存储业务数据和用户身份信息",
    db_server.quantity = 2,
    db_server.importance_level = "关键",
    db_server.server_type = "数据库服务器",
    db_server.asset_type = "服务器",
    db_server.source_section = "2.4.1",
    db_server.confidence = 1.0;

MERGE (firewall:Entity:NetworkDevice {id: "sys_gov_service:NetworkDevice:边界防火墙"})
SET firewall.system_id = "sys_gov_service",
    firewall.name = "边界防火墙",
    firewall.vendor = "已脱敏",
    firewall.model = "已脱敏",
    firewall.device_type = "防火墙",
    firewall.purpose = "互联网边界访问控制",
    firewall.quantity = 2,
    firewall.importance_level = "关键",
    firewall.network_layer = "边界",
    firewall.asset_type = "网络设备",
    firewall.quality_flags = ["PLACEHOLDER_VALUE"],
    firewall.source_section = "2.4.2",
    firewall.confidence = 0.9;

MERGE (gateway:Entity:CryptoProduct:NetworkDevice {id: "sys_gov_service:CryptoProduct:国密SSLVPN网关"})
SET gateway.system_id = "sys_gov_service",
    gateway.name = "国密 SSL VPN 网关",
    gateway.vendor = "已脱敏",
    gateway.model = "已脱敏",
    gateway.certificate_no = "有效商用密码产品认证证书（编号脱敏）",
    gateway.quantity = 2,
    gateway.purpose = "提供互联网访问链路的国密 SSL 加密和通信实体鉴别",
    gateway.importance_level = "关键",
    gateway.product_type = "VPN",
    gateway.product_type_code = "VPN",
    gateway.algorithm_names = ["国密SSL", "SM2", "SM3", "SM4"],
    gateway.asset_type = "密码产品",
    gateway.is_certified = true,
    gateway.device_type = "加密网关",
    gateway.network_layer = "边界",
    gateway.quality_flags = ["PLACEHOLDER_VALUE"],
    gateway.source_section = "3.2.1",
    gateway.confidence = 0.9;

MERGE (sign_server:Entity:CryptoProduct {id: "sys_gov_service:CryptoProduct:签名验签服务器"})
SET sign_server.system_id = "sys_gov_service",
    sign_server.name = "签名验签服务器",
    sign_server.vendor = "已脱敏",
    sign_server.model = "已脱敏",
    sign_server.certificate_no = "有效商用密码产品认证证书（编号脱敏）",
    sign_server.quantity = 2,
    sign_server.purpose = "为审批结果文件提供数字签名和验签服务",
    sign_server.importance_level = "关键",
    sign_server.product_type = "签名验签服务器",
    sign_server.product_type_code = "SIGNATURE_SERVER",
    sign_server.algorithm_names = ["SM2", "SM3"],
    sign_server.asset_type = "密码产品",
    sign_server.is_certified = true,
    sign_server.quality_flags = ["PLACEHOLDER_VALUE"],
    sign_server.source_section = "3.4.2",
    sign_server.confidence = 0.9;

MERGE (ukey:Entity:CryptoProduct {id: "sys_gov_service:CryptoProduct:管理员UKey"})
SET ukey.system_id = "sys_gov_service",
    ukey.name = "管理员 UKey",
    ukey.vendor = "已脱敏",
    ukey.model = "已脱敏",
    ukey.certificate_no = "有效商用密码产品认证证书（编号脱敏）",
    ukey.quantity = 12,
    ukey.purpose = "管理员身份鉴别",
    ukey.importance_level = "重要",
    ukey.product_type = "UKey",
    ukey.product_type_code = "UKEY",
    ukey.algorithm_names = ["SM2"],
    ukey.asset_type = "密码产品",
    ukey.is_certified = true,
    ukey.quality_flags = ["PLACEHOLDER_VALUE"],
    ukey.source_section = "3.3.1",
    ukey.confidence = 0.9;

MERGE (db:Entity:DatabaseSystem {id: "sys_gov_service:DatabaseSystem:政务服务业务数据库"})
SET db.system_id = "sys_gov_service",
    db.name = "政务服务业务数据库",
    db.version = "已脱敏",
    db.deploy_location = "数据库区",
    db.main_function = "存储事项申报、审批结果和用户身份信息",
    db.importance_level = "关键",
    db.architecture = "主备",
    db.asset_type = "数据库",
    db.quality_flags = ["PLACEHOLDER_VALUE"],
    db.source_section = "2.4.3",
    db.confidence = 0.9;

MERGE (application:Entity:BusinessApplication {id: "sys_gov_service:BusinessApplication:政务服务应用"})
SET application.system_id = "sys_gov_service",
    application.name = "政务服务应用",
    application.version = "V3.2",
    application.deploy_location = "业务区",
    application.main_function = "在线事项申报、审批和结果查询",
    application.business_process = "用户登录、事项申报、材料提交、审批、结果送达",
    application.importance_level = "关键",
    application.asset_type = "业务应用",
    application.source_section = "2.1",
    application.confidence = 1.0;

MERGE (identity_data:Entity:ImportantData {id: "sys_gov_service:ImportantData:用户身份鉴别数据"})
SET identity_data.system_id = "sys_gov_service",
    identity_data.name = "用户身份鉴别数据",
    identity_data.description = "用户登录凭据、认证结果和会话身份信息",
    identity_data.data_type = "身份鉴别数据",
    identity_data.data_category_code = "AUTHENTICATION_DATA",
    identity_data.business_application_id = "sys_gov_service:BusinessApplication:政务服务应用",
    identity_data.server_id = "sys_gov_service:Server:数据库服务器",
    identity_data.database_system_id = "sys_gov_service:DatabaseSystem:政务服务业务数据库",
    identity_data.storage_location = "政务服务业务数据库",
    identity_data.security_needs = ["机密性", "完整性", "真实性"],
    identity_data.importance_level = "关键",
    identity_data.asset_type = "重要数据",
    identity_data.source_section = "2.5.1",
    identity_data.confidence = 1.0;

MERGE (business_data:Entity:ImportantData {id: "sys_gov_service:ImportantData:事项申报与审批数据"})
SET business_data.system_id = "sys_gov_service",
    business_data.name = "事项申报与审批数据",
    business_data.description = "事项申报材料、审批意见和审批结果文件",
    business_data.data_type = "业务数据",
    business_data.data_category_code = "BUSINESS_DATA",
    business_data.business_application_id = "sys_gov_service:BusinessApplication:政务服务应用",
    business_data.server_id = "sys_gov_service:Server:数据库服务器",
    business_data.server_ids = ["sys_gov_service:Server:应用服务器", "sys_gov_service:Server:数据库服务器"],
    business_data.database_system_id = "sys_gov_service:DatabaseSystem:政务服务业务数据库",
    business_data.database_system_ids = ["sys_gov_service:DatabaseSystem:政务服务业务数据库"],
    business_data.storage_location = "政务服务业务数据库",
    business_data.security_needs = ["机密性", "完整性", "不可否认性"],
    business_data.importance_level = "关键",
    business_data.asset_type = "重要数据",
    business_data.source_section = "2.5.2",
    business_data.confidence = 1.0;

MERGE (log_data:Entity:ImportantData {id: "sys_gov_service:ImportantData:安全审计日志"})
SET log_data.system_id = "sys_gov_service",
    log_data.name = "安全审计日志",
    log_data.description = "系统登录、管理操作和审批操作日志",
    log_data.data_type = "日志数据",
    log_data.data_category_code = "LOG_DATA",
    log_data.business_application_id = "sys_gov_service:BusinessApplication:政务服务应用",
    log_data.server_id = "未明确",
    log_data.database_system_id = "N/A",
    log_data.storage_location = "日志存储",
    log_data.security_needs = ["完整性", "安全审计"],
    log_data.importance_level = "重要",
    log_data.asset_type = "重要数据",
    log_data.source_section = "2.5.3",
    log_data.confidence = 1.0;

MERGE (admin:Entity:Person {id: "sys_gov_service:Person:系统管理员"})
SET admin.system_id = "sys_gov_service",
    admin.name = "系统管理员（脱敏）",
    admin.role = "系统管理员",
    admin.responsibility = "负责系统日常运维和账号管理",
    admin.department = "信息中心",
    admin.source_section = "4.1",
    admin.confidence = 1.0;

MERGE (policy:Entity:ManagementDocument {id: "sys_gov_service:ManagementDocument:密码应用管理制度"})
SET policy.system_id = "sys_gov_service",
    policy.name = "密码应用管理制度",
    policy.main_content = "规定密码产品、密钥、人员和应急处置管理要求",
    policy.management_topic = "密码应用管理",
    policy.effective_status = "生效",
    policy.revision_cycle = "每年",
    policy.source_section = "4.2",
    policy.confidence = 1.0;

UNWIND [
  {
    id: "sys_gov_service:NetworkLink:互联网至DMZ国密加密链路",
    name: "互联网至 DMZ 国密加密链路", source_endpoint: "互联网区",
    target_endpoint: "DMZ", protocol: "国密 SSL", port: "443",
    link_type: "互联网", encryption_status: "已采用国密 SSL 加密"
  },
  {
    id: "sys_gov_service:NetworkLink:DMZ至业务区内部链路",
    name: "DMZ 至业务区内部链路", source_endpoint: "DMZ",
    target_endpoint: "业务区", protocol: "HTTPS", port: "8443",
    link_type: "内部网络", encryption_status: "已加密"
  }
] AS item
MERGE (n:Entity:NetworkLink {id: item.id})
SET n.system_id = "sys_gov_service",
    n.name = item.name,
    n.source_endpoint = item.source_endpoint,
    n.target_endpoint = item.target_endpoint,
    n.protocol = item.protocol,
    n.port = item.port,
    n.link_type = item.link_type,
    n.encryption_status = item.encryption_status,
    n.boundary_crossing = true,
    n.source_section = "3.2.1",
    n.confidence = 1.0;

UNWIND [
  {
    id: "sys_gov_service:CryptoApplication:互联网通信链路保护",
    name: "互联网通信链路保护", domain: "网络和通信安全",
    scenario: "公众用户访问政务服务平台",
    description: "使用国密 SSL VPN 网关对互联网访问链路进行加密并鉴别通信实体",
    mechanism: "国密 SSL、SM2、SM3、SM4",
    algorithm_names: ["国密SSL", "SM2", "SM3", "SM4"],
    compliance_statement: "通信实体身份鉴别和传输数据保护措施有效"
  },
  {
    id: "sys_gov_service:CryptoApplication:管理员身份鉴别",
    name: "管理员身份鉴别", domain: "设备和计算安全",
    scenario: "管理员登录服务器和密码产品",
    description: "管理员使用 UKey 和口令进行双因素身份鉴别",
    mechanism: "UKey、SM2 数字证书",
    algorithm_names: ["SM2"],
    compliance_statement: "关键设备管理员采用密码技术进行身份鉴别"
  },
  {
    id: "sys_gov_service:CryptoApplication:审批结果数字签名",
    name: "审批结果数字签名", domain: "应用和数据安全",
    scenario: "审批结果文件生成和验证",
    description: "调用签名验签服务器对审批结果文件进行 SM2 数字签名",
    mechanism: "SM2、SM3、签名验签服务器",
    algorithm_names: ["SM2", "SM3"],
    compliance_statement: "审批结果文件具备真实性、完整性和不可否认性保护"
  },
  {
    id: "sys_gov_service:CryptoApplication:安全审计日志完整性保护",
    name: "安全审计日志完整性保护", domain: "设备和计算安全",
    scenario: "安全审计日志存储",
    description: "当前仅依赖数据库权限控制，未使用密码技术保护日志完整性",
    mechanism: "未采用密码技术",
    algorithm_names: ["未明确"],
    compliance_statement: "未满足日志完整性密码保护要求"
  }
] AS item
MERGE (n:Entity:CryptoApplication {id: item.id})
SET n.system_id = "sys_gov_service",
    n.report_id = "rpt_20260610_gov_service",
    n.name = item.name,
    n.domain = item.domain,
    n.scenario = item.scenario,
    n.description = item.description,
    n.mechanism = item.mechanism,
    n.algorithm_names = item.algorithm_names,
    n.compliance_statement = item.compliance_statement,
    n.source_section = "3",
    n.confidence = 1.0;

MERGE (timestamp_service:Entity:CryptoService {id: "sys_gov_service:CryptoService:统一时间戳服务"})
SET timestamp_service.system_id = "sys_gov_service",
    timestamp_service.report_id = "rpt_20260610_gov_service",
    timestamp_service.name = "统一时间戳服务",
    timestamp_service.provider = "某电子认证服务机构",
    timestamp_service.service_type = "时间戳",
    timestamp_service.purpose = "为审批结果签名提供可信时间证明",
    timestamp_service.algorithm_names = ["SM2", "SM3"],
    timestamp_service.source_section = "3.4.3",
    timestamp_service.confidence = 1.0;

UNWIND [
  {
    code: "GB-T-39786-2021-7.2.1",
    name: "网络和通信安全-身份鉴别",
    domain: "网络和通信安全",
    requirement_text: "采用密码技术对通信实体进行身份鉴别",
    source_standard: "GB/T 39786-2021 信息安全技术 信息系统密码应用基本要求",
    clause_no: "7.2.1"
  },
  {
    code: "GB-T-39786-2021-7.3.4",
    name: "设备和计算安全-日志记录完整性",
    domain: "设备和计算安全",
    requirement_text: "采用密码技术保证日志记录的完整性",
    source_standard: "GB/T 39786-2021 信息安全技术 信息系统密码应用基本要求",
    clause_no: "7.3.4"
  },
  {
    code: "GB-T-39786-2021-7.4.4",
    name: "应用和数据安全-重要数据完整性",
    domain: "应用和数据安全",
    requirement_text: "采用密码技术保证重要数据在传输和存储过程中的完整性",
    source_standard: "GB/T 39786-2021 信息安全技术 信息系统密码应用基本要求",
    clause_no: "7.4.4"
  }
] AS item
MERGE (n:EvaluationCriterion {code: item.code})
SET n.name = item.name,
    n.domain = item.domain,
    n.requirement_text = item.requirement_text,
    n.source_standard = item.source_standard,
    n.clause_no = item.clause_no;

UNWIND [
  {
    id: "rpt_20260610_gov_service:ComplianceItem:NET_AUTH",
    code: "NET_AUTH", criterion_code: "GB-T-39786-2021-7.2.1",
    name: "通信实体身份鉴别检查", domain: "网络和通信安全",
    evaluation_method: "访谈、配置核查和抓包验证", result: "符合"
  },
  {
    id: "rpt_20260610_gov_service:ComplianceItem:LOG_INTEGRITY",
    code: "LOG_INTEGRITY", criterion_code: "GB-T-39786-2021-7.3.4",
    name: "日志记录完整性检查", domain: "设备和计算安全",
    evaluation_method: "访谈和配置核查", result: "不符合"
  },
  {
    id: "rpt_20260610_gov_service:ComplianceItem:DATA_INTEGRITY",
    code: "DATA_INTEGRITY", criterion_code: "GB-T-39786-2021-7.4.4",
    name: "重要数据完整性检查", domain: "应用和数据安全",
    evaluation_method: "访谈、配置核查和功能验证", result: "部分符合"
  }
] AS item
MERGE (n:Entity:ComplianceItem {id: item.id})
SET n.report_id = "rpt_20260610_gov_service",
    n.name = item.name,
    n.code = item.code,
    n.criterion_code = item.criterion_code,
    n.domain = item.domain,
    n.evaluation_method = item.evaluation_method,
    n.applicability = "适用",
    n.result = item.result,
    n.source_section = "5",
    n.confidence = 1.0;

MERGE (finding:Entity:Finding {id: "rpt_20260610_gov_service:Finding:日志完整性保护缺失"})
SET finding.report_id = "rpt_20260610_gov_service",
    finding.compliance_item_id = "rpt_20260610_gov_service:ComplianceItem:LOG_INTEGRITY",
    finding.name = "安全审计日志未采用密码技术进行完整性保护",
    finding.finding_type = "不符合项",
    finding.description = "抽查发现安全审计日志仅通过数据库权限控制防止修改，未采用 MAC 或数字签名等密码技术进行完整性保护",
    finding.severity = "中",
    finding.status = "待整改",
    finding.impact = "日志被篡改后可能无法及时发现，影响安全事件追溯",
    finding.recommendation = "采用基于 SM3 的 MAC 或数字签名机制保护日志完整性",
    finding.source_section = "5.3.4",
    finding.confidence = 1.0;

UNWIND [
  {
    id: "rpt_20260610_gov_service:Evidence:国密SSL网关配置核查",
    name: "国密 SSL 网关配置核查记录",
    compliance_item_id: "rpt_20260610_gov_service:ComplianceItem:NET_AUTH",
    finding_id: null,
    evidence_type: "配置",
    description: "核查网关启用了双向身份鉴别和国密算法套件",
    content: "启用 SM2/SM3/SM4 国密算法套件，服务端证书在有效期内"
  },
  {
    id: "rpt_20260610_gov_service:Evidence:日志完整性访谈记录",
    name: "日志完整性访谈和配置核查记录",
    compliance_item_id: "rpt_20260610_gov_service:ComplianceItem:LOG_INTEGRITY",
    finding_id: "rpt_20260610_gov_service:Finding:日志完整性保护缺失",
    evidence_type: "访谈和配置",
    description: "管理员确认日志未配置 MAC 或数字签名保护",
    content: "日志由数据库账号权限控制，未部署密码完整性校验机制"
  }
] AS item
MERGE (n:Entity:Evidence {id: item.id})
SET n.report_id = "rpt_20260610_gov_service",
    n.name = item.name,
    n.compliance_item_id = item.compliance_item_id,
    n.finding_id = item.finding_id,
    n.evidence_type = item.evidence_type,
    n.description = item.description,
    n.content = item.content,
    n.source = "现场测评",
    n.collected_at = datetime("2026-05-20T10:00:00+08:00"),
    n.confidence = 1.0;

// 明确的部署、拓扑和业务关系。
MATCH (access:PhysicalSecurityFacility {id: "sys_gov_service:PhysicalSecurityFacility:机房门禁系统"}),
      (room:PhysicalEnvironment {id: "sys_gov_service:PhysicalEnvironment:政务云主机房"})
MERGE (access)-[:DEPLOYED_IN]->(room);

MATCH (app:BusinessApplication {id: "sys_gov_service:BusinessApplication:政务服务应用"}),
      (server:Server {id: "sys_gov_service:Server:应用服务器"})
MERGE (app)-[:DEPLOYED_ON]->(server);

MATCH (db:DatabaseSystem {id: "sys_gov_service:DatabaseSystem:政务服务业务数据库"}),
      (server:Server {id: "sys_gov_service:Server:数据库服务器"})
MERGE (db)-[:DEPLOYED_ON]->(server);

MATCH (data:ImportantData), (db:DatabaseSystem {id: "sys_gov_service:DatabaseSystem:政务服务业务数据库"})
WHERE data.id IN [
  "sys_gov_service:ImportantData:用户身份鉴别数据",
  "sys_gov_service:ImportantData:事项申报与审批数据"
]
MERGE (data)-[:STORED_IN]->(db);

MATCH (data:ImportantData), (app:BusinessApplication {id: "sys_gov_service:BusinessApplication:政务服务应用"})
WHERE data.system_id = "sys_gov_service"
MERGE (data)-[:BELONGS_TO]->(app);

MATCH (link:NetworkLink {id: "sys_gov_service:NetworkLink:互联网至DMZ国密加密链路"}),
      (from:SecurityArea {id: "sys_gov_service:SecurityArea:互联网区"}),
      (to:SecurityArea {id: "sys_gov_service:SecurityArea:DMZ"})
MERGE (link)-[:FROM_AREA]->(from)
MERGE (link)-[:TO_AREA]->(to);

MATCH (link:NetworkLink {id: "sys_gov_service:NetworkLink:DMZ至业务区内部链路"}),
      (from:SecurityArea {id: "sys_gov_service:SecurityArea:DMZ"}),
      (to:SecurityArea {id: "sys_gov_service:SecurityArea:业务区"})
MERGE (link)-[:FROM_AREA]->(from)
MERGE (link)-[:TO_AREA]->(to);

MATCH (gateway:CryptoProduct {id: "sys_gov_service:CryptoProduct:国密SSLVPN网关"}),
      (dmz:SecurityArea {id: "sys_gov_service:SecurityArea:DMZ"})
MERGE (gateway)-[:PROTECTS_BOUNDARY]->(dmz);

// 密码应用和字典知识关系。
MATCH (app:CryptoApplication {id: "sys_gov_service:CryptoApplication:互联网通信链路保护"}),
      (product:CryptoProduct {id: "sys_gov_service:CryptoProduct:国密SSLVPN网关"})
MERGE (app)-[:USES_PRODUCT]->(product);

MATCH (app:CryptoApplication {id: "sys_gov_service:CryptoApplication:管理员身份鉴别"}),
      (product:CryptoProduct {id: "sys_gov_service:CryptoProduct:管理员UKey"})
MERGE (app)-[:USES_PRODUCT]->(product);

MATCH (app:CryptoApplication {id: "sys_gov_service:CryptoApplication:审批结果数字签名"}),
      (product:CryptoProduct {id: "sys_gov_service:CryptoProduct:签名验签服务器"}),
      (data:ImportantData {id: "sys_gov_service:ImportantData:事项申报与审批数据"})
MERGE (app)-[:USES_PRODUCT]->(product)
MERGE (app)-[:PROTECTS_DATA]->(data);

UNWIND [
  {app_id: "sys_gov_service:CryptoApplication:互联网通信链路保护", algorithm: "国密SSL"},
  {app_id: "sys_gov_service:CryptoApplication:互联网通信链路保护", algorithm: "SM2"},
  {app_id: "sys_gov_service:CryptoApplication:互联网通信链路保护", algorithm: "SM3"},
  {app_id: "sys_gov_service:CryptoApplication:互联网通信链路保护", algorithm: "SM4"},
  {app_id: "sys_gov_service:CryptoApplication:管理员身份鉴别", algorithm: "SM2"},
  {app_id: "sys_gov_service:CryptoApplication:审批结果数字签名", algorithm: "SM2"},
  {app_id: "sys_gov_service:CryptoApplication:审批结果数字签名", algorithm: "SM3"}
] AS item
MATCH (app:CryptoApplication {id: item.app_id})
MATCH (algorithm:CryptoAlgorithm {name: item.algorithm})
MERGE (app)-[:USES_ALGORITHM]->(algorithm);

UNWIND [
  {app_id: "sys_gov_service:CryptoApplication:互联网通信链路保护", usage: "身份鉴别"},
  {app_id: "sys_gov_service:CryptoApplication:互联网通信链路保护", usage: "传输加密"},
  {app_id: "sys_gov_service:CryptoApplication:管理员身份鉴别", usage: "身份鉴别"},
  {app_id: "sys_gov_service:CryptoApplication:审批结果数字签名", usage: "数字签名"},
  {app_id: "sys_gov_service:CryptoApplication:审批结果数字签名", usage: "完整性保护"}
] AS item
MATCH (app:CryptoApplication {id: item.app_id})
MATCH (usage:CryptoUsage {name: item.usage})
MERGE (app)-[:HAS_USAGE]->(usage);

UNWIND [
  {app_id: "sys_gov_service:CryptoApplication:互联网通信链路保护", requirement: "机密性"},
  {app_id: "sys_gov_service:CryptoApplication:互联网通信链路保护", requirement: "真实性"},
  {app_id: "sys_gov_service:CryptoApplication:管理员身份鉴别", requirement: "身份鉴别"},
  {app_id: "sys_gov_service:CryptoApplication:审批结果数字签名", requirement: "完整性"},
  {app_id: "sys_gov_service:CryptoApplication:审批结果数字签名", requirement: "不可否认性"}
] AS item
MATCH (app:CryptoApplication {id: item.app_id})
MATCH (requirement:SecurityRequirement {name: item.requirement})
MERGE (app)-[:SATISFIES]->(requirement);

// 威胁、管理和责任关系。
UNWIND [
  {threat_code: "TN2", app_id: "sys_gov_service:CryptoApplication:互联网通信链路保护"},
  {threat_code: "TA6", app_id: "sys_gov_service:CryptoApplication:审批结果数字签名"}
] AS item
MATCH (system:System {id: "sys_gov_service"})
MATCH (threat:Threat {code: item.threat_code})
MATCH (app:CryptoApplication {id: item.app_id})
MERGE (system)-[:HAS_THREAT]->(threat)
MERGE (threat)-[:MITIGATED_BY]->(app);

MATCH (system:System {id: "sys_gov_service"}),
      (threat:Threat {code: "TD5"}),
      (data:ImportantData {id: "sys_gov_service:ImportantData:安全审计日志"})
MERGE (system)-[:HAS_THREAT]->(threat)
MERGE (threat)-[:AFFECTS_DATA]->(data);

MATCH (person:Person {id: "sys_gov_service:Person:系统管理员"}),
      (system:System {id: "sys_gov_service"})
MERGE (person)-[:RESPONSIBLE_FOR]->(system);

MATCH (document:ManagementDocument {id: "sys_gov_service:ManagementDocument:密码应用管理制度"}),
      (gateway:CryptoProduct {id: "sys_gov_service:CryptoProduct:国密SSLVPN网关"})
MERGE (document)-[:REGULATES]->(gateway);

RETURN "sample_evaluation_data_loaded" AS status;
