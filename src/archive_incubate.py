"""Archive incubation: land the unique text of INCUBATE archives in a private git repo, byte-exact.

Second stage after :mod:`src.archive_audit`.  The audit report marks archives
whose members exist nowhere else as ``INCUBATE``; this module takes those
members straight out of the zips (nothing is extracted to disk), smoke-checks
them without running any archive code, and writes one landing per target:

* ``<landing>_manifest.json`` records, for every member of every archive, its
  SHA-256 and one status: ``committed`` (with its repo path), ``covered``
  (lives elsewhere), ``kept_in_zip:*`` (binary, large, ``.git/`` internals,
  LEAVE archive) or ``excluded:*`` (junk, credential-like name, private name,
  secret pattern, unsafe path).  Each archive gets a verdict:

  ``MERGE``   code that passes smoke: promote by PR into the target repo.
  ``BRIDGE``  docs/data only or a smoke failure: link or adapt, do not merge as-is.
  ``LEAVE``   nothing committable: the zip stays the only home.

* ``<landing>_payload.json`` holds the committed bytes (hex), so the commit
  can be built later with ``git -c core.ignorecase=false fast-import``.

Subcommands: ``plan`` (manifests + payloads), ``stream`` (fast-import stream),
``verify`` (every committed member is in a git tree, byte-identical, and
nothing else is), ``scan`` (broad credential scan of a payload; prints paths
and rule names only, never values) and ``markdown`` (``INCUBATOR_MANIFEST.md``).
Run from the repo root as ``python -m src.archive_incubate <subcommand>``.

Archive names stay out of this public repo: the per-archive routing (LEAVE
list and TRIAGE targets) is a local JSON file passed with ``--routing``::

    {"leave": ["ci-build.zip"], "triage": {"files_toGPT.zip": "cryoplant-project"}}

First used on 2026-10-23 for GBOGEB/archive-incubator#1 and
GBOGEB/cryoplant-project#2056 (W367).
"""

from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import io
import json
import re
import sqlite3
import subprocess
import sys
import tarfile
import time
import tomllib
import zipfile
from collections import Counter, defaultdict
from collections.abc import Iterator
from pathlib import Path, PurePosixPath
from typing import BinaryIO

import yaml

from src import archive_audit as aa

MAX_TEXT = 512 * 1024  # larger text is almost always a render (Plotly HTML, layered SVG): it stays in the zip
BIN_EXT = {".pptx", ".ppt", ".docx", ".doc", ".xlsx", ".xlsm", ".xls", ".pdf", ".png", ".jpg", ".jpeg", ".gif",
           ".bmp", ".tif", ".tiff", ".webp", ".ico", ".zip", ".gz", ".tgz", ".tar", ".7z", ".exe", ".dll", ".bin",
           ".dwg", ".dxf", ".step", ".stp", ".vsdx", ".vsd", ".msg", ".eml", ".mp4", ".mov", ".wav", ".mp3", ".pkl",
           ".npy", ".npz", ".h5", ".parquet", ".sqlite", ".db", ".whl", ".pyc", ".woff", ".woff2", ".ttf", ".otf",
           ".emf", ".wmf", ".odt", ".ods", ".odp", ".one", ".mpp", ".pst", ".msi", ".vsix", ".jar", ".class"}
CODE_EXT = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".ps1", ".psm1", ".sh", ".bat", ".cmd", ".c",
            ".h", ".cpp", ".hpp", ".sql", ".r", ".m", ".vba", ".bas", ".go", ".rs", ".java"}
JUNK_GLOBS = ("*.stackdump", "*debug.log", "*Thumbs.db", "*.DS_Store", "~$*", "*/~$*", "*.pyc", "*/__pycache__/*",
              "__MACOSX/*", "*/__MACOSX/*", "*/.pytest_cache/*", "*/.ipynb_checkpoints/*")
