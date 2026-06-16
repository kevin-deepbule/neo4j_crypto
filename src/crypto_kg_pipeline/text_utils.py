from __future__ import annotations

import re
from typing import Any, Iterable, List

_PLACEHOLDER_VALUES = {
    "", "-", "—", "--", "/", "无", "暂无", "无相关", "不涉及", "未提供",
    "未明确", "不明确", "未知", "待补充", "见附件", "详见附件", "nan", "none", "null"
}

_ALGO_PATTERN = re.compile(r"SM[2349]|RSA|AES|DES|3DES|SHA-?\d*|HMAC|ECC|ECDSA|国密", re.I)
_IP_PATTERN = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
_PHONE_PATTERN = re.compile(r"(?<!\d)(?:1[3-9]\d{9}|0\d{2,3}-?\d{7,8})(?!\d)")
_EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def norm_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("：", ":").replace("，", ",").replace("；", ";")
    return text.strip()


def is_placeholder(value: Any) -> bool:
    return norm_text(value).lower() in _PLACEHOLDER_VALUES


def split_multi(value: Any) -> List[str]:
    text = norm_text(value)
    if not text or is_placeholder(text):
        return []
    parts = re.split(r"[、,，;；/\n]+", text)
    return [p.strip() for p in parts if p.strip() and not is_placeholder(p)]


def normalize_name(value: Any) -> str:
    text = norm_text(value).lower()
    text = re.sub(r"[\s\-_（）()【】\[\]<>《》:：]+", "", text)
    return text


def build_instance_id(system_id: str, entity_type: str, name: str) -> str:
    return f"{normalize_name(system_id)}:{snake(entity_type)}:{normalize_name(name)}"


def snake(value: str) -> str:
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return value.lower()


def contains_algorithm(value: Any) -> bool:
    return bool(_ALGO_PATTERN.search(norm_text(value)))


def contains_ip(value: Any) -> bool:
    return bool(_IP_PATTERN.search(norm_text(value)))


def contains_phone(value: Any) -> bool:
    return bool(_PHONE_PATTERN.search(norm_text(value)))


def contains_email(value: Any) -> bool:
    return bool(_EMAIL_PATTERN.search(norm_text(value)))


def extract_algorithms(value: Any) -> List[str]:
    text = norm_text(value)
    if not text:
        return []
    found = []
    for item in split_multi(text):
        matches = _ALGO_PATTERN.findall(item)
        if matches:
            # Preserve common written form when possible.
            found.extend([m.upper().replace("SHA-", "SHA") for m in matches])
    return dedupe(found)


def dedupe(values: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for value in values:
        key = normalize_name(value)
        if key and key not in seen:
            seen.add(key)
            out.append(value)
    return out
