from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from .models import Entity, ExtractedRecord, Relationship, SourceRef
from .schemas import get_schema
from .text_utils import build_instance_id, dedupe, extract_algorithms, normalize_name, norm_text, split_multi


class EntityBuilder:
    """Requirement 8: build canonical entities and deterministic relationships."""

    def __init__(self, system_id: str):
        self.system_id = system_id

    def build(self, records: List[ExtractedRecord]) -> Tuple[List[Entity], List[Relationship]]:
        entities_by_id: Dict[str, Entity] = {}
        relationships: List[Relationship] = []

        for record in records:
            name = norm_text(record.fields.get("name"))
            if not name:
                continue
            entity = self._record_to_entity(record, name)
            entities_by_id[entity.id] = self._merge_entity(entities_by_id.get(entity.id), entity)

        for record in records:
            name = norm_text(record.fields.get("name"))
            if not name:
                continue
            start_id = build_instance_id(self.system_id, record.entity_type, name)
            relationships.extend(self._build_relations_for_record(record, start_id, entities_by_id))

        return list(entities_by_id.values()), self._dedupe_relationships(relationships)

    def _record_to_entity(self, record: ExtractedRecord, name: str) -> Entity:
        entity_id = build_instance_id(self.system_id, record.entity_type, name)
        props = {
            k: v for k, v in record.fields.items()
            if not k.startswith("_") and k not in {"name"}
        }
        props.update({
            "system_id": self.system_id,
            "name": name,
            "source_section": record.source_ref.section,
            "confidence": record.confidence,
        })
        return Entity(
            id=entity_id,
            labels=["Entity", record.entity_type],
            primary_label=record.entity_type,
            name=name,
            properties=props,
            source_refs=[record.source_ref],
            quality_flags=record.quality_flags[:],
            confidence=record.confidence,
        )

    def _merge_entity(self, old: Entity | None, new: Entity) -> Entity:
        if old is None:
            return new
        old.labels = dedupe(old.labels + new.labels)
        old.source_refs.extend(new.source_refs)
        old.quality_flags = sorted(set(old.quality_flags + new.quality_flags))
        old.confidence = round(max(old.confidence, new.confidence), 3)
        for key, value in new.properties.items():
            if key not in old.properties or old.properties[key] in (None, "", []):
                old.properties[key] = value
            elif old.properties[key] != value:
                # Do not overwrite conflicting values. Keep alternatives for detector/auditor.
                conflict_key = f"_conflict_{key}"
                old.properties.setdefault(conflict_key, [])
                if value not in old.properties[conflict_key]:
                    old.properties[conflict_key].append(value)
        return old

    def _build_relations_for_record(
        self,
        record: ExtractedRecord,
        start_id: str,
        entities_by_id: Dict[str, Entity],
    ) -> List[Relationship]:
        spec = get_schema(record.schema_id)
        rels: List[Relationship] = []
        for field_name, rel_type in spec.relation_fields.items():
            value = record.fields.get(field_name)
            if not value:
                continue
            values = value if isinstance(value, list) else split_multi(value)
            if not values:
                values = [norm_text(value)]

            for item in values:
                item = norm_text(item)
                if not item:
                    continue
                rel = self._relation_from_field(record, start_id, field_name, rel_type, item)
                rels.append(rel)
        return rels

    def _relation_from_field(
        self,
        record: ExtractedRecord,
        start_id: str,
        field_name: str,
        rel_type: str,
        value: str,
    ) -> Relationship:
        if field_name == "algorithms":
            algos = extract_algorithms(value) or [value]
            # If a cell has multiple algorithms, caller already split once; create first here.
            value = algos[0]
            return Relationship(
                start_id=start_id,
                rel_type=rel_type,
                end_lookup={"label": "CryptoAlgorithm", "key": "name", "value": value},
                properties={"source_section": record.source_ref.section},
                source_refs=[record.source_ref],
                confidence=record.confidence,
            )
        if field_name == "security_requirement":
            return Relationship(
                start_id=start_id,
                rel_type=rel_type,
                end_lookup={"label": "SecurityRequirement", "key": "name", "value": value},
                properties={"source_section": record.source_ref.section},
                source_refs=[record.source_ref],
                confidence=record.confidence,
            )
        if field_name == "product_name":
            end_id = build_instance_id(self.system_id, "CryptoProduct", value)
        elif field_name == "data_asset":
            end_id = build_instance_id(self.system_id, "DataAsset", value)
        elif field_name == "stored_on":
            end_id = build_instance_id(self.system_id, "ServerDevice", value)
        else:
            end_id = build_instance_id(self.system_id, "Entity", value)

        return Relationship(
            start_id=start_id,
            rel_type=rel_type,
            end_id=end_id,
            properties={"source_section": record.source_ref.section},
            source_refs=[record.source_ref],
            confidence=record.confidence,
        )

    @staticmethod
    def _dedupe_relationships(rels: Iterable[Relationship]) -> List[Relationship]:
        result: Dict[Tuple[str, str, str], Relationship] = {}
        for rel in rels:
            end_key = rel.end_id or str(rel.end_lookup)
            key = (rel.start_id, rel.rel_type, end_key)
            if key not in result:
                result[key] = rel
            else:
                result[key].source_refs.extend(rel.source_refs)
                result[key].confidence = max(result[key].confidence, rel.confidence)
        return list(result.values())
