"""Unit tests for the ADR-0002 SPINE gate and stage tools (synthetic trees only)."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "spine"))

import spine_gate
import spine_stage


def _tree(files: dict[str, str], manifest: dict) -> Path:
    root = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    (root / "spine").mkdir(exist_ok=True)
    (root / "spine" / "SPINE_MANIFEST.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return root


BASE = {
    "include": ["core/**"],
    "exclude": ["core/private.py"],
    "deny_terms": {"private_project": [r"\bqps\b"]},
    "secret_patterns": {"github_token": r"gh[pousr]_[A-Za-z0-9]{36,}"},
}


def _run(root: Path) -> tuple[int, dict]:
    receipt = root / "r.json"
    rc = spine_gate.run(root, root / "spine" / "SPINE_MANIFEST.yaml", receipt)
    return rc, json.loads(receipt.read_text())


def test_clean_tree_passes_and_hashes_every_file():
    root = _tree({"core/__init__.py": "", "core/a.py": "import json\n"}, BASE)
    rc, r = _run(root)
    assert rc == 0 and r["verdict"] == "PASS"
    assert r["counts"] == {"admitted": 2, "clean": 2, "blocked": 0}
    assert all(len(f["sha256"]) == 64 for f in r["files"])


def test_deny_term_blocks_file():
    root = _tree({"core/a.py": "# QPS authority\n"}, BASE)
    rc, r = _run(root)
    assert rc == 1 and r["files"][0]["findings"][0]["rule"] == "private_project"


def test_secret_blocks_file():
    root = _tree({"core/a.py": "T='ghp_" + "a" * 36 + "'\n"}, BASE)
    rc, r = _run(root)
    assert rc == 1 and r["files"][0]["findings"][0]["rule"] == "github_token"


def test_excluded_file_is_not_admitted_and_import_of_it_breaks_closure():
    files = {"core/__init__.py": "", "core/a.py": "import secretmod\n", "secretmod.py": "x=1\n",
             "core/private.py": "# QPS\n"}
    rc, r = _run(_tree(files, BASE))
    paths = {f["path"] for f in r["files"]}
    assert "core/private.py" not in paths
    assert rc == 1 and any(x["rule"] == "import_closure" for x in r["files"][1]["findings"])


def test_missing_include_pattern_fails():
    m = dict(BASE, include=["core/**", "nothing/**"])
    rc, r = _run(_tree({"core/a.py": ""}, m))
    assert rc == 1 and r["missing_include_patterns"] == ["nothing/**"]


def test_overlay_replaces_and_is_scanned():
    m = dict(BASE, overlay={"core/README.md": "spine/overlay/README.md"})
    root = _tree({"core/a.py": "", "spine/overlay/README.md": "clean text\n"}, m)
    rc, r = _run(root)
    entry = next(f for f in r["files"] if f["path"] == "core/README.md")
    assert rc == 0 and entry["overlay_source"] == "spine/overlay/README.md"


def test_allowlist_suppresses_documented_false_positive():
    m = dict(BASE, allowlist=[{"path": "core/a.py", "pattern": "private_project", "reason": "test"}])
    rc, _ = _run(_tree({"core/a.py": "# qps\n"}, m))
    assert rc == 0


def test_stage_refuses_fail_receipt_and_detects_drift():
    root = _tree({"core/a.py": "# qps\n"}, BASE)
    _run(root)
    assert spine_stage.stage(root, root / "r.json", root / "out1") == 2

    root = _tree({"core/a.py": "x=1\n"}, BASE)
    _run(root)
    (root / "core" / "a.py").write_text("x=2\n", encoding="utf-8")
    assert spine_stage.stage(root, root / "r.json", root / "out2") == 1


def test_stage_copies_exact_tree():
    root = _tree({"core/a.py": "x=1\n", "core/sub/b.py": "y=2\n"}, BASE)
    _run(root)
    out = root / "out"
    assert spine_stage.stage(root, root / "r.json", out) == 0
    assert (out / "core" / "sub" / "b.py").read_text() == "y=2\n"
    assert json.loads((out / "STAGE_RECEIPT.json").read_text())["files"] == 2


def test_recursive_include_matches_nested_files_on_every_python():
    # Regression: Path.glob("dir/**") yields only directories before Python 3.13,
    # which made every "dir/**" include match nothing on 3.11 CI runners.
    root = _tree({"core/a.py": "", "core/deep/er/b.py": ""}, BASE)
    admitted, missing = spine_gate.resolve(root, BASE)
    assert admitted == ["core/a.py", "core/deep/er/b.py"] and missing == []
