from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Set

from .models import DetectionIssue, Entity, ExtractedRecord, Relationship, SourceRef
from .text_utils import (
    contains_algorithm,
    contains_email,
    contains_ip,
    contains_phone,
    is_placeholder,
    normalize_name,
    norm_text,
)


class ContradictionDetector:
    """Requirement 11: detect duplicate, misplaced, inconsistent and abnormal content."""

    def detect(
        self,
        records: List[ExtractedRecord],
        entities: List[Entity],
        relationships: List[Relationship],
    ) -> List[DetectionIssue]:
        issues: List[DetectionIssue] = []
        issues.extend(self._detect_record_abnormal_text(records))
        issues.extend(self._detect_field_misalignment(records))
        issues.extend(self._detect_same_person_conflicts(entities))
        issues.extend(self._detect_cross_type_duplicates(entities))
        issues.extend(self._detect_missing_relation_targets(entities, relationships))
        issues.extend(self._detect_entity_property_conflicts(entities))
        return issues

    def _detect_record_abnormal_text(self, records: List[ExtractedRecord]) -> List[DetectionIssue]:
        issues: List[DetectionIssue] = []
        for record in records:
            for field, value in record.fields.items():
                if field.startswith("_"):
                    continue
                values = value if isinstance(value, list) else [value]
                for item in values:
                    text = norm_text(item)
                    if is_placeholder(text):
                        issues.append(DetectionIssue(
                            issue_type="placeholder_value",
                            severity="warning",
                            message=f"字段 {field} 使用了占位或不明确取值：{text}",
                            field_name=field,
                            source_refs=[record.source_ref],
                            detail={"value": text},
                        ))
                    if len(text) > 120:
                        issues.append(DetectionIssue(
                            issue_type="abnormal_long_text",
                            severity="warning",
                            message=f"字段 {field} 文本过长，可能是表格串行或字段错位",
                            field_name=field,
                            source_refs=[record.source_ref],
                            detail={"value_preview": text[:120]},
                        ))
                    if "|" in text or "\t" in text:
                        issues.append(DetectionIssue(
                            issue_type="table_artifact_text",
                            severity="warning",
                            message=f"字段 {field} 含有疑似表格残留符号",
                            field_name=field,
                            source_refs=[record.source_ref],
                            detail={"value": text},
                        ))
        return issues

    def _detect_field_misalignment(self, records: List[ExtractedRecord]) -> List[DetectionIssue]:
        issues: List[DetectionIssue] = []
        for record in records:
            fields = record.fields
            # Phone/email/IP appear in non-corresponding descriptive fields.
            for field, value in fields.items():
                if field.startswith("_"):
                    continue
                text = norm_text(value)
                if field not in {"phone"} and contains_phone(text):
                    issues.append(self._misplaced(record, field, text, "手机号/电话疑似落入错误字段"))
                if field not in {"email"} and contains_email(text):
                    issues.append(self._misplaced(record, field, text, "邮箱疑似落入错误字段"))
                if field not in {"ip_address", "stored_on"} and contains_ip(text):
                    issues.append(self._misplaced(record, field, text, "IP 地址疑似落入错误字段"))

            if record.entity_type == "CryptoProduct":
                name = norm_text(fields.get("name"))
                if name and contains_algorithm(name) and len(name) <= 8:
                    issues.append(self._misplaced(record, "name", name, "产品名称疑似填写成了算法名称"))
            if record.entity_type == "Person":
                dept = norm_text(fields.get("department"))
                if contains_phone(dept) or contains_email(dept) or contains_ip(dept):
                    issues.append(self._misplaced(record, "department", dept, "部门字段疑似包含联系方式或地址"))
        return issues

    @staticmethod
    def _misplaced(record: ExtractedRecord, field: str, value: str, message: str) -> DetectionIssue:
        return DetectionIssue(
            issue_type="field_misalignment",
            severity="error",
            message=message,
            field_name=field,
            source_refs=[record.source_ref],
            detail={"value": value, "schema_id": record.schema_id},
        )

    def _detect_same_person_conflicts(self, entities: List[Entity]) -> List[DetectionIssue]:
        people = [e for e in entities if e.primary_label == "Person"]
        grouped: Dict[str, List[Entity]] = defaultdict(list)
        for person in people:
            grouped[normalize_name(person.name)].append(person)

        issues: List[DetectionIssue] = []
        for _, group in grouped.items():
            if not group:
                continue
            merged_values: Dict[str, Set[str]] = defaultdict(set)
            refs: List[SourceRef] = []
            entity_id = group[0].id
            for person in group:
                refs.extend(person.source_refs)
                for field in ["department", "role", "phone", "email"]:
                    value = norm_text(person.properties.get(field))
                    conflict_values = person.properties.get(f"_conflict_{field}", [])
                    if value:
                        merged_values[field].add(value)
                    for cv in conflict_values:
                        if norm_text(cv):
                            merged_values[field].add(norm_text(cv))
            for field, values in merged_values.items():
                if len(values) > 1:
                    issues.append(DetectionIssue(
                        issue_type="same_person_field_conflict",
                        severity="error",
                        message=f"同名人员字段 {field} 存在不一致取值：{sorted(values)}",
                        entity_id=entity_id,
                        field_name=field,
                        source_refs=refs,
                        detail={"values": sorted(values)},
                    ))
        return issues

    def _detect_cross_type_duplicates(self, entities: List[Entity]) -> List[DetectionIssue]:
        by_name: Dict[str, List[Entity]] = defaultdict(list)
        for entity in entities:
            by_name[normalize_name(entity.name)].append(entity)
        issues: List[DetectionIssue] = []
        for _, group in by_name.items():
            labels = {e.primary_label for e in group}
            if len(group) > 1 and len(labels) > 1:
                refs = []
                for entity in group:
                    refs.extend(entity.source_refs)
                issues.append(DetectionIssue(
                    issue_type="cross_table_duplicate_name",
                    severity="warning",
                    message=f"同名对象出现在多个实体类型中：{sorted(labels)}，需要确认是多标签实体还是误抽取",
                    entity_id=group[0].id,
                    source_refs=refs,
                    detail={"entity_ids": [e.id for e in group], "labels": sorted(labels)},
                ))
        return issues

    def _detect_missing_relation_targets(
        self,
        entities: List[Entity],
        relationships: List[Relationship],
    ) -> List[DetectionIssue]:
        existing_ids = {e.id for e in entities}
        issues: List[DetectionIssue] = []
        for rel in relationships:
            if rel.end_id and rel.end_id not in existing_ids:
                issues.append(DetectionIssue(
                    issue_type="missing_relation_target",
                    severity="warning",
                    message=f"关系 {rel.rel_type} 指向的实例节点不存在：{rel.end_id}",
                    entity_id=rel.start_id,
                    source_refs=rel.source_refs,
                    detail={"rel_type": rel.rel_type, "end_id": rel.end_id},
                ))
        return issues

    def _detect_entity_property_conflicts(self, entities: List[Entity]) -> List[DetectionIssue]:
        issues: List[DetectionIssue] = []
        for entity in entities:
            for key, value in entity.properties.items():
                if key.startswith("_conflict_") and value:
                    field = key.replace("_conflict_", "", 1)
                    base = entity.properties.get(field)
                    values = [base] + list(value)
                    issues.append(DetectionIssue(
                        issue_type="entity_property_conflict",
                        severity="error",
                        message=f"实体 {entity.name} 的字段 {field} 存在多个冲突取值",
                        entity_id=entity.id,
                        field_name=field,
                        source_refs=entity.source_refs,
                        detail={"values": values},
                    ))
        return issues
