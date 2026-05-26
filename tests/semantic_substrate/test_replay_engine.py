from semantic_substrate.engines.replay_engine import ReplayEngine
from semantic_substrate.runtime.replay_runner import run_replay
from semantic_substrate.viewers.semantic_graph_renderer import load_branches, render_html_graph


def test_replay_engine_is_deterministic():
    engine = ReplayEngine()
    first = engine.replay()
    second = engine.replay()

    assert first['status'] == 'ok'
    assert second['status'] == 'ok'
    assert first['state_hash'] == second['state_hash']
    assert first['state']['snapshot_id'] == 'STATE-0001'
    assert 'ROOT' in first['state']['tuple_lineage']


def test_replay_runner_returns_serializable_payload():
    payload = run_replay()
    assert payload['status'] == 'ok'
    assert payload['error'] is None
    assert payload['state']


def test_semantic_graph_renderer_emits_html_document():
    branches = load_branches()
    html = render_html_graph(branches)
    assert '<!DOCTYPE html>' in html
    assert 'CODEX Semantic Graph' in html
    assert 'ROOT' in html
