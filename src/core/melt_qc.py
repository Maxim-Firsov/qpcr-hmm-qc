"""Melt-curve-specific QC summaries."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def analyze_melt_curves(rows: Iterable[dict]) -> dict[tuple[str, str, str], dict]:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if not row.get("is_melt_stage"):
            continue
        key = (str(row["plate_id"]), str(row["well_id"]), str(row["target_id"]))
        grouped[key].append(row)

    summaries: dict[tuple[str, str, str], dict] = {}
    for key, group in grouped.items():
        ordered = sorted(group, key=lambda item: (float(item.get("temperature_c") or 0.0), float(item["fluorescence"])))
        temperatures = [float(row.get("temperature_c") or 0.0) for row in ordered]
        fluorescence = [float(row["fluorescence"]) for row in ordered]
        peak_count = 0
        peak_temperatures: list[float] = []
        for index in range(1, len(fluorescence) - 1):
            if fluorescence[index] > fluorescence[index - 1] and fluorescence[index] >= fluorescence[index + 1]:
                peak_count += 1
                peak_temperatures.append(temperatures[index])

        temperature_span = round(max(temperatures) - min(temperatures), 3) if temperatures else 0.0
        issues: list[str] = []
        if peak_count == 0:
            issues.append("missing_peak")
        elif peak_count > 1:
            issues.append("multiple_peaks")
        if temperature_span < 2.0:
            issues.append("low_resolution")
        status = "review" if issues else "pass"
        summaries[key] = {
            "peak_count": peak_count,
            "peak_temperatures": peak_temperatures,
            "temperature_span": temperature_span,
            "issues": issues,
            "status": status,
        }
    return summaries
