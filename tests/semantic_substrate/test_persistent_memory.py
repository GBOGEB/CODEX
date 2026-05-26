from semantic_substrate.memory.persistent_memory import load_memory, persist_session


def test_persist_session_writes_replay_checkpoint(tmp_path):
    memory_path = tmp_path / 'session_memory.yaml'
    snapshot = {'snapshot_id': 'STATE-0099'}
    delta = {'id': 'DELTA-0001', 'to_state': 'STATE-0099'}
    drift = {'drift_score': 2, 'debt_status': 'warning', 'finding_count': 1}

    entry = persist_session(
        snapshot=snapshot,
        delta=delta,
        drift_report=drift,
        recommended_next_actions=['review drift'],
        path=memory_path,
    )
    payload = load_memory(memory_path)

    assert entry['replay_checkpoint']['snapshot_id'] == 'STATE-0099'
    assert entry['replay_checkpoint']['delta_id'] == 'DELTA-0001'
    assert payload['sessions'][-1]['drift']['status'] == 'warning'
