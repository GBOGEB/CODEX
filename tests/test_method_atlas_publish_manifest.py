"""Guard the Method Atlas publication registration without masking orphan HTML."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_stale.py"
ENTRYPOINT = "docs/method_atlas/index.html"


def test_method_atlas_has_explicit_publication_registration():
    published = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))["published_pages"]
    assert ENTRYPOINT in published
    assert (ROOT / ENTRYPOINT).is_file()


def _check_in_isolated_docs(paths: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        (work / "MANIFEST.json").write_text(
            json.dumps({"published_pages": ["docs/index.html", ENTRYPOINT]}), encoding="utf-8"
        )
        for path in paths:
            dest = work / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("<!doctype html><title>test</title>", encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(CHECKER)], cwd=work, capture_output=True, text=True, check=False
        )


def test_registered_pages_pass_stale_checker():
    result = _check_in_isolated_docs(("docs/index.html", ENTRYPOINT))
    assert result.returncode == 0, result.stdout + result.stderr


def test_unregistered_sibling_still_fails_closed():
    stray = "docs/method_atlas/unregistered.html"
    result = _check_in_isolated_docs(("docs/index.html", ENTRYPOINT, stray))
    assert result.returncode != 0
    assert "Untracked public entrypoints under docs/:" in result.stdout + result.stderr
    assert stray in result.stdout + result.stderr
