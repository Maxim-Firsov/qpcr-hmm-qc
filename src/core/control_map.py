"""Config-driven control map helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.core.normalize import normalize_well_id


def load_control_map(path: str | Path) -> dict:
    config_path = Path(path)
    text = config_path.read_text(encoding="utf-8")
    config = json.loads(text)
    config["_path"] = str(config_path)
    config["_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return config


def _rule_matches(rule: dict, plate_id: str, well_id: str, target_id: str) -> bool:
    plate_rule = str(rule.get("plate_id", "*"))
    target_rule = str(rule.get("target_id", "*"))
    well_ids = [normalize_well_id(str(value)) for value in rule.get("well_ids", [])]

    return (
        (plate_rule == "*" or plate_rule == plate_id)
        and (target_rule == "*" or target_rule == target_id)
        and normalize_well_id(well_id) in well_ids
    )


def build_plate_meta(
    base_meta: dict[tuple[str, str], dict],
    inferred_rows: list[dict],
    control_map: dict | None,
) -> dict[tuple[str, str], dict]:
    merged = {(plate_id, well_id): dict(meta) for (plate_id, well_id), meta in base_meta.items()}
    if not control_map:
        return merged

    rules = list(control_map.get("rules", []))
    for row in inferred_rows:
        plate_id = str(row["plate_id"])
        well_id = normalize_well_id(str(row["well_id"]))
        target_id = str(row.get("target_id", ""))
        metadata = merged.setdefault((plate_id, well_id), {"plate_id": plate_id, "well_id": well_id})
        for rule in rules:
            if not _rule_matches(rule, plate_id=plate_id, well_id=well_id, target_id=target_id):
                continue
            for key in ["control_type", "expected_target_id", "replicate_group", "sample_group"]:
                if key in rule and not metadata.get(key):
                    metadata[key] = rule[key]
    return merged
