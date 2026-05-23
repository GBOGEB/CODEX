import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / 'docs' / 'hbhs-ep-v8.3-tuplebridge' / 'runtime-metrics.json'


def test_metrics_file_exists():
    assert METRICS.exists()


def test_metrics_json_valid():
    data = json.loads(METRICS.read_text(encoding='utf-8'))
    assert 'program' in data
    assert 'waves' in data


def test_wave_progression_monotonic():
    data = json.loads(METRICS.read_text(encoding='utf-8'))

    previous = 0
    for wave in data['waves']:
        assert 'score_after' in wave
        after = wave['score_after']
        assert isinstance(after, (int, float))
        assert after >= previous
        previous = after
