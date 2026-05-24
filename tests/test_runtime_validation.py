from pathlib import Path
import json

from docs.wave_packages.runtime.covariance_runtime import covariance_health
from docs.wave_packages.runtime.abacus_feed_runtime import validate_feed
from docs.wave_packages.runtime.statistics_pca_runtime import compute_report
from docs.wave_packages.runtime import topology_reconciliation_runtime


def test_covariance_runtime():
    report = covariance_health([[1.0, 0.1], [0.1, 1.0]])
    assert report['status'] == 'ok'
    assert report['score'] >= 80


def test_feed_validation():
    report = validate_feed({
        'source': 'ABACUS',
        'wave': 'A69',
        'timestamp': '2026-01-01T00:00:00Z',
        'signals': {'temperature_K': 4.5}
    })
    assert report['signal_count'] == 1
    assert report['status'] == 'validated'


def test_statistics_runtime():
    report = compute_report([
        {'wave': 'A66', 'bridge': 80, 'sync': 82, 'pages': 75, 'covariance': 60, 'abacus': 50},
        {'wave': 'A67', 'bridge': 90, 'sync': 92, 'pages': 85, 'covariance': 70, 'abacus': 65},
    ])
    assert report['status'] == 'statistics-pca-runtime-complete'
    assert 'pca' in report
    assert report['kpi_summary']['average_latest'] > 0


def test_runtime_paths_exist():
    assert Path('docs/wave_packages/runtime').exists()


def test_topology_reconciliation_deduplicates_recorded_nodes(tmp_path, monkeypatch):
    topology_data = {
        'forward_recursion': ['ABACUS feed', 'bridge runtime'],
        'backward_recursion': ['runtime insight'],
        'bridge_federation': {'runtime_bridge': 'medium_high'},
    }
    topology_path = tmp_path / 'topology_runtime.json'
    topology_path.write_text(json.dumps(topology_data), encoding='utf-8')
    monkeypatch.setattr(topology_reconciliation_runtime, 'TOPOLOGY', topology_path)

    first_report = topology_reconciliation_runtime.reconcile()
    second_report = topology_reconciliation_runtime.reconcile()
    expected_missing = topology_reconciliation_runtime.REQUIRED_NODES[1:]

    assert first_report['status'] == 'reconciled-persisted'
    assert second_report['status'] == 'reconciled-already-recorded'
    assert second_report['reconciled_nodes'] == []
    assert 'runtime_bridge' not in first_report['missing_nodes']
    assert set(second_report['missing_nodes']) == set(expected_missing)

    persisted = json.loads(topology_path.read_text(encoding='utf-8'))
    for node in expected_missing:
        assert persisted['reconciled_nodes'].count(node) == 1
