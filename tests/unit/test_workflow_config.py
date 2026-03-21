from src.workflow.config import load_mapping


def test_load_mapping_supports_simple_yaml(tmp_path):
    config = tmp_path / "policy.yaml"
    config.write_text(
        "max_failed_runs_for_release: 1\n"
        "artifact_profile: review\n"
        "enabled: true\n",
        encoding="utf-8",
    )

    payload = load_mapping(config)

    assert payload["max_failed_runs_for_release"] == 1
    assert payload["artifact_profile"] == "review"
    assert payload["enabled"] is True