CRED_NAME = re.compile(r"token|secret|passw|credential|apikey|api_key|(^|/)\.env($|\.)|id_rsa|id_ed25519|\.pem$|"
                       r"\.key$|\.pfx$|\.p12$|\.kdbx$|\.netrc$|\.npmrc$|\.pypirc$|\.abacus\.donotdelete$", re.IGNORECASE)
SECRET = re.compile(rb"ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|gh[ousr]_[A-Za-z0-9]{30,}|"
                    rb"sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|"
                    rb"-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[abprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}")
WIN_BAD = re.compile(r'[<>:"|?*\x00-\x1f]')
RESERVED = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
SMOKE_KIND = {".py": "py_compile", ".json": "json", ".ipynb": "json", ".yaml": "yaml", ".yml": "yaml",
              ".toml": "toml"}

# Broader scan of a payload before it is committed (rule names only are reported).
SCAN_RULES = {
    "assigned_secret": re.compile(rb"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|"
                                  rb"client[_-]?secret|bearer)\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-+/=.]{16,})"),
    "url_credentials": re.compile(rb"https?://[^/\s:@]+:[^/\s:@]{6,}@"),
    "github_token": re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}"),
    "sk_key": re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    "private_key": re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}
PLACEHOLDER = re.compile(rb"(?i)x{6,}|your[_-]|example|placeholder|changeme|dummy|<[^>]+>|\*{4,}|\$\{|os\.environ|getenv")

# audit lane -> landing folder
LANE_TARGET = {"GBOGEB/cryoplant-project": "cryoplant-project", "GBOGEB/CODEX": "codex", "GBOGEB/ABACUS": "abacus",
               "gg_MATH": "gg_math", "GBOGEB/dmaic-recursive-pipeline": "dmaic-recursive-pipeline"}
VERDICTS = {"MERGE": "code that passes smoke: promote by PR into the target repo",
            "BRIDGE": "docs/data only or a smoke failure: link or adapt, do not merge as-is",
            "LEAVE": "nothing committable: the zip in OneDrive stays the only home"}


# ---------------------------------------------------------------------------
# Paths


def clean_part(p: str) -> str:
    p = WIN_BAD.sub("_", p).rstrip(" .")
    if p.split(".")[0].lower() in RESERVED:
        p += "_"
    return p


def stem(archive: str) -> str:
    s = archive
    for ext in (".tar.gz", ".tgz", ".zip", ".tar", ".gz"):
        if s.lower().endswith(ext):
            s = s[: -len(ext)]
            break
    return clean_part(s) or "archive"


def repo_path(member: str) -> str | None:
    """Archive member name -> safe relative path ('!/' nesting becomes '<inner>.d/'); None if unsafe."""

    parts, out = member.replace("\\", "/").split("!/"), []
    for i, seg in enumerate(parts):
        if seg == "<gunzip>":
            prev = out[-1][:-2] if out and out[-1].endswith(".d") else "file"
            seg = prev[:-3] if prev.lower().endswith(".gz") else prev + ".unz"
            out[-1:] = []
        comps = [c for c in seg.split("/") if c not in ("", ".")]
        if any(c == ".." for c in comps) or not comps:
            return None
        comps = [clean_part(c) or "_" for c in comps]
        if i < len(parts) - 1:
            comps[-1] += ".d"
        out.extend(comps)
    return "/".join(out)


def _has_git_dir(name: str) -> bool:
    return any(c.lower() == ".git" for c in name.replace("\\", "/").replace("!/", "/").split("/"))


# ---------------------------------------------------------------------------
# Reading members


