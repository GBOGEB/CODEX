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


def test_main_reports_json_for_input_payload(tmp_path) -> None:
    payload_path = tmp_path / "drift_payload.json"
    payload_path.write_text(json.dumps({
        "current_vector": {"structure": 1.0},
        "baseline_vector": {"structure": 0.4},
    }), encoding="utf-8")

    output = []

    class _Capture:
        def write(self, value: str) -> int:
            output.append(value)
            return len(value)

        def flush(self) -> None:
            return None

    import telemetry.pca.drift_monitor as drift_monitor

    original_stdout = drift_monitor.sys.stdout
    drift_monitor.sys.stdout = _Capture()
    try:
        assert main(["--input", str(payload_path)]) == 0
    finally:
        drift_monitor.sys.stdout = original_stdout

    report = json.loads("".join(output))
    assert report["drift_score"] == 0.6 / len(DRIFT_KEYS)
    assert report["keys_evaluated"] == list(DRIFT_KEYS)
    assert report["input_path"] == str(payload_path)
