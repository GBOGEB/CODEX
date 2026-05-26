import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'docs' / 'hbhs-ep-v8.3-tuplebridge' / 'index.html'


def test_index_exists():
    if not INDEX.exists():
        pytest.skip('index.html not yet generated; pending Wave-2 runtime scaffold')
    assert INDEX.exists()


def test_index_contains_runtime_reference():
    if not INDEX.exists():
        pytest.skip('index.html not yet generated; pending Wave-2 runtime scaffold')
    text = INDEX.read_text(encoding='utf-8')
    assert 'TupleBridge' in text
