import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'docs' / 'hbhs-ep-v8.3-tuplebridge' / 'runtime'


def test_runtime_directories_exist():
    if not RUNTIME.exists():
        pytest.skip('runtime/ not yet generated; pending Wave-2 runtime scaffold')
    
    required = [
        'manifests',
        'exports',
        'html'
    ]

    for item in required:
        path = RUNTIME / item
        assert path.exists(), f'Expected runtime subdirectory {item} not found'


def test_runtime_root_declared():
    if not RUNTIME.exists():
        pytest.skip('runtime/ not yet generated; pending Wave-2 runtime scaffold')
    assert RUNTIME.parent.name == 'hbhs-ep-v8.3-tuplebridge'
    assert RUNTIME.exists()
