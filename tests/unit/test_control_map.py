import json

from src.core.control_map import build_plate_meta, load_control_map


def test_load_control_map_reads_rule_config(tmp_path):
    config_path = tmp_path / "control_map.json"
    config_path.write_text(
        json.dumps(
            {
                "rules": [
                    {
                        "plate_id": "*",
                        "well_ids": ["H12"],
                        "control_type": "ntc",
                        "expected_target_id": "assay_a",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    config = load_control_map(config_path)
    assert len(config["rules"]) == 1
    assert config["rules"][0]["well_ids"] == ["H12"]


def test_build_plate_meta_applies_control_map_defaults():
    inferred_rows = [
        {"plate_id": "plate_1", "well_id": "A01", "target_id": "assay_a"},
        {"plate_id": "plate_1", "well_id": "H12", "target_id": "assay_a"},
    ]
    control_map = {
        "rules": [
            {
                "plate_id": "*",
                "well_ids": ["A01"],
                "control_type": "positive_control",
                "expected_target_id": "assay_a",
            },
            {
                "plate_id": "*",
                "well_ids": ["H12"],
                "control_type": "ntc",
                "expected_target_id": "assay_a",
            },
        ]
    }

    plate_meta = build_plate_meta(base_meta={}, inferred_rows=inferred_rows, control_map=control_map)

    assert plate_meta[("plate_1", "A01")]["control_type"] == "positive_control"
    assert plate_meta[("plate_1", "A01")]["expected_target_id"] == "assay_a"
    assert plate_meta[("plate_1", "H12")]["control_type"] == "ntc"
