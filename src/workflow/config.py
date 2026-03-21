"""Workflow configuration helpers."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_mapping(path: str | Path | None) -> dict:
    if not path:
        return {}
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Workflow config at {path} must contain a mapping/object at the top level.")
    return payload
