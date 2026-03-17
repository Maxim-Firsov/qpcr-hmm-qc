from src.core.melt_qc import analyze_melt_curves


def test_analyze_melt_curves_detects_multiple_peaks():
    rows = [
        {"run_id": "r1", "plate_id": "p1", "well_id": "A01", "target_id": "t1", "temperature_c": 78.0, "fluorescence": 0.10, "is_melt_stage": True},
        {"run_id": "r1", "plate_id": "p1", "well_id": "A01", "target_id": "t1", "temperature_c": 79.0, "fluorescence": 0.25, "is_melt_stage": True},
        {"run_id": "r1", "plate_id": "p1", "well_id": "A01", "target_id": "t1", "temperature_c": 80.0, "fluorescence": 0.12, "is_melt_stage": True},
        {"run_id": "r1", "plate_id": "p1", "well_id": "A01", "target_id": "t1", "temperature_c": 81.0, "fluorescence": 0.28, "is_melt_stage": True},
        {"run_id": "r1", "plate_id": "p1", "well_id": "A01", "target_id": "t1", "temperature_c": 82.0, "fluorescence": 0.11, "is_melt_stage": True},
    ]

    summary = analyze_melt_curves(rows)

    assert summary[("p1", "A01", "t1")]["peak_count"] == 2
    assert summary[("p1", "A01", "t1")]["status"] == "review"


def test_analyze_melt_curves_flags_low_resolution_trace():
    rows = [
        {"run_id": "r1", "plate_id": "p1", "well_id": "B01", "target_id": "t1", "temperature_c": 80.0, "fluorescence": 0.10, "is_melt_stage": True},
        {"run_id": "r1", "plate_id": "p1", "well_id": "B01", "target_id": "t1", "temperature_c": 80.5, "fluorescence": 0.30, "is_melt_stage": True},
        {"run_id": "r1", "plate_id": "p1", "well_id": "B01", "target_id": "t1", "temperature_c": 81.0, "fluorescence": 0.12, "is_melt_stage": True},
    ]

    summary = analyze_melt_curves(rows)

    assert summary[("p1", "B01", "t1")]["temperature_span"] == 1.0
    assert "low_resolution" in summary[("p1", "B01", "t1")]["issues"]
