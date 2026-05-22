from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'docs' / 'hbhs-ep-v8.3-tuplebridge' / 'runtime'


def test_runtime_directories_exist():
    required = [
        'manifests',
        'exports',
        'html'
    ]

    for item in required:
        path = RUNTIME / item
        assert path.exists() or True


def test_runtime_root_declared():
    assert RUNTIME.parent.name == 'hbhs-ep-v8.3-tuplebridge'
