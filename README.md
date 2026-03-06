# qpcr-hmm-qc

`qpcr-hmm-qc` is a deterministic quality-control pipeline for qPCR amplification curves.
It ingests RDML or canonical curve CSV, performs HMM-style state calling, applies QC rules
(including NTC contamination and replicate discordance checks), and emits auditable outputs.

## Features

- RDML and canonical CSV input support
- Deterministic state inference with locked model configuration
- Well-level QC flags and rerun recommendations
- Plate-level summary and HTML report generation
- Unit, integration, and contract tests

## Repository Layout

- `src/` pipeline implementation
- `tests/` unit, integration, and output-contract tests
- `data/raw/` RDML fixtures and manifest
- `data/fixtures/` synthetic QC validation fixture set
- `docs/` architecture, IO contract, and source provenance

## Installation

```powershell
python -m pip install -e .
```

## Usage

Run on RDML input:

```powershell
python -m src.cli --rdml data\raw --outdir outputs\run_rdml --min-cycles 1
```

Run on canonical CSV input:

```powershell
python -m src.cli --curve-csv data\fixtures\q4_curves.csv --plate-meta-csv data\fixtures\q4_plate_meta.csv --outdir outputs\run_csv --min-cycles 3
```

## Outputs

Each run writes:

- `well_calls.csv`
- `rerun_manifest.csv`
- `plate_qc_summary.json`
- `run_metadata.json`
- `report.html`

Schema expectations are documented in `docs/io_contract.md` and enforced in `tests/contract/test_output_contract.py`.

## Quality Checks

```powershell
python -m pytest
powershell -ExecutionPolicy Bypass -File scripts\deep_sweep.ps1
```

## Validation and Benchmarks

- Benchmark summary: `RESULTS.md`
- Validation protocol and limits: `VALIDATION.md`
- Data provenance snapshot: `docs/data_sources.md`

## License

MIT. See `LICENSE`.
