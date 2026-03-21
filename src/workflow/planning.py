"""Helpers for conservative pre-validation Snakemake planning."""

from __future__ import annotations

from pathlib import Path

from src.workflow.manifest import RUN_ID_PATTERN


def planned_run_ids(manifest_path: str | Path) -> list[str]:
    manifest_file = Path(manifest_path)
    if not manifest_file.is_absolute():
        manifest_file = Path.cwd() / manifest_file
    if not manifest_file.exists():
        return []

    run_ids = []
    seen = set()
    with manifest_file.open("r", encoding="utf-8-sig", errors="replace") as handle:
        lines = handle.read().splitlines()
    for index, line in enumerate(lines[1:], start=1):
        if not line.strip():
            continue
        candidate = (line.split("\t", 1)[0] or "").strip()
        if not candidate or not RUN_ID_PATTERN.match(candidate):
            candidate = f"manifest_row_{index:03d}"
        if candidate in seen:
            candidate = f"{candidate}__row_{index:03d}"
        seen.add(candidate)
        run_ids.append(candidate)
    return run_ids
