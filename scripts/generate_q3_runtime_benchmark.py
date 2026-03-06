"""Generate Q3 runtime and determinism benchmark evidence."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.features import build_features
from src.core.hmm_infer import infer_state_paths, load_model_config
from src.core.normalize import normalize_rows
from src.core.validate import validate_rows
from src.io.rdml_loader import load_rdml


def _path_hash(rows: list[dict]) -> str:
    compact = [
        {
            "run_id": row["run_id"],
            "plate_id": row["plate_id"],
            "well_id": row["well_id"],
            "target_id": row["target_id"],
            "cycle": row["cycle"],
            "state": row["state"],
        }
        for row in rows
    ]
    payload = json.dumps(compact, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _load_baseline_rows(repo_root: Path) -> list[dict]:
    rdml_dir = repo_root / "data" / "raw"
    rows: list[dict] = []
    for rdml_file in sorted(rdml_dir.glob("*.rdml")):
        rows.extend(load_rdml(rdml_file))
    return rows


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    out_path = repo_root / "outputs" / "q3" / "runtime_benchmark.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    model_config = load_model_config()
    raw = _load_baseline_rows(repo_root)
    normalized = normalize_rows(raw)
    eligible, _, validation_summary = validate_rows(normalized, min_cycles=1)
    features = build_features(eligible)

    # Runtime benchmark on repeated deterministic inference calls.
    iterations = 200
    start = time.perf_counter()
    final_paths: list[dict] = []
    for _ in range(iterations):
        final_paths = infer_state_paths(features, model_config_path=model_config["path"])
    elapsed = time.perf_counter() - start
    avg_ms = (elapsed / iterations) * 1000.0

    run_a = infer_state_paths(features, model_config_path=model_config["path"])
    run_b = infer_state_paths(features, model_config_path=model_config["path"])
    path_hash_a = _path_hash(run_a)
    path_hash_b = _path_hash(run_b)
    deterministic = path_hash_a == path_hash_b

    unique_curves = {
        (row["run_id"], row["plate_id"], row["well_id"], row["target_id"])
        for row in eligible
    }
    inferred_curves = {
        (row["run_id"], row["plate_id"], row["well_id"], row["target_id"])
        for row in final_paths
    }
    state_emission_complete = inferred_curves == unique_curves

    runtime_target_ms = 1.0
    checks = {
        "eligible_curve_count": len(unique_curves),
        "state_path_emitted_for_each_curve": state_emission_complete,
        "deterministic_same_input": deterministic,
        "avg_infer_runtime_ms": round(avg_ms, 6),
        "runtime_target_ms": runtime_target_ms,
        "runtime_target_met": avg_ms <= runtime_target_ms,
    }
    checks["q3_pass"] = (
        checks["state_path_emitted_for_each_curve"]
        and checks["deterministic_same_input"]
        and checks["runtime_target_met"]
    )

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "model_config": {
            "path": str(Path(model_config["path"]).resolve().relative_to(repo_root)),
            "sha256": model_config["sha256"],
            "thresholds": model_config["thresholds"],
        },
        "dataset_summary": {
            "raw_rows": len(raw),
            "eligible_rows": len(eligible),
            "validation_error_counts": validation_summary["error_counts"],
        },
        "checks": checks,
        "determinism": {"run_a_path_hash": path_hash_a, "run_b_path_hash": path_hash_b},
    }
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"q3_pass": checks["q3_pass"], "report": str(out_path.relative_to(repo_root))}))
    return 0 if checks["q3_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
