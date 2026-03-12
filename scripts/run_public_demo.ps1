param(
    [string]$Fixture = "stepone_std.rdml",
    [string]$PlateSchema = "96"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$fixturePath = Join-Path $repoRoot "data\raw\$Fixture"
$outDir = Join-Path $repoRoot ("outputs\demo_" + [System.IO.Path]::GetFileNameWithoutExtension($Fixture))

python -m src.cli --rdml $fixturePath --outdir $outDir --min-cycles 25 --plate-schema $PlateSchema

if ($Fixture -eq "stepone_std.rdml") {
    $wellCalls = Join-Path $outDir "well_calls.csv"
    $tarball = Join-Path $repoRoot "data\raw\PCRedux_1.2-1.tar.gz"
    $compareOut = Join-Path $outDir "pcrredux_compare.json"
    if (Test-Path $tarball) {
        python scripts\compare_pcrredux.py --well-calls $wellCalls --fixture stepone_std --pcrredux-tarball $tarball --out $compareOut
    }
}
