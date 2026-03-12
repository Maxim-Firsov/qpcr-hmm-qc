from src.core.normalize import normalize_rows


def test_normalize_rows_standardizes_well_and_types():
    rows = [
        {
            "run_id": "run1",
            "plate_id": "plateA",
            "well_id": "a1",
            "sample_id": "",
            "target_id": "",
            "cycle": "1",
            "fluorescence": "0.10",
        }
    ]
    out = normalize_rows(rows)
    assert out[0]["well_id"] == "A01"
    assert out[0]["sample_id"] == "unknown_sample"
    assert out[0]["target_id"] == "unknown_target"
    assert out[0]["cycle"] == 1
    assert out[0]["fluorescence"] == 0.10


def test_normalize_rows_preserves_optional_temperature():
    rows = [
        {
            "run_id": "run1",
            "plate_id": "plateA",
            "well_id": "a1",
            "sample_id": "s1",
            "target_id": "t1",
            "cycle": "1",
            "fluorescence": "0.10",
            "temperature_c": "95.5",
            "is_melt_stage": True,
        }
    ]
    out = normalize_rows(rows)
    assert out[0]["temperature_c"] == 95.5
    assert out[0]["is_melt_stage"] is True
