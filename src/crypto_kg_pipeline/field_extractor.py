from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .models import ExtractedRecord, RawTableRow, SourceRef
from .schemas import get_schema
from .text_utils import is_placeholder, norm_text, split_multi


class FieldExtractor:
    """Requirement 7: convert one normalized table row into a structured record."""

    def extract_row(self, row: RawTableRow) -> ExtractedRecord:
        spec = get_schema(row.schema_id)
        normalized_cells = {norm_text(k): v for k, v in row.cells.items()}
        fields: Dict[str, Any] = {}
        missing: List[str] = []
        flags: List[str] = []

        for field_name, aliases in spec.aliases.items():
            raw_value, matched_column = self._find_value(normalized_cells, aliases)
            if raw_value is None or is_placeholder(raw_value):
                if field_name in spec.required_fields:
                    missing.append(field_name)
                    flags.append(f"missing_required:{field_name}")
                continue
            if field_name in spec.list_fields:
                fields[field_name] = split_multi(raw_value)
            else:
                fields[field_name] = norm_text(raw_value)

        # Keep unmapped cells for audit and later manual schema improvement.
        mapped_aliases = {alias for aliases in spec.aliases.values() for alias in aliases}
        unmapped = {
            col: norm_text(val)
            for col, val in normalized_cells.items()
            if col not in mapped_aliases and not is_placeholder(val)
        }
        if unmapped:
            fields["_unmapped_cells"] = unmapped
            flags.append("has_unmapped_cells")

        confidence = 1.0 - min(0.5, 0.1 * len(missing))
        if "name" not in fields:
            confidence = min(confidence, 0.4)

        return ExtractedRecord(
            schema_id=row.schema_id,
            entity_type=spec.entity_type,
            source_ref=SourceRef(
                section=row.section,
                table_name=row.table_name,
                row_index=row.row_index,
                source_text=str(row.cells),
            ),
            fields=fields,
            missing_fields=missing,
            quality_flags=sorted(set(flags)),
            confidence=round(confidence, 3),
        )

    def extract_rows(self, rows: List[RawTableRow]) -> List[ExtractedRecord]:
        return [self.extract_row(row) for row in rows]

    @staticmethod
    def _find_value(cells: Dict[str, Any], aliases: List[str]) -> Tuple[Any, str | None]:
        alias_set = {norm_text(alias) for alias in aliases}
        for column, value in cells.items():
            if column in alias_set:
                return value, column
        # Fuzzy containment for columns like "密码产品名称（如有）".
        for column, value in cells.items():
            if any(alias and alias in column for alias in alias_set):
                return value, column
        return None, None
