import tarfile
from pathlib import Path

from scripts.compare_pcrredux import compare_stepone


def test_compare_stepone_matches_expected_labels(tmp_path):
    well_calls = tmp_path / "well_calls.csv"
    well_calls.write_text(
        "\n".join(
            [
                "run_id,plate_id,well_id,sample_id,target_id,control_type,ct_estimate,hmm_state_path_compact,amplification_confidence,call_label,qc_status,qc_flags",
                'Run001,Run001,A01,NTC_RNase P,RNase P,sample,,baseline_noise:40,0.49,not_amplified,review,"[]"',
                'Run001,Run001,A04,pop1_RNase P,RNase P,sample,31.4,baseline_noise:27|exponential_amplification:4,0.66,amplified,pass,"[]"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    tarball = tmp_path / "PCRedux_1.2-1.tar.gz"
    csv_payload = "\n".join(
        [
            "stepone_std,test.result.1,test.result.2,test.result.3,conformity",
            "A01~NTC_RNase P~ntc~RNase P~Run001,n,n,n,TRUE",
            "A04~pop1_RNase P~unkn~RNase P~Run001,y,y,y,TRUE",
        ]
    ) + "\n"
    source_csv = tmp_path / "decision_res_stepone_std.csv"
    source_csv.write_text(csv_payload, encoding="utf-8")

    with tarfile.open(tarball, "w:gz") as archive:
        archive.add(source_csv, arcname="PCRedux/inst/decision_res_stepone_std.csv")

    report = compare_stepone(well_calls, tarball)
    assert report["matched_rows"] >= 2
    assert report["label_matches"] >= 2
