import json

from telemetry.pca.drift_monitor import DRIFT_KEYS, calculate_drift, main


def test_calculate_drift_returns_zero_for_identical_vectors() -> None:
    vector = {key: 0.5 for key in DRIFT_KEYS}

    assert calculate_drift(vector, vector) == 0.0


def test_calculate_drift_averages_known_deltas() -> None:
    current_vector = {
        "structure": 0.5,
        "federation": 0.25,
    }

    assert calculate_drift(current_vector, {}) == (0.5 + 0.25) / len(DRIFT_KEYS)


def test_main_with_json_input(tmp_path, capsys) -> None:
    payload_path = tmp_path / "drift_payload.json"
    payload_path.write_text(json.dumps({
        "current_vector": {"structure": 1.0},
        "baseline_vector": {"structure": 0.4},
    }), encoding="utf-8")

    assert main(["--input", str(payload_path)]) == 0

    report = json.loads(capsys.readouterr().out)
    assert report["drift_score"] == 0.6 / len(DRIFT_KEYS)
    assert report["keys_evaluated"] == list(DRIFT_KEYS)
    assert report["input_path"] == str(payload_path)
