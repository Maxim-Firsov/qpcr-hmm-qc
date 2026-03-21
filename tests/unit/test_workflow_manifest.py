import pytest

from pathlib import Path

from src.workflow.manifest import validate_manifest, validate_manifest_report


def test_validate_manifest_normalizes_paths_and_run_dirs(tmp_path):
    curve_csv = tmp_path / "curves.csv"
    curve_csv.write_text(
        "run_id,plate_id,well_id,sample_id,target_id,cycle,fluorescence\n"
        "r1,p1,A1,s1,t1,1,0.1\n"
        "r1,p1,A1,s1,t1,2,0.2\n"
        "r1,p1,A1,s1,t1,3,0.8\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text(
        "run_id\tinput_mode\tinput_path\tmin_cycles\tplate_schema\tallow_empty_run\n"
        "batch_run_a\tcurve_csv\tcurves.csv\t3\t96\tfalse\n",
        encoding="utf-8",
    )

    payload = validate_manifest(manifest, tmp_path / "batch_out", artifact_profile="review")

    assert payload["artifact_profile"] == "review"
    assert payload["validation_status"] == "valid"
    assert payload["run_count"] == 1
    assert payload["rows"][0]["input_path"] == str(curve_csv.resolve())
    assert Path(payload["rows"][0]["run_dir"]).parts[-3:] == ("batch_out", "runs", "batch_run_a")


def test_validate_manifest_rejects_duplicate_run_ids(tmp_path):
    curve_csv = tmp_path / "curves.csv"
    curve_csv.write_text(
        "run_id,plate_id,well_id,sample_id,target_id,cycle,fluorescence\n"
        "r1,p1,A1,s1,t1,1,0.1\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text(
        "run_id\tinput_mode\tinput_path\n"
        "dup\tcurve_csv\tcurves.csv\n"
        "dup\tcurve_csv\tcurves.csv\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="reuses run_id"):
        validate_manifest(manifest, tmp_path / "batch_out")


def test_validate_manifest_report_captures_invalid_manifest_errors(tmp_path):
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text(
        "run_id\tinput_mode\tinput_path\n"
        "missing_input\tcurve_csv\tmissing.csv\n",
        encoding="utf-8",
    )

    payload = validate_manifest_report(manifest, tmp_path / "batch_out")

    assert payload["validation_status"] == "invalid"
    assert payload["run_count"] == 0
    assert payload["errors"]


def test_validate_manifest_accepts_utf8_bom_manifest(tmp_path):
    curve_csv = tmp_path / "curves.csv"
    curve_csv.write_text(
        "run_id,plate_id,well_id,sample_id,target_id,cycle,fluorescence\n"
        "r1,p1,A1,s1,t1,1,0.1\n"
        "r1,p1,A1,s1,t1,2,0.2\n"
        "r1,p1,A1,s1,t1,3,0.8\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest_bom.tsv"
    manifest.write_text(
        "run_id\tinput_mode\tinput_path\n"
        "batch_run_a\tcurve_csv\tcurves.csv\n",
        encoding="utf-8-sig",
    )

    payload = validate_manifest(manifest, tmp_path / "batch_out")

    assert payload["validation_status"] == "valid"
    assert payload["rows"][0]["run_id"] == "batch_run_a"
