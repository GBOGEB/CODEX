"""Archive dedup audit: decide which ZIP/TAR handover bundles can be deleted losslessly.

Companion to :mod:`src.zip_pipeline` (which *creates* archives).  This module
reads existing archives, hashes every member (recursing into nested
archives) and checks where else each byte-identical member lives:

* **git** - the member is a blob in a local repository (any ref, any commit,
  including blobs only referenced by trees of a partial clone).  Text members
  are also checked with CRLF normalised to LF, because git stores LF.
* **disk** - a byte-identical file exists outside the audited archives.
* **archive** - the member exists only inside other audited archives; a greedy
  keeper set is chosen so that every archive-only blob is retained once.

Each archive then receives a verdict:

``SAFE_LOSSLESS``      every substantive member is in pushed git history or on disk.
``SAFE_LOCAL_GIT``     as above, but some members exist only in unpushed local
                       git objects (push first).
``SAFE_REDUNDANT``     the remainder is inside a kept archive (delete only
                       while the keeper is retained).
``SAFE_IF_REGENERABLE`` the remainder is generated output (``outputs/``,
                       ``dist/``...) - lossless only if the generator in git
                       still reproduces it.
``REDOWNLOADABLE``     a public third-party package.
``KEEP``               holds blobs found nowhere else.
``ERROR``              unreadable/truncated archive.

All state is kept in a SQLite cache keyed by archive SHA-256 so that a long run
can be interrupted and resumed, and identical archives are hashed once.
Reports with member names stay local; :func:`aggregate_receipt` produces a
name-free summary suitable for committing as Golden Thread / Mycelium evidence.
"""

from __future__ import annotations

import argparse
import fnmatch
import gzip
import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
import zlib
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

ARCHIVE_EXTS = (".zip", ".tar", ".tgz", ".tar.gz", ".gz")
TRIVIAL_GLOBS = (
    "*/__pycache__/*", "*.pyc", "*/.pytest_cache/*", "*/node_modules/*", "*/.ipynb_checkpoints/*",
    "*.DS_Store", "*Thumbs.db", "*/~$*", "~$*", "__MACOSX/*", "*/__MACOSX/*", "*.lock.tmp",
)
GENERATED_GLOBS = (
    "output/*", "outputs/*", "*/output/*", "*/outputs/*", "dist/*", "*/dist/*", "build/*",
    "*/build/*", "*/generated/*", "generated/*", "*/site/*", "*/_site/*", "*/rendered/*",
)
REDOWNLOADABLE_GLOBS = ("node-v*-win-x64.zip", "claude-code-jetbrains-plugin-*.zip")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "AppData", ".pytest_cache", "$RECYCLE.BIN"}
# FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS | RECALL_ON_OPEN | OFFLINE: reading would hydrate a cloud file.
CLOUD_ATTRS = 0x400000 | 0x40000 | 0x1000
NESTED_LIMIT = 512 * 1024 * 1024
TEXT_LIMIT = 32 * 1024 * 1024
PR_RE = re.compile(r"#(\d+)")
# truncated/corrupt/encrypted/unsupported-compression archives
READ_ERRORS = (ValueError, zipfile.BadZipFile, tarfile.TarError, EOFError, OSError, zlib.error,
               NotImplementedError, RuntimeError)


# ---------------------------------------------------------------------------
# Hashing


@dataclass
class Digest:
    size: int
    sha256: str
    git_sha1: str
    git_sha1_lf: str | None  # CRLF->LF variant for text members with CRLF


def _git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def digest_stream(stream: BinaryIO, size: int) -> Digest:
    """Hash a stream of known size: sha256, git blob sha1 and the LF variant."""

    if size <= TEXT_LIMIT:
        data = stream.read()
        lf = None
        if b"\r\n" in data and b"\0" not in data[:8192]:
            lf = _git_blob_sha1(data.replace(b"\r\n", b"\n"))
        return Digest(len(data), hashlib.sha256(data).hexdigest(), _git_blob_sha1(data), lf)
    h256, h1 = hashlib.sha256(), hashlib.sha1(b"blob %d\0" % size)
    for chunk in iter(lambda: stream.read(1 << 20), b""):
        h256.update(chunk)
        h1.update(chunk)
    return Digest(size, h256.hexdigest(), h1.hexdigest(), None)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Archive reading


@dataclass
class Member:
    name: str  # nested members use "outer!/inner"
    digest: Digest
    is_archive: bool = False


def _looks_archive(name: str) -> bool:
    low = name.lower()
    return low.endswith(ARCHIVE_EXTS)


