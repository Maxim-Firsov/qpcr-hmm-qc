from src.report.render import render_report


def test_render_report_has_table():
    html = render_report(
        {
            "global_counts": {"pass": 90, "review": 4, "rerun": 2},
            "plates": [
                {
                    "plate_id": "p1",
                    "well_total": 96,
                    "pass_count": 90,
                    "review_count": 4,
                    "rerun_count": 2,
                    "ntc_contamination_count": 1,
                    "replicate_discordance_count": 1,
                    "plate_status": "review",
                }
            ]
        }
    )
    assert "<table" in html
    assert "p1" in html
    assert "Overview" in html
    assert "Per-Plate Summary" in html
    assert "Rerun Rationale" in html