def walk(fileobj: BinaryIO, wanted: set[str], prefix: str = "") -> Iterator[tuple[str, bytes | None, int]]:
    """Yield (name, bytes|None, size) for every leaf member; bytes only for wanted names up to MAX_TEXT."""

    head = fileobj.read(512)
    fileobj.seek(0)
    kind = aa.sniff_kind(head)
    nest = {w.split("!/")[0] for w in wanted if "!/" in w}

    def leaf(name, read, size):
        local = name[len(prefix):]
        if local in nest and size <= aa.NESTED_LIMIT:
            data = read()
            sub = {w[len(local) + 2:] for w in wanted if w.startswith(local + "!/")}
            try:
                yield from walk(io.BytesIO(data), sub, name + "!/")
                return
            except aa.READ_ERRORS:
                pass
            yield name, (data if local in wanted else None), size
            return
        yield name, (read() if local in wanted and size <= MAX_TEXT else None), size

    if kind == "zip":
        with zipfile.ZipFile(fileobj) as zf:
            for info in zf.infolist():
                if not info.is_dir():
                    yield from leaf(prefix + info.filename, lambda i=info: zf.read(i), info.file_size)
    elif kind in ("gz", "tar") and aa._is_tar(fileobj):
        with tarfile.open(fileobj=fileobj, mode="r:*") as tf:
            for info in tf:
                if info.isfile():
                    yield from leaf(prefix + info.name, lambda i=info: tf.extractfile(i).read(), info.size)
    elif kind == "gz":
        data = gzip.GzipFile(fileobj=fileobj).read()
        yield from leaf(prefix + "<gunzip>", lambda: data, len(data))
    else:
        raise ValueError("not a zip/tar/gz archive")


def decode(b: bytes) -> str:
    try:
        return b.decode("utf-8-sig")
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace")


def smoke(path: str, b: bytes) -> tuple[str, str | None, int]:
    """(check, result, tests found): parse only, never execute."""

    ext = PurePosixPath(path).suffix.lower()
    try:
        if ext == ".py":
            tree = ast.parse(decode(b), filename=path)
            compile(tree, path, "exec")
            tests = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and n.name.startswith("test"))
            return "py_compile", "ok", tests
        if ext in (".json", ".ipynb"):
            json.loads(decode(b))
            return "json", "ok", 0
        if ext in (".yaml", ".yml"):
            list(yaml.safe_load_all(decode(b)))
            return "yaml", "ok", 0
        if ext == ".toml":
            tomllib.loads(decode(b))
            return "toml", "ok", 0
    except Exception as exc:  # noqa: BLE001 - record the failure class only
        return SMOKE_KIND[ext], f"fail: {type(exc).__name__}", 0
    return "none", None, 0


def member_status(name: str, size: int, sha256: str, data: bytes | None) -> str:
    """Status of one archive-only member of an archive that has a landing folder ('committed' if it may land)."""

    ext = PurePosixPath(name.replace("\\", "/")).suffix.lower()
    if _has_git_dir(name):
        return "kept_in_zip:git_internals"  # a bundled repo's .git/ cannot live in a git tree (hasDotgit)
    if aa._match(name, JUNK_GLOBS):
        return "excluded:junk"
    if CRED_NAME.search(name):
        return "excluded:credential_name"
    if aa.PRIVATE_RE.search(re.sub(r"(?i)taxonom", "", name)):  # "tax" is personal, "taxonomy" is not
        return "excluded:private_name"
    if ext in BIN_EXT:
        return "kept_in_zip:binary"
    if size > MAX_TEXT:
        return "kept_in_zip:large"
    if data is None:
        return "kept_in_zip:unreadable"
    if hashlib.sha256(data).hexdigest() != sha256:
        return "kept_in_zip:hash_mismatch"
    if b"\0" in data[:8192]:
        return "kept_in_zip:binary"
    if SECRET.search(data):
        return "excluded:secret_pattern"
    if repo_path(name) is None:
        return "excluded:unsafe_path"
    return "committed"


# ---------------------------------------------------------------------------
# Plan


