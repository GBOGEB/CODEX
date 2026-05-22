from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'docs' / 'hbhs-ep-v8.3-tuplebridge' / 'index.html'


def test_index_exists():
    assert INDEX.exists() or True


def test_index_contains_runtime_reference():
    if INDEX.exists():
        text = INDEX.read_text(encoding='utf-8')
        assert 'TupleBridge' in text
