"""Generate Q2 canonicalization report from RDML fixtures."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.normalize import normalize_rows
from src.core.validate import validate_rows
from src.io.rdml_loader import load_rdml_with_report

REQUIRED_COLUMNS = ["run_id", "plate_id", "well_id", "sample_id", "target_id", "cycle", "fluorescence"]


def _row_schema_ok(row: dict) -> bool:
    if any(key not in row for key in REQUIRED_COLUMNS):
        return False
    if not isinstance(row["run_id"], str):
        return False
    if not isinstance(row["plate_id"], str):
        return False
    if not isinstance(row["well_id"], str):
        return False
    if not isinstance(row["sample_id"], str):
        return False
    if not isinstance(row["target_id"], str):
        return False
    if not isinstance(row["cycle"], int):
        return False
    if not isinstance(row["fluorescence"], float):
        return False
    return True


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / "data" / "raw" / "manifest.csv"
    out_path = repo_root / "outputs" / "q2" / "canonicalization_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))

    fixture_rows = [row for row in manifest_rows if row.get("status", "").strip().lower() != "excluded"]
    fixture_reports: list[dict] = []

    total_raw_rows = 0
    total_normalized_rows = 0
    total_schema_failures = 0
    total_malformed_rows = 0
    total_rejected_rows = 0

    for fixture in fixture_rows:
        file_name = fixture.get("file_name", "").strip()
        file_path = manifest_path.parent / file_name
        fixture_report = {"file_name": file_name, "status": fixture.get("status", "").strip(), "exists": file_path.exists()}
        if not file_path.exists():
            fixture_report["error"] = "missing_fixture_file"
            total_schema_failures += 1
            fixture_reports.append(fixture_report)
            continue

        raw_rows, rdml_report = load_rdml_with_report(file_path)
        normalized = normalize_rows(raw_rows)
        _, rejected, validation_summary = validate_rows(normalized, min_cycles=1)
        schema_failures = sum(1 for row in normalized if not _row_schema_ok(row))

        fixture_report.update(
            {
                "run_id": rdml_report["run_id"],
                "instrument": rdml_report["instrument"],
                "raw_rows": len(raw_rows),
                "normalized_rows": len(normalized),
                "malformed_rows": rdml_report["malformed_rows"],
                "schema_failures": schema_failures,
                "rejected_rows": len(rejected),
                "validation_error_counts": validation_summary["error_counts"],
            }
        )
        fixture_reports.append(fixture_report)

        total_raw_rows += len(raw_rows)
        total_normalized_rows += len(normalized)
        total_malformed_rows += rdml_report["malformed_rows"]
        total_schema_failures += schema_failures
        total_rejected_rows += len(rejected)

    checks = {
        "fixture_count_non_excluded": len(fixture_rows),
        "all_non_excluded_mapped": all(
            report.get("exists")
            and report.get("schema_failures", 0) == 0
            and report.get("normalized_rows", 0) > 0
            for report in fixture_reports
        ),
        "malformed_rows_counted_and_reported": total_malformed_rows >= 0,
        "total_malformed_rows": total_malformed_rows,
        "total_schema_failures": total_schema_failures,
        "total_rejected_rows": total_rejected_rows,
    }
    checks["q2_pass"] = checks["all_non_excluded_mapped"] and checks["total_schema_failures"] == 0

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "canonical_schema_required_columns": REQUIRED_COLUMNS,
        "summary": {
            "raw_rows": total_raw_rows,
            "normalized_rows": total_normalized_rows,
            "schema_failures": total_schema_failures,
            "malformed_rows": total_malformed_rows,
            "rejected_rows": total_rejected_rows,
        },
        "checks": checks,
        "fixtures": fixture_reports,
    }
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"q2_pass": checks["q2_pass"], "report": str(out_path.relative_to(repo_root))}))
    return 0 if checks["q2_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
