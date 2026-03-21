from src.workflow.planning import planned_run_ids


def test_planned_run_ids_accepts_utf8_bom_manifest(tmp_path):
    manifest = tmp_path / "manifest_bom.tsv"
    manifest.write_text(
        "run_id\tinput_mode\tinput_path\n"
        "batch_run_a\tcurve_csv\tcurves.csv\n",
        encoding="utf-8-sig",
    )

    assert planned_run_ids(manifest) == ["batch_run_a"]


def test_planned_run_ids_replaces_invalid_path_like_ids(tmp_path):
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text(
        "run_id\tinput_mode\tinput_path\n"
        "bad/run\tcurve_csv\tcurves.csv\n"
        "good_run\tcurve_csv\tcurves.csv\n"
        "bad:run\tcurve_csv\tcurves.csv\n",
        encoding="utf-8",
    )

    assert planned_run_ids(manifest) == ["manifest_row_001", "good_run", "manifest_row_003"]
