"""Stop workflow dispatch if the validated manifest report is invalid."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assert that a validated manifest report is valid.")
    parser.add_argument("--validated-manifest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    manifest_path = Path(args.validated_manifest)
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if payload.get("validation_status") != "valid":
        errors = payload.get("errors") or ["Manifest validation failed."]
        raise ValueError("; ".join(errors))

    outpath = Path(args.out)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text("valid\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
