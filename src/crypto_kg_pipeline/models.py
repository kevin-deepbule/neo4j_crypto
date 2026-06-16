from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SourceRef:
    section: str
    table_name: str
    row_index: int
    column_name: Optional[str] = None
    source_text: Optional[str] = None


@dataclass
class RawTableRow:
    schema_id: str
    section: str
    table_name: str
    row_index: int
    cells: Dict[str, Any]


@dataclass
class ExtractedRecord:
    schema_id: str
    entity_type: str
    source_ref: SourceRef
    fields: Dict[str, Any]
    missing_fields: List[str] = field(default_factory=list)
    quality_flags: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class Entity:
    id: str
    labels: List[str]
    primary_label: str
    name: str
    properties: Dict[str, Any]
    source_refs: List[SourceRef] = field(default_factory=list)
    quality_flags: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class Relationship:
    start_id: str
    rel_type: str
    end_id: Optional[str] = None
    end_lookup: Optional[Dict[str, str]] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    source_refs: List[SourceRef] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class DetectionIssue:
    issue_type: str
    severity: str
    message: str
    entity_id: Optional[str] = None
    field_name: Optional[str] = None
    source_refs: List[SourceRef] = field(default_factory=list)
    detail: Dict[str, Any] = field(default_factory=dict)


def to_jsonable(obj: Any) -> Any:
    if isinstance(obj, list):
        return [to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if hasattr(obj, "__dataclass_fields__"):
        return to_jsonable(asdict(obj))
    return obj
