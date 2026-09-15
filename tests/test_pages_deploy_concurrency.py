from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.check_pages_deploy_concurrency import audit

ROOT = Path(__file__).resolve().parents[1]


def test_all_pages_deployers_share_repository_concurrency_boundary() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_pages_deploy_concurrency.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_unrelated_malformed_workflow_is_out_of_scope(tmp_path: Path) -> None:
    (tmp_path / "unrelated.yml").write_text("jobs:\n  broken: [\n", encoding="utf-8")
    (tmp_path / "pages.yml").write_text(
        "concurrency:\n  group: pages\njobs:\n  deploy:\n    steps:\n"
        "      - uses: actions/deploy-pages@v4\n",
        encoding="utf-8",
    )
    assert audit(tmp_path) == []


def test_malformed_pages_deployer_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(
        "jobs:\n  deploy: [\n  # actions/deploy-pages@v4\n",
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert errors and "Pages-deployer YAML parse failed" in errors[0]


def test_pages_deployer_without_shared_boundary_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "pages.yml").write_text(
        "jobs:\n  deploy:\n    steps:\n      - uses: actions/deploy-pages@v4\n",
        encoding="utf-8",
    )
    errors = audit(tmp_path)
    assert errors and "outside shared concurrency group 'pages'" in errors[0]