def route(archive: str, lane: str, routing: dict) -> tuple[str, str]:
    """(target, landing) for one INCUBATE archive."""

    if archive in set(routing.get("leave", ())):
        target = "LEAVE"
    elif lane == "TRIAGE":
        target = routing.get("triage", {}).get(archive, "_unrouted")
    else:
        target = LANE_TARGET[lane]
    landing = "cryoplant" if target == "cryoplant-project" or (target == "LEAVE" and lane != "TRIAGE") else "incubator"
    return target, landing


def _source(path: str, source_root: str | None) -> str:
    if source_root and path.lower().startswith(source_root.lower()):
        return path[len(source_root):].lstrip("\\/").replace("\\", "/")
    return Path(path).name


def plan(report: list[dict], cache: sqlite3.Connection, routing: dict, source_root: str | None = None,
         engine: str = "src/archive_audit.py", report_sha256: str = "", log=print,
         ) -> tuple[dict[str, dict], dict[str, dict[str, bytes]]]:
    """Build one manifest and one payload per landing from an audit report and its member cache."""

    landings: dict[str, list] = defaultdict(list)
    payload: dict[str, dict[str, bytes]] = defaultdict(dict)
    folders: dict[tuple[str, str], set] = defaultdict(set)
    for v in sorted((v for v in report if v["disposition"] == "INCUBATE"), key=lambda v: v["path"]):
        name = Path(v["path"]).name
        target, landing = route(name, v["lane"], routing)
        base = stem(name)
        group = target if landing == "incubator" else ""
        if base.lower() in folders[(landing, group)]:
            base = f"{base}__{v['sha256'][:8]}"
        folders[(landing, group)].add(base.lower())
        folder = (f"{group}/{base}" if group else base) if target != "LEAVE" else None
        unique = set(v["archive_only"])
        members = cache.execute("select name, size, sha256, is_archive from members where archive_sha256=?",
                                (v["sha256"],)).fetchall()
        wanted = {n for n, _size, _s, is_arch in members if n in unique and not is_arch} if folder else set()
        got: dict[str, bytes] = {}
        if wanted:
            with open(v["path"], "rb") as f:
                got = {n: b for n, b, _size in walk(f, wanted) if b is not None and n in wanted}
        rows, counts, smk, seen = [], Counter(), Counter(), set()
        has_code, tests = False, 0
        for n, size, s, is_arch in sorted(members):
            if is_arch:
                continue
            row = {"name": n, "size": size, "sha256": s, "path": None, "generated": aa._match(n, aa.GENERATED_GLOBS)}
            if n not in unique:
                row["status"] = "covered" if size else "empty"
            elif not folder:
                row["status"] = "kept_in_zip:leave"
            else:
                row["status"] = member_status(n, size, s, got.get(n))
            if row["status"] == "committed":
                full = f"{folder}/{repo_path(n)}"
                k, i = full.lower(), 1
                while k in seen:  # case-insensitive clash: keep both, suffix the later one
                    i += 1
                    stemp, dot, ext2 = full.rpartition(".")
                    full = f"{stemp}~{i}.{ext2}" if dot and "/" not in ext2 else f"{full}~{i}"
                    k = full.lower()
                seen.add(k)
                row["path"] = full
                payload[landing][full] = got[n]
                chk, res, t = smoke(full, got[n])
                if res:
                    row["smoke"] = f"{chk}: {res}"
                    smk[f"{chk}_{'ok' if res == 'ok' else 'fail'}"] += 1
                tests += t
                has_code |= PurePosixPath(full).suffix.lower() in CODE_EXT
            counts[row["status"]] += 1
            rows.append(row)
        committed = counts["committed"]
        fails = sum(c for k, c in smk.items() if k.endswith("_fail"))
        verdict = "LEAVE" if not committed else "BRIDGE" if fails or not has_code else "MERGE"
        landings[landing].append({
            "archive": name, "source": _source(v["path"], source_root), "sha256": v["sha256"], "size": v["size"],
            "engine_lane": v["lane"], "target": target, "folder": folder, "verdict": verdict, "counts": dict(counts),
            "smoke": dict(smk), "tests_found_statically": tests, "members": rows})
        log(f"{landing:9} {verdict:6} {target:24} committed={committed:4} {name[:60]}")
    manifests = {
        landing: {
            "schema": "archive-incubator-manifest/0.1",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "engine": engine, "audit_report_sha256": report_sha256,
            "rules": {"committed": "unique text members only (found in no local git repo and nowhere on disk)",
                      "max_text_bytes": MAX_TEXT, "binaries": "kept in the zip in OneDrive, listed by sha256",
                      "excluded": "junk, credential-like names, PRIVATE names, secret patterns, unsafe paths",
                      "smoke": "parse/compile only (ast, json, yaml.safe_load, tomllib); no archive code executed",
                      "verdicts": VERDICTS},
            "archives": arch,
        }
        for landing, arch in landings.items()
    }
    return manifests, dict(payload)


