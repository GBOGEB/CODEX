from unittest.mock import patch

from semantic_substrate.runtime.orchestration_loop import (
    _parse_porcelain_z,
    run_orchestration,
)


def test_parse_porcelain_handles_rename_records():
    # Real git --porcelain=v1 -z output: destination path is first in the entry,
    # origin (old) path follows as the next NUL-delimited field.
    payload = b'R  new_name.txt\x00old_name.txt\x00'
    assert _parse_porcelain_z(payload) == ['new_name.txt']


def test_parse_porcelain_handles_normal_records():
    payload = b'M  semantic_substrate/runtime/orchestration_loop.py\x00'
    assert _parse_porcelain_z(payload) == [
        'semantic_substrate/runtime/orchestration_loop.py'
    ]


def test_run_orchestration_payload_shape_ok():
    fake_validator = {
        'exit_code': 0,
        'stdout': 'SEMANTIC VALIDATION PASSED\n',
        'stderr': '',
    }
    with patch(
        'semantic_substrate.runtime.orchestration_loop._run_validator',
        return_value=fake_validator,
    ):
        result = run_orchestration(changed_files=['README.md'])

    assert result['validator_exit_code'] == 0
    assert result['delta'] is not None
    assert result['status'] == 'ok'
    assert result['error'] is None
    assert 'validator_stdout' in result
    assert 'validator_stderr' in result
    assert result['loop_trace'] == [
        'observe',
        'classify',
        'validate',
        'generate_delta',
        'update_snapshot',
        'update_lineage',
        'update_debt',
        'recommend_next_action',
    ]
    assert result['delta']['files'][0]['classification'] == 'documentation'
    assert result['drift_report']['finding_count'] == 0
    assert result['merge_orchestration']['rules']
    assert '<html' in result['semantic_graph_html']
    assert result['recommended_next_actions']


def test_run_orchestration_payload_shape_failed():
    fake_validator = {'exit_code': 1, 'stdout': '', 'stderr': 'validation error'}
    with patch(
        'semantic_substrate.runtime.orchestration_loop._run_validator',
        return_value=fake_validator,
    ):
        result = run_orchestration(changed_files=['README.md'])

    assert result['validator_exit_code'] == 1
    assert result['status'] == 'failed'
    assert result['error'] is None
    assert 'validator_stdout' in result
    assert 'validator_stderr' in result
    assert result['recommended_next_actions'] == ['Resolve semantic validator failures before merge.']


def test_run_orchestration_payload_shape_oserror():
    with patch(
        'semantic_substrate.runtime.orchestration_loop._run_validator',
        side_effect=OSError('no python binary'),
    ):
        result = run_orchestration(changed_files=['README.md'])

    assert result['status'] == 'failed'
    assert result['validator_exit_code'] is None
    assert 'no python binary' in result['error']
    assert result['loop_trace'] == ['observe', 'classify', 'validate']
