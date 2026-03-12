from src.core.validate import validate_rows


def test_validate_rows_rejects_short_curves():
    rows = [
        {
            "run_id": "r1",
            "plate_id": "p1",
            "well_id": "A01",
            "sample_id": "s1",
            "target_id": "t1",
            "cycle": 1,
            "fluorescence": 0.1,
        },
        {
            "run_id": "r1",
            "plate_id": "p1",
            "well_id": "A01",
            "sample_id": "s1",
            "target_id": "t1",
            "cycle": 2,
            "fluorescence": 0.2,
        },
    ]
    eligible, rejected, summary = validate_rows(rows, min_cycles=3)
    assert len(eligible) == 0
    assert len(rejected) == 2
    assert summary["error_counts"]["min_cycles_failed"] == 2


def test_validate_rows_excludes_melt_stage_rows():
    rows = [
        {
            "run_id": "r1",
            "plate_id": "p1",
            "well_id": "A01",
            "sample_id": "s1",
            "target_id": "t1",
            "cycle": 1,
            "fluorescence": 0.1,
            "temperature_c": 95.0,
            "is_melt_stage": True,
        },
        {
            "run_id": "r1",
            "plate_id": "p1",
            "well_id": "A01",
            "sample_id": "s1",
            "target_id": "t1",
            "cycle": 2,
            "fluorescence": 0.2,
            "temperature_c": 95.0,
            "is_melt_stage": True,
        },
    ]
    eligible, rejected, summary = validate_rows(rows, min_cycles=1)
    assert len(eligible) == 0
    assert len(rejected) == 2
    assert summary["error_counts"]["melt_stage_excluded"] == 2