def sniff_kind(head: bytes) -> str | None:
    if head[:4] == b"PK\x03\x04" or head[:4] == b"PK\x05\x06":
        return "zip"
    if head[:2] == b"\x1f\x8b":
        return "gz"
    if len(head) > 262 and head[257:262] == b"ustar":
        return "tar"
    return None


def iter_members(fileobj: BinaryIO, prefix: str = "") -> Iterator[Member]:
    """Yield every member of a zip/tar/tar.gz/gz stream, recursing into nested archives."""

    head = fileobj.read(512)
    fileobj.seek(0)
    kind = sniff_kind(head)
    if kind == "zip":
        with zipfile.ZipFile(fileobj) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                with zf.open(info) as m:
                    yield from _member(prefix + info.filename, m, info.file_size)
    elif kind in ("gz", "tar") and _is_tar(fileobj):
        with tarfile.open(fileobj=fileobj, mode="r:*") as tf:
            for info in tf:
                if not info.isfile():
                    continue
                m = tf.extractfile(info)
                if m is not None:
                    yield from _member(prefix + info.name, m, info.size)
    elif kind == "gz":  # plain gzip of a single file
        with gzip.GzipFile(fileobj=fileobj) as g, tempfile.SpooledTemporaryFile(64 << 20) as spool:
            for chunk in iter(lambda: g.read(1 << 20), b""):
                spool.write(chunk)
            size = spool.tell()
            spool.seek(0)
            yield from _member(prefix + "<gunzip>", spool, size)
    else:
        raise ValueError("not a zip/tar/gz archive")


def _is_tar(fileobj: BinaryIO) -> bool:
    try:
        with tarfile.open(fileobj=fileobj, mode="r:*") as tf:
            tf.next()
        return True
    except READ_ERRORS:
        return False
    finally:
        fileobj.seek(0)


def _member(name: str, stream: BinaryIO, size: int) -> Iterator[Member]:
    if _looks_archive(name) and size <= NESTED_LIMIT:
        with tempfile.SpooledTemporaryFile(64 << 20) as spool:
            for chunk in iter(lambda: stream.read(1 << 20), b""):
                spool.write(chunk)
            spool.seek(0)
            digest = digest_stream(spool, size)
            spool.seek(0)
            try:
                inner = list(iter_members(spool, name + "!/"))
            except READ_ERRORS:
                # not an archive after all, or truncated: the blob itself must then be covered
                yield Member(name, digest)
                return
            yield Member(name, digest, is_archive=True)
            yield from inner
        return
    yield Member(name, digest_stream(stream, size))


# ---------------------------------------------------------------------------
# Cache


SCHEMA = """
create table if not exists archives(path text primary key, size int, mtime_ns int, sha256 text, error text);
create table if not exists members(archive_sha256 text, name text, size int, sha256 text,
    git_sha1 text, git_sha1_lf text, is_archive int);
create index if not exists members_arch on members(archive_sha256);
create table if not exists disk(path text primary key, size int, mtime_ns int, sha256 text);
"""


class Cache:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), timeout=60)
        self.db.executescript(SCHEMA)

    def archive_sha(self, path: Path) -> tuple[str | None, str | None]:
        st = path.stat()
        row = self.db.execute(
            "select sha256, error from archives where path=? and size=? and mtime_ns=?",
            (str(path), st.st_size, st.st_mtime_ns),
        ).fetchone()
        return (row[0], row[1]) if row else (None, None)

    def scan_archive(self, path: Path) -> tuple[str, str | None]:
        """Hash an archive and its members once; returns (sha256, error)."""

        sha, err = self.archive_sha(path)
        if sha:
            return sha, err
        st = path.stat()
        sha = file_sha256(path)
        known = self.db.execute("select 1 from members where archive_sha256=? limit 1", (sha,)).fetchone()
        err = None
        if not known:
            rows = []
            try:
                with open(path, "rb") as f:
                    for m in iter_members(f):
                        d = m.digest
                        rows.append((sha, m.name, d.size, d.sha256, d.git_sha1, d.git_sha1_lf, int(m.is_archive)))
            except READ_ERRORS as exc:  # truncated or corrupt: keep what was read, flag the archive
                err = f"{type(exc).__name__}: {exc}"[:300]
            self.db.executemany("insert into members values(?,?,?,?,?,?,?)", rows)
        self.db.execute("insert or replace into archives values(?,?,?,?,?)", (str(path), st.st_size, st.st_mtime_ns, sha, err))
        self.db.commit()
        return sha, err

    def members(self, sha: str) -> list[tuple]:
        return self.db.execute(
            "select name, size, sha256, git_sha1, git_sha1_lf, is_archive from members where archive_sha256=?", (sha,)
        ).fetchall()

    def disk_sha(self, path: str, size: int, mtime_ns: int) -> str | None:
        row = self.db.execute("select sha256 from disk where path=? and size=? and mtime_ns=?", (path, size, mtime_ns)).fetchone()
        if row:
            return row[0]
        try:
            sha = file_sha256(Path(path))
        except OSError:
            return None
        self.db.execute("insert or replace into disk values(?,?,?,?)", (path, size, mtime_ns, sha))
        return sha


