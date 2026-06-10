from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_runtime_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "codex" / "contract_governance" / "runtime.py"
    assert module_path.is_file(), f"missing runtime module at {module_path}"
    spec = importlib.util.spec_from_file_location("contract_governance_runtime", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runtime = _load_runtime_module()


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("21.3", (21, 3)),
        ("22.0", (22, 0)),
        ("23.1.dev0", (23, 1)),
        ("24.0rc1", (24, 0)),
    ],
)
def test_parse_pip_major_minor_accepts_pep440_suffixes(
    version: str,
    expected: tuple[int, int],
) -> None:
    assert runtime.parse_pip_major_minor(version) == expected


@pytest.mark.parametrize("version", ["21.3", "22.0", "23.1.dev0"])
def test_ensure_pep660_pip_version_accepts_supported_versions(version: str) -> None:
    runtime.ensure_pep660_pip_version(version)


@pytest.mark.parametrize("version", ["21.2", "20.3.4"])
def test_ensure_pep660_pip_version_rejects_old_versions(version: str) -> None:
    with pytest.raises(RuntimeError, match="pip>=21.3"):
        runtime.ensure_pep660_pip_version(version)


def test_parse_pip_major_minor_rejects_unparseable_versions() -> None:
    with pytest.raises(ValueError, match="unable to parse pip version"):
        runtime.parse_pip_major_minor("not-a-version")
