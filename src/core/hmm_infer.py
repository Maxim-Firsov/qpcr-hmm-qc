"""Deterministic HMM-like inference scaffold."""

from __future__ import annotations

import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Iterable

STATE_BASELINE = "baseline_noise"
STATE_EXP = "exponential_amplification"
STATE_TRANSITION = "linear_transition"
STATE_PLATEAU = "plateau"
DEFAULT_MODEL_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "model_v1.yaml"


def load_model_config(path: str | Path | None = None) -> dict:
    config_path = Path(path) if path else DEFAULT_MODEL_CONFIG_PATH
    text = config_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    exp_df_threshold = None
    plateau_df_threshold = None
    states: list[str] = []
    deterministic = False
    in_states = False

    for line in lines:
        if line.startswith("states:"):
            in_states = True
            continue
        if in_states and line.startswith("- "):
            states.append(line[2:].strip())
            continue
        if in_states and not line.startswith("- "):
            in_states = False
        if line.startswith("exp_df_threshold:"):
            exp_df_threshold = float(line.split(":", 1)[1].strip())
        elif line.startswith("plateau_df_threshold:"):
            plateau_df_threshold = float(line.split(":", 1)[1].strip())
        elif line.startswith("deterministic:"):
            deterministic = line.split(":", 1)[1].strip().lower() == "true"

    if exp_df_threshold is None or plateau_df_threshold is None:
        raise ValueError(f"Missing threshold values in model config: {config_path}")
    if not states:
        states = [STATE_BASELINE, STATE_EXP, STATE_TRANSITION, STATE_PLATEAU]

    return {
        "path": str(config_path),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "states": states,
        "thresholds": {
            "exp_df_threshold": exp_df_threshold,
            "plateau_df_threshold": plateau_df_threshold,
        },
        "deterministic": deterministic,
    }


def _state_from_features(feature_row: dict, exp_df_threshold: float, plateau_df_threshold: float) -> str:
    df = float(feature_row["df"])
    d2f = float(feature_row["d2f"])
    if df >= exp_df_threshold and d2f >= 0:
        return STATE_EXP
    if df >= plateau_df_threshold:
        return STATE_TRANSITION
    if df >= 0 and d2f < 0:
        return STATE_PLATEAU
    return STATE_BASELINE


def infer_state_paths(
    feature_rows: Iterable[dict],
    exp_df_threshold: float | None = None,
    plateau_df_threshold: float | None = None,
    model_config_path: str | Path | None = None,
) -> list[dict]:
    if exp_df_threshold is None or plateau_df_threshold is None:
        config = load_model_config(model_config_path)
        exp_df_threshold = config["thresholds"]["exp_df_threshold"]
        plateau_df_threshold = config["thresholds"]["plateau_df_threshold"]

    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in feature_rows:
        key = (row["run_id"], row["plate_id"], row["well_id"], row["target_id"])
        grouped[key].append(row)

    inferred: list[dict] = []
    for _, rows in grouped.items():
        for row in sorted(rows, key=lambda r: r["cycle"]):
            state = _state_from_features(row, exp_df_threshold, plateau_df_threshold)
            out = dict(row)
            out["state"] = state
            # Confidence is deterministic and bounded for simple contract testing.
            out["state_confidence"] = min(1.0, max(0.0, abs(float(row["df"])) * 2.0))
            inferred.append(out)
    inferred.sort(
        key=lambda r: (
            r["run_id"],
            r["plate_id"],
            r["well_id"],
            r["target_id"],
            r["cycle"],
        )
    )
    return inferred
