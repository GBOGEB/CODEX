from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_pages_deploy_concurrency import audit

ROOT = Path(__file__).resolve().parents[1]


def _canonical(version: str = "v4") -> str:
    return (
        "permissions:\n  contents: read\n  pages: write\n  id-token: write\n"
        "concurrency:\n  group: pages\n"
        "jobs:\n  deploy:\n    steps:\n"
        f"      - uses: actions/deploy-pages@{version}\n"
    )


def test_repository_has_exactly_one_canonical_pages_writer() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_pages_deploy_concurrency.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_canonical_writer_is_accepted(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(_canonical(), encoding="utf-8")
    assert audit(tmp_path) == []


def test_deploy_pages_v5_is_detected_and_rejected_outside_canonical(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(_canonical(), encoding="utf-8")
    (tmp_path / "legacy.yml").write_text(
        "jobs:\n  deploy:\n    steps:\n      - uses: actions/deploy-pages@v5\n",
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert any("non-canonical workflow may not deploy shared Pages" in error for error in errors)


def test_noncanonical_pages_write_permission_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(_canonical(), encoding="utf-8")
    (tmp_path / "legacy.yml").write_text(
        "permissions:\n  contents: read\n  pages: write\njobs:\n  build:\n    steps: []\n",
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert any("may not hold pages:write permission" in error for error in errors)


def test_noncanonical_inline_pages_write_permission_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(_canonical(), encoding="utf-8")
    (tmp_path / "legacy.yml").write_text(
        'permissions: {contents: read, pages: "write"}\njobs:\n  build:\n    steps: []\n',
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert any("may not hold pages:write permission" in error for error in errors)


def test_noncanonical_write_all_permission_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(_canonical(), encoding="utf-8")
    (tmp_path / "legacy.yml").write_text(
        "permissions: write-all\njobs:\n  build:\n    steps: []\n",
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert any("may not hold pages:write permission" in error for error in errors)


def test_canonical_writer_without_shared_boundary_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(
        "permissions:\n  pages: write\njobs:\n  deploy:\n    steps:\n"
        "      - uses: actions/deploy-pages@v4\n",
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert any("outside concurrency group" in error for error in errors)


def test_malformed_noncanonical_pages_writer_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(_canonical(), encoding="utf-8")
    (tmp_path / "legacy.yml").write_text(
        "jobs:\n  deploy: [\n  # actions/deploy-pages@v4\n",
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert any("YAML parse failed" in error for error in errors)


def test_unrelated_malformed_workflow_does_not_block_pages_ownership(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(_canonical(), encoding="utf-8")
    (tmp_path / "legacy.yml").write_text(
        "permissions:\n  contents: read\njobs:\n  build: [\n",
        encoding="utf-8",
    )
    assert audit(tmp_path) == []


def test_malformed_write_all_workflow_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(_canonical(), encoding="utf-8")
    (tmp_path / "legacy.yml").write_text(
        "permissions: write-all\njobs:\n  build: [\n",
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert any("YAML parse failed" in error for error in errors)


def test_malformed_quoted_write_all_workflow_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(_canonical(), encoding="utf-8")
    (tmp_path / "legacy.yml").write_text(
        "permissions: 'write-all'\njobs:\n  build: [\n",
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert any("YAML parse failed" in error for error in errors)


def test_malformed_truncated_inline_pages_write_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(_canonical(), encoding="utf-8")
    (tmp_path / "legacy.yml").write_text(
        "permissions: {pages: write\njobs:\n  build: []\n",
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert any("YAML parse failed" in error for error in errors)
