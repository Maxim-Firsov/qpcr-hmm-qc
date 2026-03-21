"""Workflow configuration helpers."""

from __future__ import annotations

import json
from pathlib import Path


def _coerce_scalar(value: str):
    text = value.strip()
    if not text:
        return ""
    if text[0] == text[-1] and text[0] in {'"', "'"}:
        return text[1:-1]
    lowered = text.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


def _parse_simple_yaml(text: str) -> dict:
    payload: dict[str, object] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError("Only simple top-level 'key: value' YAML mappings are supported for workflow config.")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError("Workflow config contains an empty key.")
        payload[key] = _coerce_scalar(raw_value)
    return payload


def load_mapping(path: str | Path | None) -> dict:
    if not path:
        return {}
    text = Path(path).read_text(encoding="utf-8-sig")
    stripped = text.strip()
    if not stripped:
        return {}
    if stripped.startswith("{"):
        payload = json.loads(stripped)
    else:
        payload = _parse_simple_yaml(text)
    if not isinstance(payload, dict):
        raise ValueError(f"Workflow config at {path} must contain a mapping/object at the top level.")
    return payload