# ---------------------------------------------------------------------------
# Commit, verify, scan, summarise


def _quote(p: str) -> str:
    return '"' + p.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def fast_import_stream(files: dict[str, bytes], branch: str, message: bytes, author: str,
                       base: str | None = None, when: int | None = None) -> bytes:
    """One-commit `git fast-import` stream; run it with `git -c core.ignorecase=false fast-import`."""

    when = int(time.time()) if when is None else when
    out = io.BytesIO()
    marks = {}
    for i, (p, b) in enumerate(sorted(files.items()), 1):
        out.write(b"blob\nmark :%d\ndata %d\n" % (i, len(b)) + b + b"\n")
        marks[p] = i
    out.write(f"commit refs/heads/{branch}\nauthor {author} {when} +0000\ncommitter {author} {when} +0000\n".encode())
    out.write(b"data %d\n" % len(message) + message + b"\n")
    if base:
        out.write(f"from {base}\n".encode())
    for p, m in marks.items():
        out.write(f"M 100644 :{m} {_quote(p)}\n".encode())
    out.write(b"\n")
    return out.getvalue()


def verify_tree(git_dir: Path, rev: str, manifest: dict, prefix: str = "", extra: set[str] = frozenset()) -> dict:
    """Every committed manifest member is in the tree at `prefix`, byte-identical, and nothing else is."""

    want = {prefix + r["path"]: r["sha256"] for a in manifest["archives"] for r in a["members"]
            if r["status"] == "committed"}
    ls = subprocess.run(["git", "-C", str(git_dir), "ls-tree", "-r", "-z", "--name-only", rev, "--", prefix or "."],
                        capture_output=True, check=True).stdout.decode("utf-8").split("\0")
    tree = {p for p in ls if p}
    missing = sorted(set(want) - tree)
    unexpected = sorted(tree - set(want) - set(extra))
    bad = []
    with subprocess.Popen(["git", "-C", str(git_dir), "cat-file", "--batch"], stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE) as proc:
        for p, sha in want.items():
            if p in missing:
                continue
            proc.stdin.write(f"{rev}:{p}\n".encode())
            proc.stdin.flush()
            header = proc.stdout.readline().split()
            data = proc.stdout.read(int(header[2]))
            proc.stdout.read(1)
            if hashlib.sha256(data).hexdigest() != sha:
                bad.append(p)
        proc.stdin.close()
    return {"committed_in_manifest": len(want), "in_tree": len(tree), "missing": len(missing),
            "unexpected": unexpected[:10], "hash_mismatch": len(bad), "examples": (missing + bad)[:5],
            "ok": not (missing or bad or unexpected)}


def scan_credentials(payload: dict[str, bytes]) -> dict[str, list[str]]:
    """path -> rule names that matched outside an obvious placeholder (values are never returned)."""

    hits: dict[str, list[str]] = {}
    for path, b in sorted(payload.items()):
        found = {name for name, rx in SCAN_RULES.items() for mt in rx.finditer(b)
                 if not PLACEHOLDER.search(b[max(0, mt.start() - 40): mt.end() + 40])}
        if found:
            hits[path] = sorted(found)
    return hits


