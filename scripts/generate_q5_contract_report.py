"""Generate Q5 contract/reporting evidence artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cli import run_pipeline


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    outdir = repo_root / "outputs" / "q5"
    outdir.mkdir(parents=True, exist_ok=True)

    run_pipeline(
        Namespace(
            curve_csv=str(repo_root / "data" / "fixtures" / "q4_curves.csv"),
            rdml=None,
            plate_meta_csv=str(repo_root / "data" / "fixtures" / "q4_plate_meta.csv"),
            outdir=str(outdir),
            min_cycles=3,
        )
    )

    contract_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/contract",
        "--basetemp",
        str(repo_root / ".pytest_tmp" / "q5_contract"),
    ]
    contract_exit_code = subprocess.call(contract_cmd, cwd=str(repo_root))

    metadata = json.loads((outdir / "run_metadata.json").read_text(encoding="utf-8"))
    report_html = (outdir / "report.html").read_text(encoding="utf-8")
    summary = json.loads((outdir / "plate_qc_summary.json").read_text(encoding="utf-8"))

    checks = {
        "contract_tests_passed": contract_exit_code == 0,
        "schema_keys_present": all(key in summary for key in ["schema_version", "generated_at_utc", "plates", "global_counts"]),
        "report_has_overview": "Overview" in report_html,
        "report_has_per_plate_summary": "Per-Plate Summary" in report_html,
        "report_has_rerun_rationale": "Rerun Rationale" in report_html,
        "metadata_has_model_hash": bool(metadata.get("model_config", {}).get("hash", "")),
        "metadata_has_input_hashes": all(
            key in metadata.get("input_hashes", {})
            for key in ["curve_csv_sha256", "rdml_sha256", "plate_meta_csv_sha256"]
        ),
    }
    checks["q5_pass"] = all(checks.values())

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "checks": checks,
        "contract_exit_code": contract_exit_code,
    }
    out_path = outdir / "contract_test_report.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"q5_pass": checks["q5_pass"], "report": str(out_path.relative_to(repo_root))}))
    return 0 if checks["q5_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
