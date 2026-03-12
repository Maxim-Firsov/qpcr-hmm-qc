# VALIDATION

This document records the validation dataset design, metrics, and current limitations.

## 1. Dataset Provenance and Snapshot Date

- RDML intake fixtures: `data/raw/*.rdml` tracked in `data/raw/manifest.csv`
- Q4/Q5/Q6 validation fixture: `data/fixtures/q4_curves.csv` with metadata `data/fixtures/q4_plate_meta.csv`
- Public parser/runtime fixtures: `data/raw/stepone_std.rdml`, `data/raw/BioRad_qPCR_melt.rdml`, `data/raw/lc96_bACTXY.rdml`
- Snapshot date: 2026-03-12 UTC
- Fixture types:
  - deterministic synthetic validation fixture for rule-level expected outcomes
  - public RDML fixtures for parser coverage and runtime evidence, not clinical truth data

## 2. Labeling Methodology

Expected QC outcomes were assigned directly from fixture design intent:

- `A01` (`control_type=ntc`) contains amplification profile and should trigger `ntc_contamination` rerun.
- `A02` and `A03` are replicate group `rg1` with conflicting amplification labels and should trigger `replicate_discordance` rerun.
- `B01` is a clean amplified sample and should pass.

Ground truth was compared against generated `well_calls.csv`/`rerun_manifest.csv` outputs from repeated runs.

## 3. Metrics and Confidence Intervals

Observed on the Q4 synthetic fixture:

- Rerun detection for designed failure wells: `3/3` (100%)
- Overall expected well-level QC status match: `4/4` (100%)

95% Wilson confidence intervals (small-sample, binomial):

- Failure-well rerun detection (`3/3`): `[0.4385, 1.0000]`
- Overall expected status match (`4/4`): `[0.5101, 1.0000]`

Supporting evidence:

- `outputs/q4/q4_check_report.json`
- `outputs/q6/reproducibility_report.json`

## 4. Public RDML Coverage Evidence

Observed parser coverage on public fixtures:

- `stepone_std.rdml`: `960` parsed rows across `24` well-target traces
- `BioRad_qPCR_melt.rdml`: `2460` parsed rows across `60` well-target traces
- `lc96_bACTXY.rdml`: `19200` parsed rows across `384` well-target traces

What this supports:

- ZIP-container `.rdml` archives are now parsed successfully, not just plain XML fixtures
- numeric `react id` values are mapped into canonical well IDs when RDML plate geometry is present
- the pipeline can execute end to end on small, medium, and larger public RDML examples

What this does not support:

- no claim of biological/clinical correctness on these public fixtures
- no claim that melt-stage handling is fully calibrated or assay-specific
- no claim that current review/pass outcomes are reference labels

## 5. Additional Public Reference Material

An optional local-only reference package, `PCRedux_1.2-1.tar.gz`, contains public decision files that correspond to some of the same fixture families used here, including:

- `decision_res_stepone_std.csv`
- `decision_res_lc96_bACTXY.csv`

These files are useful as portfolio evidence that public third-party decision references exist, but they are not yet integrated into automated Python-side validation because identifier mapping between the PCRedux decision tables and current pipeline outputs still needs explicit reconciliation.

## 6. Known Failure Modes and Limitations

- Current validation is synthetic and low-scale; no claim is made about clinical sensitivity/specificity.
- RDML parsing now covers plain XML and ZIP-container RDML examples, but vendor-specific edge schemas may still require extensions.
- Confidence and state assignment use deterministic threshold logic in `v0.1.0`; statistical calibration against external truth datasets is not included yet.
- Runtime evidence now includes public RDML fixtures, and peak traced memory is captured in `run_metadata.json`, but full process RSS is not.
