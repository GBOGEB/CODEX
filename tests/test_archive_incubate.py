from __future__ import annotations

import io
import os
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
import uuid
import zipfile
from collections.abc import Iterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src import archive_audit as aa
from src import archive_incubate as ai

# built at runtime so this file never holds a token-shaped literal
FAKE_KEY = b"sk-" + b"q7Rz" * 6


def _zip(path: Path, files: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return path


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return buf.getvalue()


@pytest.fixture()
def git_repo(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    # Not under tmp_path: on Windows + Python 3.12 pytest's 0o700 dirs get an owner-only ACL
    # that a sandboxed git cannot enter (same as tests/test_archive_audit.py).
    r = Path(tempfile.gettempdir()) / f"archive_incubate_repo_{uuid.uuid4().hex}"
    os.makedirs(r)
    # an elevated shell creates the dir owned by Administrators; trust only this test repo
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "safe.directory")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", r.as_posix())
    subprocess.run(["git", "init", "-q", str(r)], check=True, capture_output=True)
    yield r
    shutil.rmtree(r, onerror=lambda f, p, _: (os.chmod(p, stat.S_IWRITE), f(p)))


def _git(r: Path, *args: str, stdin: bytes | None = None) -> bytes:
    cfg = ["-c", "core.ignorecase=false", "-c", "core.autocrlf=false"]
    return subprocess.run(["git", "-C", str(r), *cfg, *args], input=stdin, check=True, capture_output=True).stdout


@pytest.fixture()
def audited(tmp_path: Path) -> tuple[list[dict], sqlite3.Connection]:
    arch = tmp_path / "arch"
    arch.mkdir()
    _zip(arch / "cryo_tools.zip", {
        "tools/flow.py": b"def flow(x):\n    return 2 * x\n\n\ndef test_flow():\n    assert flow(2) == 4\n",
        "tools/notes.md": b"# flow notes\n",
        "tools/.env": b"API=1\n",
        "tools/plot.png": b"\x89PNG not really",
        "tools/keys.py": b"KEY = '" + FAKE_KEY + b"'\n",
        "tools/inner.zip": _zip_bytes({"deep/helper.py": b"HELPER = 1\n"}),
        "tools/vendored/.git/config": b"[core]\n",
        "tools/sh.exe.stackdump": b"junk",
        "tools/Report.txt": b"upper case\n",
        "tools/report.txt": b"lower case\n",
    })
    _zip(arch / "qps_docs.zip", {"spec/broken.yaml": b"a: [1, 2\n", "spec/intro.md": b"intro\n"})
    _zip(arch / "loose_bundle.zip", {"bundle/run.ps1": b"Write-Output 1\n"})
    _zip(arch / "parked.zip", {"parked/a.txt": b"parked only\n"})
    cache = aa.Cache(tmp_path / "c.sqlite")
    paths = sorted(arch.iterdir())
    verdicts = aa.audit(paths, cache, [], [], provenance=False, log=lambda *_: None)
    return [v.__dict__ for v in verdicts], cache.db


def test_repo_path_is_safe_and_flattens_nesting() -> None:
    assert ai.repo_path("pkg/inner.zip!/deep/a.py") == "pkg/inner.zip.d/deep/a.py"
    assert ai.repo_path("data.json.gz!/<gunzip>") == "data.json"
    assert ai.repo_path("../escape.py") is None
    assert ai.repo_path("a/b:c?.txt") == "a/b_c_.txt"
    assert ai.repo_path("con.txt") == "con.txt_"
    assert ai.stem("Bundle v1.tar.gz") == "Bundle v1"


def test_smoke_parses_without_running() -> None:
    assert ai.smoke("a.py", b"import os\nos.remove('x')\n\ndef test_a():\n    pass\n") == ("py_compile", "ok", 1)
    assert ai.smoke("a.py", b"def (:\n") == ("py_compile", "fail: SyntaxError", 0)
    assert ai.smoke("a.yaml", b"a: [1\n") == ("yaml", "fail: ParserError", 0)
    assert ai.smoke("a.json", b"{}") == ("json", "ok", 0)
    assert ai.smoke("a.toml", b"x = 1\n") == ("toml", "ok", 0)
    assert ai.smoke("a.md", b"# hi\n") == ("none", None, 0)


def test_member_status_keeps_secrets_and_binaries_out() -> None:
    import hashlib

    def st(name: str, data: bytes | None) -> str:
        return ai.member_status(name, len(data or b""), hashlib.sha256(data or b"").hexdigest(), data)

    assert st("x/.env", b"A=1") == "excluded:credential_name"
    assert st("x/github_token.txt", b"t") == "excluded:credential_name"
    assert st("x/run.py", b"K='" + FAKE_KEY + b"'") == "excluded:secret_pattern"
    assert st("x/Belasting 2023.txt", b"t") == "excluded:private_name"
    assert st("x/taxonomy.md", b"t") == "committed"
    assert st("x/a.pdf", b"%PDF") == "kept_in_zip:binary"
    assert st("x/blob.txt", b"a\0b") == "kept_in_zip:binary"
    assert st("x/repo/.git/HEAD", b"ref") == "kept_in_zip:git_internals"
    assert st("x/__pycache__/m.pyc", b"j") == "excluded:junk"
    assert ai.member_status("x/big.txt", ai.MAX_TEXT + 1, "0", None) == "kept_in_zip:large"
    assert ai.member_status("x/a.txt", 1, "0" * 64, b"a") == "kept_in_zip:hash_mismatch"


def test_plan_routes_verdicts_and_payloads(audited: tuple[list[dict], sqlite3.Connection]) -> None:
    report, db = audited
    assert {Path(v["path"]).name: v["disposition"] for v in report} == dict.fromkeys(
        ["cryo_tools.zip", "qps_docs.zip", "loose_bundle.zip", "parked.zip"], "INCUBATE")
    routing = {"leave": ["parked.zip"], "triage": {"loose_bundle.zip": "codex"}}
    manifests, payload = ai.plan(report, db, routing, log=lambda *_: None)
    assert set(manifests) == {"cryoplant", "incubator"}
    a = {x["archive"]: x for land in manifests.values() for x in land["archives"]}

    tools = a["cryo_tools.zip"]
    assert (tools["target"], tools["folder"], tools["verdict"]) == ("cryoplant-project", "cryo_tools", "MERGE")
    st = {r["name"]: (r["status"], r["path"]) for r in tools["members"]}
    assert st["tools/flow.py"] == ("committed", "cryo_tools/tools/flow.py")
    assert st["tools/inner.zip!/deep/helper.py"] == ("committed", "cryo_tools/tools/inner.zip.d/deep/helper.py")
    assert st["tools/.env"][0] == "excluded:credential_name"
    assert st["tools/keys.py"][0] == "excluded:secret_pattern"
    assert st["tools/plot.png"][0] == "kept_in_zip:binary"
    assert st["tools/vendored/.git/config"][0] == "kept_in_zip:git_internals"
    assert st["tools/sh.exe.stackdump"][0] == "excluded:junk"
    # paths that differ only in case both land, the later one suffixed
    assert {st["tools/Report.txt"][1], st["tools/report.txt"][1]} == {
        "cryo_tools/tools/Report.txt", "cryo_tools/tools/report~2.txt"}
    assert tools["tests_found_statically"] == 1

    assert (a["qps_docs.zip"]["verdict"], a["qps_docs.zip"]["smoke"]) == ("BRIDGE", {"yaml_fail": 1})
    assert (a["loose_bundle.zip"]["target"], a["loose_bundle.zip"]["folder"]) == ("codex", "codex/loose_bundle")
    assert a["loose_bundle.zip"]["verdict"] == "MERGE"
    assert (a["parked.zip"]["verdict"], a["parked.zip"]["folder"]) == ("LEAVE", None)
    assert a["parked.zip"]["counts"] == {"kept_in_zip:leave": 1}

    files = payload["cryoplant"]
    assert files["cryo_tools/tools/flow.py"].startswith(b"def flow")
    assert not any(FAKE_KEY in b for land in payload.values() for b in land.values())
    assert "codex/loose_bundle/bundle/run.ps1" in payload["incubator"]
    md = ai.manifest_markdown(manifests["cryoplant"], "W999 incubator")
    assert "| `cryo_tools.zip` | cryoplant-project | `cryo_tools/` | MERGE |" in md


def test_fast_import_round_trip_verifies(audited: tuple[list[dict], sqlite3.Connection], git_repo: Path) -> None:
    report, db = audited
    manifests, payload = ai.plan(report, db, {"leave": ["parked.zip"]}, log=lambda *_: None)
    stream = ai.fast_import_stream({"inc/" + k: v for k, v in payload["cryoplant"].items()} | {"README.md": b"hi\n"},
                                   "incubate", b"incubate\n", "t <t@t>", when=1_700_000_000)
    _git(git_repo, "fast-import", "--quiet", stdin=stream)
    ok = ai.verify_tree(git_repo, "refs/heads/incubate", manifests["cryoplant"], "inc/")
    assert (ok["committed_in_manifest"], ok["missing"], ok["hash_mismatch"], ok["unexpected"]) == (
        len(payload["cryoplant"]), 0, 0, [])
    # the README outside the prefix is not counted; a stray file inside it is
    head = _git(git_repo, "rev-parse", "refs/heads/incubate").decode().strip()
    stray = ai.fast_import_stream({"inc/stray.txt": b"x"}, "incubate", b"stray\n", "t <t@t>",
                                  base=head, when=1_700_000_001)
    _git(git_repo, "fast-import", "--quiet", stdin=stray)
    bad = ai.verify_tree(git_repo, "refs/heads/incubate", manifests["cryoplant"], "inc/")
    assert not bad["ok"] and bad["unexpected"] == ["inc/stray.txt"]
    assert ai.verify_tree(git_repo, "refs/heads/incubate", manifests["cryoplant"], "inc/", {"inc/stray.txt"})["ok"]


def test_scan_reports_rules_not_values() -> None:
    hits = ai.scan_credentials({
        "a/config.py": b"api_key = '" + b"Zx9" * 8 + b"'\n",
        "a/example.py": b"api_key = 'your-api-key-goes-here-123456'\n",
        "a/env.py": b"token = os.environ['TOKEN_VALUE_FROM_ENV_1234']\n",
        "a/url.txt": b"https://bob:hunter22@example.org/x\n",
        "a/clean.md": b"nothing here\n",
    })
    assert hits == {"a/config.py": ["assigned_secret"]}
    assert all("Zx9" not in r for rules in hits.values() for r in rules)


def test_cli_plan_and_markdown(audited: tuple[list[dict], sqlite3.Connection], tmp_path: Path) -> None:
    import json

    report, db = audited
    db.close()
    (tmp_path / "report.json").write_text(json.dumps(report), encoding="utf-8")
    (tmp_path / "routing.json").write_text(json.dumps({"leave": ["parked.zip"]}), encoding="utf-8")
    out = tmp_path / "inc"
    assert ai.main(["plan", "--report", str(tmp_path / "report.json"), "--cache", str(tmp_path / "c.sqlite"),
                    "--out", str(out), "--routing", str(tmp_path / "routing.json"),
                    "--source-root", str(tmp_path)]) == 0
    man = json.loads((out / "cryoplant_manifest.json").read_text(encoding="utf-8"))
    assert {x["source"] for x in man["archives"]} >= {"arch/cryo_tools.zip"}
    assert man["engine"].startswith("GBOGEB/CODEX src/archive_audit.py @ ")
    assert ai.main(["scan", str(out / "cryoplant_payload.json")]) == 0
    assert ai.main(["markdown", str(out / "cryoplant_manifest.json"), str(out / "M.md")]) == 0
    assert (out / "M.md").read_bytes().count(b"\r\n") == 0
