"""Tests for tools/disk_hygiene/disk_hygiene.py and a parse check of tools/relief/Fix-Machine.ps1."""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "tools" / "disk_hygiene" / "disk_hygiene.py"
FIX_MACHINE = REPO / "tools" / "relief" / "Fix-Machine.ps1"


def _load():
    spec = importlib.util.spec_from_file_location("disk_hygiene", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dh = _load()


@pytest.mark.parametrize(
    "better, worse",
    [
        ("Report.docx", "Report (1).docx"),
        ("Report.docx", "Report - Copy.docx"),
        ("Deck.pptx", "Deck-GBONTHUY-LT.pptx"),
        ("plan.xlsx", "plan_backup.xlsx"),
        ("notes.md", "notes (Recovered).md"),
    ],
)
def test_normal_name_scores_better(better, worse):
    assert dh.name_penalty(Path(better)) < dh.name_penalty(Path(worse))


def test_keeper_prefers_name_then_newest():
    a, b = Path("x/Report.docx"), Path("x/Report (1).docx")
    assert min([(b, 200.0), (a, 100.0)], key=lambda pm: dh.keeper_key(*pm))[0] == a
    c, d = Path("x/one.bin"), Path("y/one.bin")
    assert min([(c, 100.0), (d, 200.0)], key=lambda pm: dh.keeper_key(*pm))[0] == d


def test_find_duplicates_groups_identical_content(tmp_path):
    payload = os.urandom(4096)
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "Report.bin").write_bytes(payload)
    (tmp_path / "a" / "Report (1).bin").write_bytes(payload)
    (tmp_path / "a" / "other.bin").write_bytes(os.urandom(4096))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "Report.bin").write_bytes(payload)  # skipped directory
    # Backdate: a just-written file's mtime can be a hair after time.time() on Windows,
    # which the age filter would read as "too new" even with min_age_s=0.
    old = os.path.getmtime(tmp_path / "a" / "Report.bin") - 3600
    for p in tmp_path.rglob("*.bin"):
        os.utime(p, (old, old))
    groups = dh.find_duplicates([tmp_path], min_bytes=1, min_age_s=0)
    assert len(groups) == 1
    g = groups[0]
    assert Path(g["keep"]).name == "Report.bin"
    assert [Path(p).name for p in g["remove"]] == ["Report (1).bin"]


def test_dry_run_writes_reports_outside_repo(tmp_path):
    root, out = tmp_path / "root", tmp_path / "out"
    root.mkdir()
    (root / "f.bin").write_bytes(b"x" * 2048)
    assert dh.main(["--roots", str(root), "--min-mb", "0.001", "--min-age-days", "0", "--out", str(out)]) == 0
    assert list(out.glob("report_*.json")) and list(out.glob("report_*.md"))
    assert REPO not in dh.REPORTS.parents


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh not installed")
def test_fix_machine_parses():
    cmd = ("$e=$null;$t=$null;[void][System.Management.Automation.Language.Parser]::ParseFile("
           f"'{FIX_MACHINE}',[ref]$t,[ref]$e);$e.Count")
    out = subprocess.run(["pwsh", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=120,
                         check=False)
    assert out.stdout.strip() == "0", out.stdout + out.stderr
