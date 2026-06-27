"""crypto_kg —— 密评报告知识图谱抽取流水线。

流水线分层（与本体 ontology/ 对齐）：

    文档(docx/pdf/txt)
        → parsing   解析章节与表格
        → mapping   章节号/标题 → 实体类型(schema)
        → normalization  实体名归一、同义词合并、多标签
        → graph     生成符合 Neo4j 本体的实体/关系，写入或导出 Cypher
        → integration  以工具形式接入 CryptoAgent

公开的高层入口见 `crypto_kg.pipeline`。
"""

from crypto_kg.models import (
    Entity,
    ExtractionResult,
    ParsedDocument,
    Relation,
    SchemaMapping,
    Section,
    Table,
)
from crypto_kg.pipeline import extract_kg, extract_to_cypher, extract_to_dict

__all__ = [
    "Entity",
    "ExtractionResult",
    "ParsedDocument",
    "Relation",
    "SchemaMapping",
    "Section",
    "Table",
    "extract_kg",
    "extract_to_cypher",
    "extract_to_dict",
]

__version__ = "0.1.0"
