"""Write one run-row JSON file from a validated manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.export.writers import write_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract one run row from a validated manifest.")
    parser.add_argument("--validated-manifest", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    with Path(args.validated_manifest).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("validation_status") != "valid":
        raise ValueError("Validated manifest must have validation_status='valid' before extracting run rows.")

    records = {row["run_id"]: row for row in payload["rows"]}
    if args.run_id not in records:
        raise ValueError(f"Run id {args.run_id!r} is not present in {args.validated_manifest}.")

    write_json(args.out, records[args.run_id])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