# ---------------------------------------------------------------------------
# Git index


@dataclass
class GitHit:
    repo: str
    path: str
    pushed: bool = False


def discover_repos(roots: Iterable[Path], max_depth: int = 3) -> list[Path]:
    """Find git repositories (deduplicated by common dir, so worktrees count once)."""

    found: dict[str, Path] = {}
    for root in roots:
        root = Path(root)
        if not root.is_dir():
            continue
        base = len(root.parts)
        for dp, dns, _ in os.walk(root):
            depth = len(Path(dp).parts) - base
            if ".git" in dns or os.path.isfile(os.path.join(dp, ".git")):
                common = _git(Path(dp), "rev-parse", "--path-format=absolute", "--git-common-dir")
                if common:
                    found.setdefault(os.path.normcase(common.strip()), Path(dp))
            dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")] if depth < max_depth else []
    return sorted(found.values())


def _git(repo: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.decode("utf-8", "replace")


def git_blob_index(repos: Iterable[Path], paths: dict[str, GitHit] | None = None) -> dict[str, GitHit]:
    """Map every blob id in the local object stores to a repo path.

    Blobs reachable from a remote-tracking ref are marked ``pushed`` (they survive
    deletion of the local clone); blobs only on local branches or unreachable are not.
    When ``paths`` is given it is filled with ``path tail -> hit`` for every tree entry,
    which :func:`_tail` uses to detect same-path successors with different content.
    """

    index: dict[str, GitHit] = {}
    for repo in repos:
        name = _remote_name(repo)
        hosted = "/" in name and ":" not in name
        for refs, pushed in (("--remotes", hosted), ("--all", False)):
            listing = _git(repo, "rev-list", "--objects", refs, "--missing=print") or ""
            for line in listing.splitlines():
                sha, _, path = line.lstrip("?").partition(" ")
                if not path:
                    continue
                hit = GitHit(name, path, pushed)
                old = index.get(sha)
                if old is None or (pushed and not old.pushed):
                    index[sha] = hit
                if paths is not None:
                    paths.setdefault(_tail(path), hit)
        loose = _git(repo, "cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype)") or ""
        for line in loose.splitlines():
            sha, _, kind = line.partition(" ")
            if kind == "blob":
                index.setdefault(sha, GitHit(name, "<unreachable blob>"))
    return index


GENERIC_NAMES = {"readme.md", "readme.txt", "index.html", "__init__.py", "requirements.txt", "package.json",
                 "manifest.json", "manifest.yaml", "config.yaml", "config.json", "main.py", "app.py", "license"}


def _tail(name: str) -> str:
    """Last two path components (lower-case); a lone generic basename is too ambiguous to use."""

    parts = name.rsplit("!/", 1)[-1].replace("\\", "/").lower().split("/")
    if len(parts) >= 2:
        return "/".join(parts[-2:])
    return "" if parts[0] in GENERIC_NAMES else parts[0]


def _remote_name(repo: Path) -> str:
    url = (_git(repo, "config", "--get", "remote.origin.url") or "").strip()
    m = re.search(r"github\.com[/:]([^/]+/[^/.]+)", url)
    return m.group(1) if m else str(repo)


def introducing_commit(repo: Path, blob: str) -> tuple[str, str, str | None] | None:
    """Oldest commit (any ref) that introduced ``blob``: (sha, subject, PR number)."""

    out = _git(repo, "log", "--all", "--format=%H%x09%s", f"--find-object={blob}")
    if not out:
        return None
    sha, _, subject = out.strip().splitlines()[-1].partition("\t")
    pr = PR_RE.findall(subject)
    return sha, subject, pr[-1] if pr else None


# ---------------------------------------------------------------------------
# Disk index


def disk_size_index(roots: Iterable[Path], wanted_sizes: set[int], exclude: set[str]) -> tuple[dict[int, list], list[str]]:
    """Paths whose size matches a wanted size; cloud-only matches are listed but never read."""

    by_size: dict[int, list] = defaultdict(list)
    cloud: list[str] = []
    seen: set[str] = set()
    for root in roots:
        for dp, dns, fns in os.walk(root):
            dns[:] = [d for d in dns if d not in SKIP_DIRS]
            for fn in fns:
                p = os.path.join(dp, fn)
                key = os.path.normcase(os.path.abspath(p))
                if key in seen or key in exclude:
                    continue
                seen.add(key)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                if st.st_size not in wanted_sizes:
                    continue
                if getattr(st, "st_file_attributes", 0) & CLOUD_ATTRS:
                    cloud.append(p)
                    continue
                by_size[st.st_size].append((p, st.st_mtime_ns))
    return by_size, cloud


# ---------------------------------------------------------------------------
# Classification


@dataclass
class ArchiveVerdict:
    path: str
    sha256: str
    size: int
    verdict: str = "KEEP"
    error: str | None = None
    members: int = 0
    covered_git: int = 0
    covered_disk: int = 0
    trivial: int = 0
    generated_only: list[str] = field(default_factory=list)
    archive_only: list[str] = field(default_factory=list)  # member names whose blob is nowhere else
    orphan_bytes: int = 0
    keepers: list[str] = field(default_factory=list)
    duplicate_of: str | None = None
    repos: dict[str, int] = field(default_factory=dict)
    provenance: list[dict] = field(default_factory=list)
    disk_examples: list[str] = field(default_factory=list)
    covered_git_local: int = 0  # git hits only on local branches / unpushed / unreachable objects
    disk_locations: dict[str, int] = field(default_factory=dict)
    superseded_git: int = 0  # archive-only members whose path tail exists in git with other content
    superseded_archive: int = 0  # ... or in a newer audited archive
    superseded_examples: list[str] = field(default_factory=list)
    lane: str = ""
    disposition: str = ""


# Lane routing for archive-only content, first match wins (archive file name, case-insensitive).
PRIVATE_RE = re.compile(r"aanslagbiljet|sars_|account-documents|applicant|belasting|tax", re.IGNORECASE)
LANES = (
    (re.compile(r"abacus|tuplebridge", re.IGNORECASE), "GBOGEB/ABACUS"),
    (re.compile(r"gg_math|pca|nlpca", re.IGNORECASE), "gg_MATH"),
    (re.compile(r"mycelium|golden_thread|code.purple|codex|federation|mip_|jade|pulse|github_repos|master.?input|"
                r"ruleset|gbogeb|gbogeg|workspace_intelligence|renderer_governance|p-process|handover_process|"
                r"handover_testing|hbhs", re.IGNORECASE), "GBOGEB/CODEX"),
    (re.compile(r"dmaic|recursive|phase0", re.IGNORECASE), "GBOGEB/dmaic-recursive-pipeline"),
    (re.compile(r"qps|qplant|qcell|cryo|helium|pid|pfd|lkt|dsbt|icd|offer|valve|pressure|heatload|gistau|"
                r"weis|kaezer|leak|cost|cyber|component|minerva|nfs_|sline|s_line|section_9|material|"
                r"\bad_|flow schemes|3d_model|building|rtm|wcs|deepagent|figures|architecture|pvps|put_rt",
                re.IGNORECASE), "GBOGEB/cryoplant-project"),
)


def lane_for(archive_name: str) -> str:
    if PRIVATE_RE.search(archive_name):
        return "PRIVATE"
    return next((lane for rx, lane in LANES if rx.search(archive_name)), "TRIAGE")


def _location(path: str) -> str:
    """Coarse place a covering copy lives, so a user does not delete the copy and the archive together."""

    p = path.replace("\\", "/")
    for marker, label in (("/Master_Input/", "OneDrive/Master_Input"), ("/OneDrive - ", "OneDrive"),
                          ("/upd/work/", "work:")):
        if marker in p:
            if label == "work:":
                return "work/" + p.split(marker, 1)[1].split("/", 1)[0]
            return label
    rel = p.split("/Users/", 1)[-1].split("/")
    return "/".join(rel[1:2]) or p


def _match(name: str, globs: Iterable[str]) -> bool:
    low = name.replace("\\", "/")
    return any(fnmatch.fnmatch(low, g) for g in globs)


def audit(
    archives: list[Path],
    cache: Cache,
    repos: list[Path],
    disk_roots: list[Path],
    provenance: bool = True,
    log=print,
) -> list[ArchiveVerdict]:
    verdicts: list[ArchiveVerdict] = []
    for i, path in enumerate(archives, 1):
        sha, err = cache.scan_archive(path)
        verdicts.append(ArchiveVerdict(str(path), sha, path.stat().st_size, error=err))
        log(f"[scan {i}/{len(archives)}] {path.name}{' ERROR ' + err if err else ''}")

    gpaths: dict[str, GitHit] = {}
    gindex = git_blob_index(repos, gpaths)
    log(f"[git] {len(gindex)} blob ids ({sum(h.pushed for h in gindex.values())} pushed) from {len(repos)} repos")
    # provenance lookups need full history: prefer a non-shallow clone of each remote
    repo_by_name: dict[str, Path] = {}
    for r in sorted(repos, key=lambda r: (_git(r, "rev-parse", "--is-shallow-repository") or "").strip() == "true"):
        repo_by_name.setdefault(_remote_name(r), r)

    # pass 1: git and trivial coverage; collect sizes still needing a disk match
    pending: dict[str, int] = {}
    for v in verdicts:
        for name, size, s256, g1, glf, is_arch in cache.members(v.sha256):
            if is_arch:
                continue  # judged through its own members
            if size == 0 or _match(name, TRIVIAL_GLOBS):
                continue
            if g1 not in gindex and (glf or "") not in gindex:
                pending[s256] = size

    exclude = {os.path.normcase(os.path.abspath(str(p))) for p in archives}
    by_size, cloud = disk_size_index(disk_roots, set(pending.values()), exclude)
    log(f"[disk] {sum(map(len, by_size.values()))} size candidates, {len(cloud)} cloud-only skipped")
    on_disk: dict[str, str] = {}
    want = set(pending)
    for n, (p, mt, size) in enumerate((p, mt, size) for size, paths in by_size.items() for p, mt in paths):
        s = cache.disk_sha(p, size, mt)
        if s in want:
            on_disk.setdefault(s, p)
        if n % 500 == 499:
            cache.db.commit()  # short write transactions: resumable and never blocks another reader long
    cache.db.commit()

    # pass 2: per-archive tallies
    holders: dict[str, set[int]] = defaultdict(set)
    for idx, v in enumerate(verdicts):
        rows = cache.members(v.sha256)
        v.members = sum(1 for r in rows if not r[5])
        rep: dict[tuple[str, str], list] = {}
        for name, size, s256, g1, glf, is_arch in rows:
            if is_arch:
                continue
            if size == 0 or _match(name, TRIVIAL_GLOBS):
                v.trivial += 1
                continue
            hit = gindex.get(g1) or (gindex.get(glf) if glf else None)
            if hit:
                v.covered_git += 1
                v.covered_git_local += not hit.pushed
                v.repos[hit.repo] = v.repos.get(hit.repo, 0) + 1
                group = rep.setdefault((hit.repo, hit.path.split("/")[0]), [g1 if g1 in gindex else glf, 0])
                group[1] += 1
                continue
            if s256 in on_disk:
                v.covered_disk += 1
                loc = _location(on_disk[s256])
                v.disk_locations[loc] = v.disk_locations.get(loc, 0) + 1
                if len(v.disk_examples) < 3:
                    v.disk_examples.append(on_disk[s256])
                continue
            if _match(name, GENERATED_GLOBS):
                v.generated_only.append(name)
            v.archive_only.append(name)
            holders[s256].add(idx)
        if provenance:
            # one representative blob for each of the three largest (repo, top-level dir) groups
            for (repo_name, _), (blob, count) in sorted(rep.items(), key=lambda kv: -kv[1][1])[:3]:
                found = introducing_commit(repo_by_name[repo_name], blob) if repo_name in repo_by_name else None
                if found:
                    v.provenance.append({"repo": repo_name, "path": gindex[blob].path, "members": count,
                                         "commit": found[0], "subject": found[1][:120], "pr": found[2]})

    # pass 3: keeper selection over archive-only blobs, plus same-path successors
    blobs_of: dict[int, set[str]] = defaultdict(set)
    sizes: dict[str, int] = {}
    tails: dict[str, set[int]] = defaultdict(set)
    mtime = [os.stat(v.path).st_mtime for v in verdicts]
    for idx, v in enumerate(verdicts):
        for name, size, s256, *_ in cache.members(v.sha256):
            tails[_tail(name)].add(idx)
            if s256 in holders:
                blobs_of[idx].add(s256)
                sizes[s256] = size
    for idx, v in enumerate(verdicts):
        for name in v.archive_only:
            t = _tail(name)
            newer = [k for k in tails.get(t, ()) if k != idx and mtime[k] > mtime[idx]] if t else []
            if t and t in gpaths:
                v.superseded_git += 1
                succ = f"{gpaths[t].repo}:{gpaths[t].path}"
            elif newer:
                v.superseded_archive += 1
                succ = Path(verdicts[max(newer, key=lambda k: mtime[k])].path).name
            else:
                continue
            if len(v.superseded_examples) < 5:
                v.superseded_examples.append(f"{name} -> {succ}")
    kept: set[int] = set()
    covered: set[str] = set()
    order = sorted(blobs_of, key=lambda i: (-sum(sizes[b] for b in blobs_of[i]), -os.stat(verdicts[i].path).st_mtime))
    for idx in order:
        if blobs_of[idx] - covered:
            kept.add(idx)
            covered |= blobs_of[idx]
    seen_sha: dict[str, str] = {}
    for idx, v in enumerate(verdicts):
        first = seen_sha.setdefault(v.sha256, v.path)
        if first != v.path:
            v.duplicate_of = first
        if v.error and not v.members:
            v.verdict = "ERROR"
        elif _match(Path(v.path).name, REDOWNLOADABLE_GLOBS):
            v.verdict = "REDOWNLOADABLE"
        elif not v.archive_only:
            v.verdict = "SAFE_LOCAL_GIT" if v.covered_git_local else "SAFE_LOSSLESS"
        elif idx not in kept:
            v.verdict = "SAFE_REDUNDANT"
            v.keepers = sorted({verdicts[k].path for b in blobs_of[idx] for k in holders[b] if k in kept})
        elif len(v.generated_only) == len(v.archive_only):
            v.verdict = "SAFE_IF_REGENERABLE"
        else:
            v.verdict = "KEEP"
        if v.verdict in ("KEEP", "SAFE_IF_REGENERABLE"):
            uniq = {s for s in blobs_of[idx]} - set().union(*(blobs_of[k] for k in kept if k != idx)) if kept else blobs_of[idx]
            v.orphan_bytes = sum(sizes[b] for b in uniq)
        if v.error and v.verdict.startswith("SAFE"):
            v.verdict = "KEEP"  # partially readable: cannot prove the unread tail is covered
        v.lane = lane_for(Path(v.path).name)
        v.disposition = _disposition(v)
    return verdicts


def _disposition(v: ArchiveVerdict) -> str:
    if v.verdict in ("SAFE_LOSSLESS", "REDOWNLOADABLE"):
        return "DELETE_OK"
    if v.verdict == "SAFE_LOCAL_GIT":
        return "PUSH_THEN_DELETE"  # some members exist only in unpushed local git objects
    if v.verdict == "SAFE_REDUNDANT":
        return "DELETE_OK_WHILE_KEEPER_KEPT"
    if v.lane == "PRIVATE":
        return "KEEP_PRIVATE"  # personal records never go into a repository
    if v.verdict == "ERROR":
        return "INSPECT"
    if v.archive_only and (v.superseded_git + v.superseded_archive) >= 0.9 * len(v.archive_only):
        return "REVIEW_SUPERSEDED"
    return "INCUBATE"


def aggregate_receipt(verdicts: list[ArchiveVerdict], report_sha256: str, engine_sha: str | None) -> dict:
    """Name-free summary for Golden Thread / Mycelium (no member or archive names)."""

    tally: dict[str, dict[str, int]] = defaultdict(lambda: {"archives": 0, "bytes": 0})
    for v in verdicts:
        tally[v.verdict]["archives"] += 1
        tally[v.verdict]["bytes"] += v.size
    return {
        "schema_version": "0.1",
        "receipt_id": "ARCHIVE_DEDUP_AUDIT_" + datetime.now(UTC).strftime("%Y%m%d"),
        "claim": "Archive members hash-matched against local git object stores and disk; verdict per archive",
        "engine": "src/archive_audit.py",
        "engine_commit": engine_sha,
        "archives": len(verdicts),
        "members": sum(v.members for v in verdicts),
        "covered_git": sum(v.covered_git for v in verdicts),
        "covered_disk": sum(v.covered_disk for v in verdicts),
        "verdicts": dict(sorted(tally.items())),
        "dispositions": dict(sorted(Counter(v.disposition for v in verdicts).items())),
        "covered_git_unpushed": sum(v.covered_git_local for v in verdicts),
        "local_report_sha256": report_sha256,
        "deletion_performed": False,
        "authority_transfer": False,
    }


# ---------------------------------------------------------------------------
# Strict prune: the archive stays the unit of grouping


@dataclass
class PruneAction:
    kind: str  # "archive" | "folder"
    path: str
    keeper: str
    keeper_sha256: str
    files: int
    bytes: int
    applied: bool = False
    # the grouping that disappears with the path: (relative name, size, sha256) per substantive file
    manifest: list[tuple[str, int, str]] = field(default_factory=list)


def _leaves(cache: Cache, sha: str) -> dict[str, int]:
    """sha256 -> size of every substantive leaf member (nested archives count through their contents)."""

    return {s: size for name, size, s, _g1, _glf, is_arch in cache.members(sha)
            if not is_arch and size and not _match(name, TRIVIAL_GLOBS)}


def _norm(name: str) -> str:
    for ext in (".gz", ".tgz", ".tar", ".zip", ".zip"):  # "x.zip.zip", "x.tar.gz"
        if name.lower().endswith(ext):
            name = name[: -len(ext)]
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _extracted_copy(folder: str, stems: set[str]) -> bool:
    """Folder name says it is an unpacked archive: same stem as an audited archive, or *extract*/*staging*."""

    f = _norm(folder)
    if "extract" in f or "staging" in f:
        return True
    return f in stems or (len(f) >= 6 and any(len(s) >= 6 and (s.startswith(f) or f.startswith(s)) for s in stems))


def plan_prune(archives: list[Path], cache: Cache, folder_roots: Iterable[Path]) -> list[PruneAction]:
    """Deletions that lose no byte *and* no grouping.

    * an archive goes only if every substantive member is inside ONE other kept archive; its
      member list is recorded so the group can be rebuilt from the keeper;
    * a top-level folder under ``folder_roots`` goes only if its name marks it as an unpacked
      archive and every substantive file is byte-identical to a member of ONE kept archive.
      Folders containing a ``.git`` directory, cloud-only or unreadable files are never touched,
      and nothing below the top level is pruned (no half-trees).
    * personal records (:data:`PRIVATE_RE`) are never pruned automatically.
    """

    scanned = {p: cache.scan_archive(p) for p in archives}
    leaves = {p: _leaves(cache, sha) for p, (sha, _) in scanned.items()}
    kept = set(archives)
    actions: list[PruneAction] = []
    by_size = sorted(archives, key=lambda p: (len(leaves[p]), p.stat().st_size, str(p)))
    for p in by_size:
        if scanned[p][1] or not leaves[p] or PRIVATE_RE.search(p.name):
            continue  # unreadable tail, nothing substantive, or personal: not pruned
        for k in sorted(kept - {p}, key=lambda k: (-len(leaves[k]), str(k))):
            if leaves[p].keys() <= leaves[k].keys():
                manifest = [(n, size, s) for n, size, s, _g1, _glf, is_arch in cache.members(scanned[p][0])
                            if not is_arch]
                actions.append(PruneAction("archive", str(p), str(k), scanned[k][0], len(leaves[p]),
                                           p.stat().st_size, manifest=manifest))
                kept.discard(p)
                break
    # a keeper that was itself pruned hands over to its own keeper (containment is transitive)
    moved = {a.path: a for a in actions}
    for a in actions:
        while a.keeper in moved:
            a.keeper, a.keeper_sha256 = moved[a.keeper].keeper, moved[a.keeper].keeper_sha256

    holders: dict[str, set[str]] = defaultdict(set)
    for k in kept:
        for s in leaves[k]:
            holders[s].add(str(k))
    sizes = {size for k in kept for size in leaves[k].values()}
    sha_of = {str(k): scanned[k][0] for k in kept}
    stems = {_norm(p.name) for p in archives}

    for root in folder_roots:
        try:
            dirs = [d for d in sorted(Path(root).iterdir()) if d.is_dir()]
        except OSError:
            continue
        for d in dirs:
            if PRIVATE_RE.search(d.name) or not _extracted_copy(d.name, stems):
                continue
            files = _folder_files(d)
            if not files or any(size not in sizes for _, size in files):
                continue
            covered: set[str] | None = None
            manifest = []
            for p, size in files:
                s = file_sha256(Path(p))
                manifest.append((os.path.relpath(p, d), size, s))
                covered = holders.get(s, set()) if covered is None else covered & holders.get(s, set())
                if not covered:
                    break
            if covered:
                keeper = max(covered, key=lambda k: (len(leaves[Path(k)]), k))
                actions.append(PruneAction("folder", str(d), keeper, sha_of[keeper], len(files),
                                           sum(size for _, size in files), manifest=manifest))
    return actions


def _folder_files(d: Path) -> list[tuple[str, int]] | None:
    """Substantive files of a folder, or None when any part is a repo, cloud-only or unreadable."""

    files: list[tuple[str, int]] = []
    errors: list[OSError] = []
    for dp, dns, fns in os.walk(d, onerror=errors.append):
        if errors or ".git" in dns or ".git" in fns:
            return None
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                st = os.stat(p)
            except OSError:
                return None
            if getattr(st, "st_file_attributes", 0) & CLOUD_ATTRS:
                return None
            if st.st_size and not _match(os.path.relpath(p, d), TRIVIAL_GLOBS):
                files.append((p, st.st_size))
    return None if errors else files


def apply_prune(actions: list[PruneAction], cache: Cache) -> None:
    """Delete planned paths after re-checking that each keeper is still the file that was verified."""

    for a in actions:
        sha, _ = cache.archive_sha(Path(a.keeper)) if Path(a.keeper).is_file() else (None, None)
        if sha != a.keeper_sha256:
            continue  # keeper moved or changed since planning: leave the candidate alone
        if a.kind == "archive":
            Path(a.path).unlink()
        else:
            shutil.rmtree(a.path, onerror=lambda f, p, _: (os.chmod(p, stat.S_IWRITE), f(p)))
        a.applied = True


# ---------------------------------------------------------------------------
# CLI


def _write_report(verdicts: list[ArchiveVerdict], out: Path) -> str:
    out.mkdir(parents=True, exist_ok=True)
    data = [v.__dict__ for v in verdicts]
    blob = json.dumps(data, indent=1, ensure_ascii=False).encode("utf-8")
    (out / "archive_audit_report.json").write_bytes(blob)
    lines = ["| disposition | verdict | MB | members | git | disk | archive-only | superseded | lane | archive |",
             "|---|---|---:|---:|---:|---:|---:|---:|---|---|"]
    for v in sorted(verdicts, key=lambda v: (v.disposition, v.verdict, v.path)):
        lines.append(f"| {v.disposition} | {v.verdict} | {v.size / 1e6:.1f} | {v.members} | {v.covered_git} | "
                     f"{v.covered_disk} | {len(v.archive_only)} | {v.superseded_git + v.superseded_archive} | "
                     f"{v.lane} | {Path(v.path).name} |")
    (out / "archive_audit_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return hashlib.sha256(blob).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("archives", nargs="*", type=Path, help="archive files (or use --list)")
    ap.add_argument("--list", type=Path, help="text file with one archive path per line (quotes allowed)")
    ap.add_argument("--repo-root", action="append", type=Path, default=[], help="where to discover git repos")
    ap.add_argument("--disk-root", action="append", type=Path, default=[], help="where to look for loose copies")
    ap.add_argument("--out", type=Path, required=True, help="local output dir (report + cache)")
    ap.add_argument("--receipt", type=Path, help="write the name-free aggregate receipt here")
    ap.add_argument("--no-provenance", action="store_true")
    ap.add_argument("--prune-root", action="append", type=Path, default=[],
                    help="also look for extracted folders fully contained in one archive under this dir")
    ap.add_argument("--prune", action="store_true", help="plan strict lossless deletions (prune_plan.json)")
    ap.add_argument("--apply", action="store_true", help="with --prune: delete what the plan proves redundant")
    ap.add_argument("--skip-audit", action="store_true", help="with --prune: skip git/disk matching")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

    paths = list(a.archives)
    if a.list:
        paths += [Path(line.strip().strip('"')) for line in a.list.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    missing = [p for p in paths if not p.is_file()]
    for p in missing:
        print("[missing]", p)
    paths = [p for p in dict.fromkeys(paths) if p.is_file()]
    cache = Cache(a.out / "archive_audit_cache.sqlite")
    if a.prune:
        actions = plan_prune(paths, cache, a.prune_root)
        if a.apply:
            apply_prune(actions, cache)
        log = {"generated_at": datetime.now(UTC).isoformat(), "apply": a.apply, "actions": [x.__dict__ for x in actions]}
        (a.out / "prune_log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
        done = [x for x in actions if x.applied or not a.apply]
        print(f"[prune] {len(done)}/{len(actions)} {'deleted' if a.apply else 'planned'}, "
              f"{sum(x.bytes for x in done if x.kind == 'folder') / 1e6:.0f} MB in folders, "
              f"{sum(x.bytes for x in done if x.kind == 'archive') / 1e6:.0f} MB in archives")
        paths = [p for p in paths if p.is_file()]
        if a.skip_audit:
            return 0
    repos = discover_repos(a.repo_root)
    print("[repos]", ", ".join(_remote_name(r) for r in repos))
    verdicts = audit(paths, cache, repos, a.disk_root, provenance=not a.no_provenance)
    digest = _write_report(verdicts, a.out)
    if a.receipt:
        engine = (_git(Path(__file__).parent, "rev-parse", "HEAD") or "").strip() or None
        a.receipt.parent.mkdir(parents=True, exist_ok=True)
        a.receipt.write_text(json.dumps(aggregate_receipt(verdicts, digest, engine), indent=2) + "\n", encoding="utf-8")
    counts = defaultdict(int)
    for v in verdicts:
        counts[v.verdict] += 1
    print("[done]", dict(counts), "report sha256", digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
