from docs.wave_packages.runtime.property_schema_validator import validate_object


def test_feed_scheme_validation():
    result = validate_object('feed', {
        'source': 'ABACUS',
        'wave': 'A75',
        'timestamp': '2026-01-01T00:00:00Z',
        'signals': {'temperature': 4.5, 'pressure': 1.2},
    })
    assert result['status'] == 'passed'


def test_feed_scheme_rejects_non_numeric_signals():
    result = validate_object('feed', {
        'source': 'ABACUS',
        'wave': 'A75',
        'timestamp': '2026-01-01T00:00:00Z',
        'signals': {'temperature': 'bad'},
    })
    assert result['status'] == 'failed'


def test_topology_scheme_validation():
    result = validate_object('topology', {
        'version': '1.0',
        'forward_recursion': ['a', 'b'],
        'backward_recursion': ['x', 'y'],
    })
    assert result['status'] == 'passed'


def test_deployment_range_validation():
    result = validate_object('deployment', {
        'status': 'ok',
        'completion_percent': 120,
        'checks': [],
        'todo': [],
    })
    assert result['status'] == 'failed'


def test_reality_validation():
    result = validate_object('reality', {
        'status': 'tracked',
        'average_actual': 75,
        'items': [],
    })
    assert result['status'] == 'passed'
