"""Core data structures for report parsing and graph extraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Table:
    """A table extracted from a report section."""

    rows: list[list[str]]
    section_no: str | None = None
    section_title: str | None = None
    caption: str | None = None
    page: int | None = None

    @property
    def headers(self) -> list[str]:
        return self.rows[0] if self.rows else []

    @property
    def body_rows(self) -> list[list[str]]:
        return self.rows[1:] if len(self.rows) > 1 else []

    def to_records(self) -> list[dict[str, str]]:
        """Return table body rows as header-keyed records."""

        headers = [normalize_cell(header) for header in self.headers]
        records: list[dict[str, str]] = []
        for row in self.body_rows:
            if not any(cell.strip() for cell in row):
                continue
            record: dict[str, str] = {}
            for index, header in enumerate(headers):
                if not header:
                    continue
                record[header] = row[index].strip() if index < len(row) else ""
            records.append(record)
        return records


@dataclass(slots=True)
class Section:
    """A numbered report section with extracted text and tables."""

    section_no: str
    title: str
    level: int
    content: str = ""
    tables: list[Table] = field(default_factory=list)

    @property
    def heading(self) -> str:
        return f"{self.section_no} {self.title}".strip()


@dataclass(slots=True)
class ParsedDocument:
    """A parsed Word/PDF/text report."""

    path: Path
    sections: list[Section] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SchemaMapping:
    """Mapping result from a report section/table to an ontology entity type."""

    schema: str
    relation: str
    section_no: str | None = None
    section_title: str | None = None
    confidence: float = 1.0
    reason: str = ""
    multi_labels: tuple[str, ...] = ()


@dataclass(slots=True)
class Entity:
    """A Neo4j ontology entity extracted from a report row or text block."""

    id: str
    labels: list[str]
    name: str
    properties: dict[str, Any] = field(default_factory=dict)
    source_section: str | None = None
    source_text: str | None = None
    confidence: float = 1.0

    def all_properties(self) -> dict[str, Any]:
        data = dict(self.properties)
        data.update(
            {
                "id": self.id,
                "name": self.name,
                "confidence": self.confidence,
            }
        )
        if self.source_section:
            data["source_section"] = self.source_section
        if self.source_text:
            data["source_text"] = self.source_text
        return {key: value for key, value in data.items() if value not in (None, "", [])}


@dataclass(slots=True)
class Relation:
    """A Neo4j relationship extracted or inferred from explicit fields."""

    start_id: str
    end_id: str
    type: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExtractionResult:
    """Structured output consumed by CryptoAgent or a Neo4j writer."""

    document: ParsedDocument
    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    section_mappings: list[SchemaMapping] = field(default_factory=list)


def normalize_cell(value: Any) -> str:
    return " ".join(str(value or "").replace("\u3000", " ").split())
