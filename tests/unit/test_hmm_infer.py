from src.core.hmm_infer import infer_state_paths, load_model_config


def test_infer_state_paths_emits_state_for_each_row():
    features = [
        {
            "run_id": "r1",
            "plate_id": "p1",
            "well_id": "A01",
            "sample_id": "s1",
            "target_id": "t1",
            "cycle": 1,
            "df": 0.0,
            "d2f": 0.0,
        },
        {
            "run_id": "r1",
            "plate_id": "p1",
            "well_id": "A01",
            "sample_id": "s1",
            "target_id": "t1",
            "cycle": 2,
            "df": 0.2,
            "d2f": 0.2,
        },
    ]
    out = infer_state_paths(features)
    assert len(out) == 2
    assert all("state" in row for row in out)


def test_infer_state_paths_is_deterministic_for_same_input():
    features = [
        {
            "run_id": "r1",
            "plate_id": "p1",
            "well_id": "A01",
            "sample_id": "s1",
            "target_id": "t1",
            "cycle": 1,
            "df": 0.0,
            "d2f": 0.0,
        },
        {
            "run_id": "r1",
            "plate_id": "p1",
            "well_id": "A01",
            "sample_id": "s1",
            "target_id": "t1",
            "cycle": 2,
            "df": 0.2,
            "d2f": 0.1,
        },
    ]
    out_a = infer_state_paths(features)
    out_b = infer_state_paths(features)
    assert out_a == out_b


def test_load_model_config_reads_locked_thresholds():
    config = load_model_config()
    assert config["thresholds"]["exp_df_threshold"] == 0.12
    assert config["thresholds"]["plateau_df_threshold"] == 0.03
    assert config["deterministic"] is True
