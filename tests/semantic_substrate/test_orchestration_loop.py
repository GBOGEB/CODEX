from semantic_substrate.runtime.orchestration_loop import (
    _parse_porcelain_z,
    run_orchestration,
)


def test_parse_porcelain_handles_rename_records():
    payload = b'R  old_name.txt\x00new_name.txt\x00'
    assert _parse_porcelain_z(payload) == ['new_name.txt']


def test_parse_porcelain_handles_normal_records():
    payload = b'M  semantic_substrate/runtime/orchestration_loop.py\x00'
    assert _parse_porcelain_z(payload) == [
        'semantic_substrate/runtime/orchestration_loop.py'
    ]


def test_run_orchestration_payload_shape():
    result = run_orchestration(changed_files=['README.md'])

    assert 'validator_exit_code' in result
    assert 'delta' in result
    assert 'status' in result
    assert result['status'] in {'ok', 'failed'}
