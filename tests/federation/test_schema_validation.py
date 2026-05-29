from pathlib import Path

from src.federation.schema_validation import validate_repository_ssot


def test_validate_repository_ssot_passes_for_current_repo():
    repo_root = Path(__file__).resolve().parents[2]
    errors = validate_repository_ssot(repo_root)
    assert errors == []
