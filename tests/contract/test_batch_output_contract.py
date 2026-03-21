import csv
import json

from src.export.writers import write_csv, write_json
from src.workflow.aggregate_batch import aggregate_batch, write_batch_outputs


def _read_header(path, delimiter=","):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter=delimiter))


def _build_batch_fixture(tmp_path):
    batch_root = tmp_path / "batch_out"
    run_a = batch_root / "runs" / "run_a"
    run_b = batch_root / "runs" / "run_b"
    run_a.mkdir(parents=True)
    run_b.mkdir(parents=True)

    validated_manifest = {
        "schema_version": "v0.1.0",
        "validation_status": "valid",
        "errors": [],
        "manifest_path": str(tmp_path / "manifest.tsv"),
        "manifest_sha256": "abc123",
        "artifact_profile": "review",
        "batch_id": "batch_out",
        "output_root": str(batch_root),
        "rows_dir": str(batch_root / "_workflow" / "run_rows"),
        "run_count": 2,
        "manifest_columns": ["run_id", "input_mode", "input_path"],
        "rows": [
            {"run_id": "run_a", "run_dir": str(run_a)},
            {"run_id": "run_b", "run_dir": str(run_b)},
        ],
    }
    write_json(tmp_path / "validated_manifest.json", validated_manifest)
    write_json(
        run_a / "summary.json",
        {
            "run_id": "run_a",
            "run_status": "pass",
            "execution_status": "succeeded",
            "plate_count": 1,
            "pass_count": 2,
            "review_count": 0,
            "rerun_count": 0,
            "rerun_well_count": 0,
            "warning_count": 0,
            "artifact_inventory": {"summary.json": {"generated": True, "reason": "always_on", "path": str(run_a / "summary.json")}},
            "status_reason_counts": [],
        },
    )
    write_json(run_a / "workflow_status.json", {"run_id": "run_a", "execution_status": "succeeded"})
    write_csv(
        run_a / "rerun_manifest.csv",
        [],
        ["plate_id", "well_id", "target_id", "sample_id", "rerun_reason", "evidence_score", "recommended_action"],
    )
    write_json(
        run_b / "summary.json",
        {
            "run_id": "run_b",
            "run_status": "rerun",
            "execution_status": "succeeded",
            "plate_count": 1,
            "pass_count": 0,
            "review_count": 1,
            "rerun_count": 1,
            "rerun_well_count": 1,
            "warning_count": 1,
            "artifact_inventory": {"summary.json": {"generated": True, "reason": "always_on", "path": str(run_b / "summary.json")}},
            "status_reason_counts": [{"reason": "ntc_contamination", "review_count": 0, "rerun_count": 1, "well_count": 1}],
        },
    )
    write_json(run_b / "workflow_status.json", {"run_id": "run_b", "execution_status": "succeeded"})
    write_csv(
        run_b / "rerun_manifest.csv",
        [
            {
                "plate_id": "p1",
                "well_id": "A01",
                "target_id": "t1",
                "sample_id": "s1",
                "rerun_reason": "ntc_contamination",
                "evidence_score": "0.95",
                "recommended_action": "repeat_well_qpcr",
            }
        ],
        ["plate_id", "well_id", "target_id", "sample_id", "rerun_reason", "evidence_score", "recommended_action"],
    )
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        "max_failed_runs_for_release: 0\n"
        "max_rerun_wells_for_release: 0\n"
        "max_review_wells_for_release: 0\n"
        "max_review_runs_for_release: 0\n",
        encoding="utf-8",
    )
    aggregated = aggregate_batch(tmp_path / "validated_manifest.json", config_path=policy)
    write_batch_outputs(aggregated, batch_root)
    return batch_root


def test_batch_output_contract_required_columns_and_keys(tmp_path):
    batch_root = _build_batch_fixture(tmp_path)

    batch_master = json.loads((batch_root / "batch_master.json").read_text(encoding="utf-8"))
    for key in [
        "schema_version",
        "generated_at_utc",
        "batch_id",
        "manifest_path",
        "manifest_sha256",
        "workflow_version",
        "artifact_profile",
        "run_count",
        "release_status",
        "global_counts",
        "failure_reason_totals",
        "runs",
    ]:
        assert key in batch_master

    batch_gate = json.loads((batch_root / "batch_gate_status.json").read_text(encoding="utf-8"))
    for key in [
        "schema_version",
        "generated_at_utc",
        "batch_id",
        "release_status",
        "blocking_reasons",
        "review_reasons",
        "policy_thresholds",
        "counts",
    ]:
        assert key in batch_gate

    assert _read_header(batch_root / "batch_master.tsv", delimiter="\t") == [
        "batch_id",
        "run_id",
        "execution_status",
        "run_status",
        "plate_count",
        "pass_count",
        "review_count",
        "rerun_count",
        "rerun_well_count",
        "warning_count",
        "artifact_dir",
    ]
    assert _read_header(batch_root / "rerun_queue.csv") == [
        "batch_id",
        "run_id",
        "plate_id",
        "well_id",
        "target_id",
        "sample_id",
        "rerun_reason",
        "evidence_score",
        "recommended_action",
    ]
    assert _read_header(batch_root / "failure_reason_counts.tsv", delimiter="\t") == [
        "batch_id",
        "failure_reason",
        "run_count",
        "well_count",
    ]


def test_batch_output_schema_compatibility(tmp_path):
    batch_root = _build_batch_fixture(tmp_path)

    batch_master = json.loads((batch_root / "batch_master.json").read_text(encoding="utf-8"))
    assert sorted(batch_master.keys()) == [
        "artifact_profile",
        "batch_id",
        "failure_reason_totals",
        "generated_at_utc",
        "global_counts",
        "manifest_path",
        "manifest_sha256",
        "release_status",
        "run_count",
        "runs",
        "schema_version",
        "workflow_version",
    ]
    assert sorted(batch_master["runs"][0].keys()) == [
        "artifact_dir",
        "artifact_inventory",
        "execution_status",
        "pass_count",
        "plate_count",
        "rerun_count",
        "rerun_well_count",
        "review_count",
        "run_id",
        "run_status",
        "warning_count",
    ]

    batch_gate = json.loads((batch_root / "batch_gate_status.json").read_text(encoding="utf-8"))
    assert sorted(batch_gate.keys()) == [
        "batch_id",
        "blocking_reasons",
        "counts",
        "generated_at_utc",
        "policy_thresholds",
        "release_status",
        "review_reasons",
        "schema_version",
    ]
