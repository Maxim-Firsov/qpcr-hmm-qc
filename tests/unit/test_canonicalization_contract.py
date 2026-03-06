from src.core.normalize import normalize_rows
from src.core.validate import validate_rows
from src.io.rdml_loader import load_rdml_with_report

REQUIRED_COLUMNS = {"run_id", "plate_id", "well_id", "sample_id", "target_id", "cycle", "fluorescence"}


def test_rdml_rows_map_to_canonical_schema():
    rows, report = load_rdml_with_report("data/raw/rdml_biorad_cfx96.rdml")
    normalized = normalize_rows(rows)
    eligible, rejected, _ = validate_rows(normalized, min_cycles=1)

    assert report["parsed_rows"] > 0
    assert report["malformed_rows"] >= 0
    assert len(rejected) == 0
    assert len(eligible) == len(normalized)
    for row in normalized:
        assert REQUIRED_COLUMNS.issubset(set(row.keys()))
        assert isinstance(row["cycle"], int)
        assert isinstance(row["fluorescence"], float)
