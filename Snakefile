from pathlib import Path
import csv


configfile: "workflow/config/batch_config.yaml"

OUTPUT_ROOT = Path(config["output_root"]).resolve()
VALIDATED_MANIFEST = OUTPUT_ROOT / "_workflow" / "validated_manifest.json"
MANIFEST_OK = OUTPUT_ROOT / "_workflow" / "manifest.ok"
GATE_CONFIG = Path(config.get("gate_config", "workflow/config/batch_release_policy.yaml")).resolve()


def _planned_run_ids(manifest_path):
    manifest_file = Path(manifest_path)
    if not manifest_file.is_absolute():
        manifest_file = Path.cwd() / manifest_file
    if not manifest_file.exists():
        return []

    run_ids = []
    seen = set()
    with manifest_file.open("r", encoding="utf-8", newline="") as handle:
        for index, row in enumerate(csv.DictReader(handle, delimiter="\t"), start=1):
            candidate = (row.get("run_id") or "").strip() or f"manifest_row_{index:03d}"
            if candidate in seen:
                candidate = f"{candidate}__row_{index:03d}"
            seen.add(candidate)
            run_ids.append(candidate)
    return run_ids


RUN_IDS = _planned_run_ids(config["manifest"])


rule all:
    input:
        str(OUTPUT_ROOT / "batch_master.json"),
        str(OUTPUT_ROOT / "batch_master.tsv"),
        str(OUTPUT_ROOT / "rerun_queue.csv"),
        str(OUTPUT_ROOT / "failure_reason_counts.tsv"),
        str(OUTPUT_ROOT / "batch_gate_status.json"),
        str(OUTPUT_ROOT / "batch_report.md"),


rule validate_manifest:
    output:
        str(VALIDATED_MANIFEST),
    params:
        manifest=config["manifest"],
        output_root=str(OUTPUT_ROOT),
        artifact_profile=config.get("artifact_profile", "review"),
    shell:
        "python -m src.workflow.manifest --manifest \"{params.manifest}\" --output-root \"{params.output_root}\" "
        "--artifact-profile {params.artifact_profile} --out \"{output}\""


rule assert_manifest_valid:
    input:
        validated_manifest=str(VALIDATED_MANIFEST),
    output:
        str(MANIFEST_OK),
    shell:
        "python -m src.workflow.assert_manifest_valid --validated-manifest \"{input.validated_manifest}\" --out \"{output}\""


rule run_manifest_row:
    input:
        validated_manifest=str(VALIDATED_MANIFEST),
        manifest_ok=str(MANIFEST_OK),
    output:
        summary=str(OUTPUT_ROOT / "runs/{run_id}/summary.json"),
        workflow_status=str(OUTPUT_ROOT / "runs/{run_id}/workflow_status.json"),
    params:
        run_id="{run_id}",
    shell:
        "python -m src.workflow.batch_runner --validated-manifest \"{input.validated_manifest}\" --run-id {params.run_id}"


rule aggregate_batch:
    input:
        validated_manifest=str(VALIDATED_MANIFEST),
        manifest_ok=str(MANIFEST_OK),
        summaries=expand(str(OUTPUT_ROOT / "runs/{run_id}/summary.json"), run_id=RUN_IDS),
        workflow_statuses=expand(str(OUTPUT_ROOT / "runs/{run_id}/workflow_status.json"), run_id=RUN_IDS),
    output:
        batch_master_json=str(OUTPUT_ROOT / "batch_master.json"),
        batch_master_tsv=str(OUTPUT_ROOT / "batch_master.tsv"),
        rerun_queue=str(OUTPUT_ROOT / "rerun_queue.csv"),
        failure_reason_counts=str(OUTPUT_ROOT / "failure_reason_counts.tsv"),
        batch_gate_status=str(OUTPUT_ROOT / "batch_gate_status.json"),
        batch_report=str(OUTPUT_ROOT / "batch_report.md"),
    params:
        output_root=str(OUTPUT_ROOT),
        gate_config=str(GATE_CONFIG),
    shell:
        "python -m src.workflow.aggregate_batch --validated-manifest \"{input.validated_manifest}\" "
        "--output-root \"{params.output_root}\" --gate-config \"{params.gate_config}\""