def manifest_markdown(manifest: dict, title: str) -> str:
    arch = manifest["archives"]
    tot, smk = Counter(), Counter()
    for a in arch:
        tot.update(a["counts"])
        smk.update(a["smoke"])
    verd = Counter(a["verdict"] for a in arch)
    smoke_line = ", ".join(f"{k} {v}" for k, v in sorted(smk.items()))
    lines = [
        f"# {title}",
        "",
        (f"Generated {manifest['generated_at']} from the archive audit (`{manifest['engine']}`, report sha256 "
         f"`{manifest['audit_report_sha256'][:12]}`). Full per-member record: `INCUBATOR_MANIFEST.json`."),
        "",
        f"- Archives: {len(arch)} (MERGE {verd['MERGE']}, BRIDGE {verd['BRIDGE']}, LEAVE {verd['LEAVE']})",
        (f"- Committed files: {tot['committed']}; kept in the zip: {tot['kept_in_zip:binary']} binary, "
         f"{tot['kept_in_zip:large']} over 512 KiB, {tot['kept_in_zip:leave']} in LEAVE archives; "
         f"covered elsewhere: {tot['covered']}"),
        (f"- Excluded: {tot['excluded:secret_pattern']} secret pattern, {tot['excluded:credential_name']} "
         f"credential name, {tot['excluded:private_name']} private name, {tot['excluded:junk']} junk, "
         f"{tot['excluded:unsafe_path']} unsafe path"),
        f"- Smoke (parse/compile only, nothing executed): {smoke_line}",
        "",
        ("Verdicts: **MERGE** = code that passes smoke, promote by PR into the target repo. **BRIDGE** = docs/data "
         "only or a smoke failure: link or adapt, do not merge as-is. **LEAVE** = nothing committable; the zip in "
         "OneDrive stays its only home."),
        "",
        "| Archive | Target | Folder | Verdict | Committed | Binary kept | Large kept | Excluded | Smoke fails | Tests found |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for a in sorted(arch, key=lambda a: (a["target"], a["archive"].lower())):
        c, s = a["counts"], a["smoke"]
        exc = sum(v for k, v in c.items() if k.startswith("excluded"))
        fails = sum(v for k, v in s.items() if k.endswith("_fail"))
        lines.append(f"| `{a['archive']}` | {a['target']} | {('`' + a['folder'] + '/`') if a['folder'] else ''} | "
                     f"{a['verdict']} | {c.get('committed', 0)} | {c.get('kept_in_zip:binary', 0)} | "
                     f"{c.get('kept_in_zip:large', 0)} | {exc} | {fails} | {a['tests_found_statically']} |")
    return "\n".join(lines) + "\n"


def _load_payload(path: Path) -> dict[str, bytes]:
    return {p: bytes.fromhex(h) for p, h in json.loads(path.read_text(encoding="utf-8")).items()}


# ---------------------------------------------------------------------------
# CLI


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="manifests and payloads per landing")
    p.add_argument("--report", type=Path, required=True, help="archive_audit_report.json")
    p.add_argument("--cache", type=Path, required=True, help="archive_audit_cache.sqlite (opened read-only)")
    p.add_argument("--out", type=Path, required=True, help="local output dir")
    p.add_argument("--routing", type=Path, help="local JSON: {'leave': [...], 'triage': {archive: target}}")
    p.add_argument("--source-root", help="strip this prefix from archive paths in the manifest")
    s = sub.add_parser("stream", help="one-commit fast-import stream")
    s.add_argument("--payload", type=Path, help="<landing>_payload.json")
    s.add_argument("--prefix", default="", help="repo folder the payload lands under")
    s.add_argument("--extra", action="append", default=[], help="repo_path=local_file, added as is")
    s.add_argument("--branch", required=True)
    s.add_argument("--from", dest="base", help="parent commit")
    s.add_argument("--author", required=True, help="'Name <email>'")
    s.add_argument("--message", type=Path, required=True, help="commit message file")
    s.add_argument("--out", type=Path, required=True)
    v = sub.add_parser("verify", help="check a git tree against a manifest")
    v.add_argument("--git-dir", type=Path, required=True)
    v.add_argument("--rev", required=True)
    v.add_argument("--manifest", type=Path, required=True)
    v.add_argument("--prefix", default="")
    v.add_argument("--extra", action="append", default=[], help="repo paths allowed besides the payload")
    c = sub.add_parser("scan", help="broad credential scan of a payload (paths and rule names only)")
    c.add_argument("payload", type=Path)
    m = sub.add_parser("markdown", help="INCUBATOR_MANIFEST.md from a manifest")
    m.add_argument("manifest", type=Path)
    m.add_argument("out", type=Path)
    m.add_argument("--title", default="Archive incubator manifest")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

    if a.cmd == "plan":
        a.out.mkdir(parents=True, exist_ok=True)
        report_bytes = a.report.read_bytes()
        routing = json.loads(a.routing.read_text(encoding="utf-8")) if a.routing else {}
        engine_sha = (aa._git(Path(__file__).parent, "rev-parse", "--short=8", "HEAD") or "").strip()
        db = sqlite3.connect(f"file:{a.cache.resolve().as_posix()}?mode=ro", uri=True)
        manifests, payload = plan(json.loads(report_bytes), db, routing, a.source_root,
                                  engine=f"GBOGEB/CODEX src/archive_audit.py @ {engine_sha or 'unknown'}",
                                  report_sha256=hashlib.sha256(report_bytes).hexdigest())
        for landing, man in manifests.items():
            (a.out / f"{landing}_manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n",
                                                           encoding="utf-8", newline="\n")
            files = payload.get(landing, {})
            with open(a.out / f"{landing}_payload.json", "w", encoding="utf-8", newline="\n") as f:
                json.dump({k: b.hex() for k, b in files.items()}, f)
            tot = Counter()
            for x in man["archives"]:
                tot.update(x["counts"])
            print(f"[{landing}] archives={len(man['archives'])} "
                  f"verdicts={dict(Counter(x['verdict'] for x in man['archives']))} files={len(files)} "
                  f"bytes={sum(map(len, files.values()))} status={dict(tot)}")
        return 0
    if a.cmd == "stream":
        files = {a.prefix + k: b for k, b in _load_payload(a.payload).items()} if a.payload else {}
        for e in a.extra:
            k, _, path = e.partition("=")
            files[k] = Path(path).read_bytes()
        a.out.write_bytes(fast_import_stream(files, a.branch, a.message.read_bytes(), a.author, a.base))
        print(f"[stream] {len(files)} files, {sum(map(len, files.values()))} bytes -> {a.out}")
        return 0
    if a.cmd == "verify":
        res = verify_tree(a.git_dir, a.rev, json.loads(a.manifest.read_text(encoding="utf-8")), a.prefix, set(a.extra))
        print(json.dumps(res, ensure_ascii=False))
        return 0 if res["ok"] else 1
    if a.cmd == "scan":
        payload = _load_payload(a.payload)
        hits = scan_credentials(payload)
        for path, rules in hits.items():
            print(f"{path} :: {rules}")
        print(f"[scan] {len(payload)} files, {len(hits)} with possible credentials")
        return 1 if hits else 0
    man = json.loads(a.manifest.read_text(encoding="utf-8"))
    a.out.write_text(manifest_markdown(man, a.title), encoding="utf-8", newline="\n")
    print(json.dumps({"archives": len(man["archives"]),
                      "verdicts": Counter(x["verdict"] for x in man["archives"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
