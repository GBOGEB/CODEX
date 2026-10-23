from __future__ import annotations

import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import uuid
import zipfile
from collections.abc import Iterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src import archive_audit as aa


def _zip(path: Path, files: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return path


def _targz(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


@pytest.fixture()
def repo(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    # Not under tmp_path: on Windows + Python 3.12 pytest's 0o700 dirs get an owner-only ACL
    # that a sandboxed git cannot enter.
    r = Path(tempfile.gettempdir()) / f"archive_audit_repo_{uuid.uuid4().hex}"
    os.makedirs(r)
    # an elevated shell creates the dir owned by Administrators; trust only this test repo
    # (and present it as a GitHub clone without writing .git/config)
    monkeypatch.setenv("GIT_CONFIG_COUNT", "2")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "safe.directory")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", r.as_posix())
    monkeypatch.setenv("GIT_CONFIG_KEY_1", "remote.origin.url")
    monkeypatch.setenv("GIT_CONFIG_VALUE_1", "https://github.com/acme/demo.git")

    def run(*args: str) -> None:
        cfg = ["-c", "core.autocrlf=false", "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "-C", str(r), *cfg, *args], check=True, capture_output=True)

    run("init", "-q")
    (r / "code.py").write_bytes(b"print('hi')\n")
    (r / "pkg").mkdir()
    (r / "pkg" / "mod.py").write_bytes(b"VERSION = 2\n")
    run("add", ".")
    run("commit", "-qm", "Add code (#42)")
    run("update-ref", "refs/remotes/origin/main", "HEAD")  # everything so far is "pushed"
    (r / "local.py").write_bytes(b"unpushed = True\n")
    run("add", ".")
    run("commit", "-qm", "local only")
    yield r
    shutil.rmtree(r, onerror=lambda f, p, _: (os.chmod(p, stat.S_IWRITE), f(p)))


def test_git_blob_sha1_matches_git(repo: Path) -> None:
    out = subprocess.run(["git", "-C", str(repo), "hash-object", "code.py"], capture_output=True, check=True)
    assert aa._git_blob_sha1(b"print('hi')\n") == out.stdout.decode().strip()


def test_nested_targz_members_are_listed(tmp_path: Path) -> None:
    inner = _targz({"pkg/a.txt": b"alpha"})
    z = _zip(tmp_path / "outer.zip", {"inner.tar.gz": inner, "b.txt": b"beta"})
    with open(z, "rb") as f:
        names = {m.name for m in aa.iter_members(f)}
    assert names == {"inner.tar.gz", "inner.tar.gz!/pkg/a.txt", "b.txt"}


def test_truncated_nested_archive_is_judged_as_a_blob(tmp_path: Path) -> None:
    whole = _zip(tmp_path / "whole.zip", {"a.txt": b"alpha" * 1000, "b.txt": b"beta" * 1000})
    z = _zip(tmp_path / "outer.zip", {"inner.zip": whole.read_bytes()[:-60]})
    with open(z, "rb") as f:
        members = list(aa.iter_members(f))
    assert [(m.name, m.is_archive) for m in members] == [("inner.zip", False)]


def test_verdicts(tmp_path: Path, repo: Path) -> None:
    loose = tmp_path / "disk"
    loose.mkdir()
    (loose / "copy.txt").write_bytes(b"on disk elsewhere")
    arch = tmp_path / "arch"
    arch.mkdir()
    # CRLF variant of a committed file still counts as in git
    safe = _zip(arch / "safe.zip", {"code.py": b"print('hi')\r\n", "x/copy.txt": b"on disk elsewhere",
                                    "__pycache__/m.pyc": b"junk"})
    big = _zip(arch / "big.zip", {"only.txt": b"unique payload", "more.txt": b"more unique"})
    small = _zip(arch / "small.zip", {"only.txt": b"unique payload"})
    gen = _zip(arch / "gen.zip", {"outputs/report.html": b"<html>generated</html>"})
    unpushed = _zip(arch / "unpushed.zip", {"local.py": b"unpushed = True\n"})
    old = _zip(arch / "old_cryo_pack.zip", {"handover/pkg/mod.py": b"VERSION = 1\n"})
    personal = _zip(arch / "Aanslagbiljet 2023.zip", {"scan.pdf": b"%PDF private"})
    broken = arch / "broken.zip"
    broken.write_bytes(big.read_bytes()[:40])

    cache = aa.Cache(tmp_path / "out" / "c.sqlite")
    paths = [safe, big, small, gen, unpushed, old, personal, broken]
    v = {Path(x.path).name: x for x in aa.audit(paths, cache, [repo], [loose], log=lambda *_: None)}

    assert v["safe.zip"].verdict == "SAFE_LOSSLESS"
    assert v["safe.zip"].disposition == "DELETE_OK"
    assert (v["safe.zip"].covered_git, v["safe.zip"].covered_disk, v["safe.zip"].trivial) == (1, 1, 1)
    assert v["safe.zip"].provenance[0]["pr"] == "42"
    assert v["safe.zip"].repos == {"acme/demo": 1}
    assert v["unpushed.zip"].verdict == "SAFE_LOCAL_GIT"
    assert v["unpushed.zip"].disposition == "PUSH_THEN_DELETE"
    assert v["old_cryo_pack.zip"].superseded_git == 1
    assert v["old_cryo_pack.zip"].disposition == "REVIEW_SUPERSEDED"
    assert v["old_cryo_pack.zip"].lane == "GBOGEB/cryoplant-project"
    assert v["Aanslagbiljet 2023.zip"].disposition == "KEEP_PRIVATE"
    assert v["big.zip"].verdict == "KEEP"
    assert v["small.zip"].verdict == "SAFE_REDUNDANT"
    assert v["small.zip"].keepers == [str(big)]
    assert v["gen.zip"].verdict == "SAFE_IF_REGENERABLE"
    assert v["broken.zip"].verdict == "ERROR"

    receipt = aa.aggregate_receipt(list(v.values()), "0" * 64, None)
    text = json.dumps(receipt)
    assert "big.zip" not in text and "only.txt" not in text and "Aanslagbiljet" not in text
    assert receipt["verdicts"]["SAFE_LOSSLESS"]["archives"] == 1


def test_cache_resumes_without_rehash(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    z = _zip(tmp_path / "a.zip", {"f.txt": b"x"})
    cache = aa.Cache(tmp_path / "c.sqlite")
    first = cache.scan_archive(z)
    monkeypatch.setattr(aa, "file_sha256", lambda p: pytest.fail("rehashed"))
    assert cache.scan_archive(z) == first


def test_prune_keeps_grouping(tmp_path: Path) -> None:
    arch = tmp_path / "Master_Input"
    arch.mkdir()
    big = _zip(arch / "big.zip", {"a.txt": b"alpha", "b.txt": b"beta", "c.txt": b"gamma"})
    mid = _zip(arch / "mid.zip", {"x/a.txt": b"alpha", "x/b.txt": b"beta", "__pycache__/z.pyc": b"junk"})
    small = _zip(arch / "small.zip", {"a.txt": b"alpha"})
    split = _zip(arch / "split.zip", {"b.txt": b"beta", "other.txt": b"other"})
    spread = _zip(arch / "spread.zip", {"c.txt": b"gamma", "other.txt": b"other"})  # needs two keepers: stays
    private = _zip(arch / "Aanslagbiljet 2023.zip", {"a.txt": b"alpha"})  # personal: never auto-pruned
    files = {
        "big/a.txt": b"alpha", "big/sub/c.txt": b"gamma",  # extracted copy of big.zip
        "mid_extract/a.txt": b"alpha",  # *extract* folder, content inside big.zip
        "notes/a.txt": b"alpha",  # same bytes, but not named like an unpacked archive
        "edited/a.txt": b"alpha (edited)",
        "split/b.txt": b"beta", "split/mine.md": b"own work",  # partly own work: whole folder stays
        "spread/c.txt": b"gamma", "spread/.git/HEAD": b"ref",  # a clone is never pruned
    }
    for rel, data in files.items():
        (arch / rel).parent.mkdir(parents=True, exist_ok=True)
        (arch / rel).write_bytes(data)

    cache = aa.Cache(tmp_path / "c.sqlite")
    actions = aa.plan_prune([big, mid, small, split, spread, private], cache, [arch])
    got = {(a.kind, Path(a.path).name): Path(a.keeper).name for a in actions}
    assert got == {
        ("archive", "small.zip"): "big.zip",
        ("archive", "mid.zip"): "big.zip",
        ("folder", "big"): "big.zip",
        ("folder", "mid_extract"): "big.zip",
    }
    mid_action = next(a for a in actions if a.path == str(mid))
    assert sorted(n for n, *_ in mid_action.manifest) == ["__pycache__/z.pyc", "x/a.txt", "x/b.txt"]

    aa.apply_prune(actions, cache)
    assert all(a.applied for a in actions)
    assert not small.exists() and not mid.exists() and not (arch / "big").exists()
    for kept in ("notes", "edited", "split", "spread"):
        assert (arch / kept).exists()
    assert big.exists() and spread.exists() and private.exists()


def test_prune_follows_keeper_chain(tmp_path: Path) -> None:
    a = _zip(tmp_path / "a.zip", {"1": b"one"})
    b = _zip(tmp_path / "b.zip", {"1": b"one", "2": b"two"})
    c = _zip(tmp_path / "c.zip", {"1": b"one", "2": b"two", "3": b"three"})
    actions = aa.plan_prune([a, b, c], aa.Cache(tmp_path / "c.sqlite"), [])
    assert {Path(x.path).name: Path(x.keeper).name for x in actions} == {"a.zip": "c.zip", "b.zip": "c.zip"}


def test_apply_skips_when_keeper_changed(tmp_path: Path) -> None:
    small = _zip(tmp_path / "small.zip", {"1": b"one"})
    big = _zip(tmp_path / "big.zip", {"1": b"one", "2": b"two"})
    cache = aa.Cache(tmp_path / "c.sqlite")
    actions = aa.plan_prune([small, big], cache, [])
    _zip(big, {"2": b"two"})  # keeper rewritten after planning
    os.utime(big, ns=(1, 1))
    aa.apply_prune(actions, cache)
    assert small.exists() and not actions[0].applied
