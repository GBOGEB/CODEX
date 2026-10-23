"""Weekly disk hygiene: free space, duplicate files by hash, stale git mirrors.

    python disk_hygiene.py                 # report only (dry run)
    python disk_hygiene.py --apply         # also send duplicate copies to the Recycle Bin
    python disk_hygiene.py --roots D1 D2   # override the scanned folders

Duplicates are files with identical content (SHA-256). In each group one copy
is kept: the one with the most "normal" name (no "(1)", "copy", "(recovered)",
"AutoRecovered", "backup", OneDrive "-PCNAME" conflict suffix...), then the most
recently modified, then the shortest path. The others go to the Recycle Bin, not
permanent deletion, and every move is written to a CSV manifest so it can be
restored. Emptying the Recycle Bin stays a manual step.

Never touched: anything under .git, node_modules or virtualenvs; OneDrive
cloud-only files (hashing them would download them); files changed in the last
7 days; files smaller than --min-mb.
"""
from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

HOME = Path(os.environ.get("USERPROFILE", str(Path.home())))
# Reports go outside the repo so a run never dirties the checkout.
REPORTS = Path(os.environ.get("LOCALAPPDATA", str(HOME / ".local" / "share"))) / "disk-hygiene" / "reports"
DEFAULT_ROOTS = [HOME / "Documents", HOME / "Downloads", HOME / "Desktop", HOME / "source", HOME / "PycharmProjects",
                 HOME / "Clone_FrOM_GITHUB"] + sorted(p for p in HOME.glob("OneDrive*") if p.is_dir())
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "env", "__pycache__", ".pytest_cache", ".mypy_cache",
             ".ruff_cache", "site-packages", "$RECYCLE.BIN"}
# Windows attributes for OneDrive placeholders whose content is not on disk.
FILE_ATTRIBUTE_OFFLINE = 0x1000
FILE_ATTRIBUTE_RECALL_ON_OPEN = 0x40000
FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x400000
CLOUD_ONLY = FILE_ATTRIBUTE_OFFLINE | FILE_ATTRIBUTE_RECALL_ON_OPEN | FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS

_L, _R = r"(?<![a-z])", r"(?![a-z])"  # letter boundaries: "_backup" and "copy2" still match
NAME_PENALTIES = [  # (regex on the lower-cased file stem, penalty) - lower total penalty = better name
    (r"\(\d+\)$", 3), (r"[ _-]\d+$", 1), (_L + r"(copy|kopie|copie)" + _R, 4), (_L + r"recovered" + _R, 4),
    (r"autorecovered|autosaved", 4), (_L + r"(backup|bak|old)" + _R, 3), (_L + r"conflict" + _R, 4),
    (_L + r"(tmp|temp)" + _R + r"|^~\$", 5),
]
# OneDrive/Office conflict copies append the machine name in capitals: "Deck-GBONTHUY-LT".
CONFLICT_SUFFIX = re.compile(r"-[A-Z][A-Z0-9]{2,}(-[A-Z0-9]{1,8})*$")


def free_gb(path: Path) -> float:
    return round(shutil.disk_usage(path).free / 1e9, 2)


def is_cloud_only(st: os.stat_result) -> bool:
    return bool(getattr(st, "st_file_attributes", 0) & CLOUD_ONLY)


def name_penalty(path: Path) -> int:
    stem = path.stem.lower()
    conflict = 2 if CONFLICT_SUFFIX.search(path.stem) else 0  # case-sensitive on the original stem
    return conflict + sum(p for rx, p in NAME_PENALTIES if re.search(rx, stem))


def keeper_key(path: Path, mtime: float) -> tuple:
    return (name_penalty(path), -mtime, len(str(path)), str(path).lower())


def walk(roots: list[Path], min_bytes: int, min_age_s: float):
    now = time.time()
    seen_inodes = set()
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith("$")]
            for name in filenames:
                p = Path(dirpath) / name
                try:
                    st = p.stat()
                except OSError:
                    continue
                if st.st_size < min_bytes or is_cloud_only(st) or now - st.st_mtime < min_age_s:
                    continue
                key = (st.st_dev, st.st_ino)
                if st.st_ino and key in seen_inodes:  # hard links are not duplicates
                    continue
                seen_inodes.add(key)
                yield p, st


def sha256(path: Path, limit: int | None = None) -> str | None:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            remaining = limit
            while True:
                chunk = fh.read(1 << 20 if remaining is None else min(1 << 20, remaining))
                if not chunk:
                    break
                h.update(chunk)
                if remaining is not None:
                    remaining -= len(chunk)
                    if remaining <= 0:
                        break
    except OSError:
        return None
    return h.hexdigest()


def find_duplicates(roots: list[Path], min_bytes: int, min_age_s: float) -> list[dict]:
    by_size = defaultdict(list)
    for p, st in walk(roots, min_bytes, min_age_s):
        by_size[st.st_size].append((p, st.st_mtime))
    groups = []
    for size, items in by_size.items():
        if len(items) < 2:
            continue
        by_head = defaultdict(list)
        for p, m in items:
            head = sha256(p, 65536)
            if head:
                by_head[head].append((p, m))
        for cands in by_head.values():
            if len(cands) < 2:
                continue
            by_full = defaultdict(list)
            for p, m in cands:
                full = sha256(p)
                if full:
                    by_full[full].append((p, m))
            for digest, same in by_full.items():
                if len(same) < 2:
                    continue
                same.sort(key=lambda pm: keeper_key(pm[0], pm[1]))
                groups.append({"sha256": digest, "size": size, "keep": str(same[0][0]),
                               "remove": [str(p) for p, _ in same[1:]]})
    groups.sort(key=lambda g: -g["size"] * len(g["remove"]))
    return groups


def recycle(path: str) -> bool:
    """Send one file to the Recycle Bin (Windows Shell); False if it failed."""
    try:
        from ctypes import wintypes

        class SHFILEOPSTRUCTW(ctypes.Structure):
            _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT), ("pFrom", wintypes.LPCWSTR),
                        ("pTo", wintypes.LPCWSTR), ("fFlags", ctypes.c_uint16), ("fAnyOperationsAborted", wintypes.BOOL),
                        ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", wintypes.LPCWSTR)]
        FO_DELETE, FOF_ALLOWUNDO, FOF_NOCONFIRMATION, FOF_SILENT, FOF_NOERRORUI = 3, 0x40, 0x10, 0x4, 0x400
        op = SHFILEOPSTRUCTW(None, FO_DELETE, path + "\0", None,
                             FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI, False, None, None)
        return ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op)) == 0 and not op.fAnyOperationsAborted
    except (OSError, AttributeError, ValueError):  # AttributeError: no ctypes.windll off Windows
        return False


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=False).stdout.strip()


def git_mirrors(roots: list[Path], stale_days: int) -> list[dict]:
    """Git clones whose every commit is on a remote and that have no local changes: safe to re-clone."""
    out = []
    for root in roots:
        if not root.exists() or root.name.startswith("OneDrive"):
            continue
        for dirpath, dirnames, _ in os.walk(root):
            if ".git" in dirnames or (Path(dirpath) / ".git").is_file():
                repo = Path(dirpath)
                dirnames[:] = []
                dirty = len([l for l in git(repo, "status", "--porcelain", "--untracked-files=no").splitlines() if l])
                unpushed = len(git(repo, "rev-list", "--branches", "--not", "--remotes").splitlines())
                stash = len(git(repo, "stash", "list").splitlines())
                last = git(repo, "log", "-1", "--format=%ct") or "0"
                age = int((time.time() - int(last)) / 86400)
                out.append({"path": str(repo), "remote": git(repo, "remote", "get-url", "origin"), "dirty": dirty,
                            "unpushed_commits": unpushed, "stashes": stash, "days_since_last_commit": age,
                            "mirror_only": dirty == 0 and unpushed == 0 and stash == 0,
                            "stale": age >= stale_days})
                continue
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith("$")]
    return out


def recycle_bin_gb() -> float | None:
    try:
        ps = ("$i=(New-Object -ComObject Shell.Application).NameSpace(10).Items();"
              "($i | ForEach-Object { $_.ExtendedProperty('Size') } | Measure-Object -Sum).Sum")
        out = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps], capture_output=True, text=True,
                             check=False).stdout
        return round(float(out.strip() or 0) / 1e9, 2)
    except (OSError, ValueError):  # OSError: no powershell.exe off Windows
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--roots", nargs="*", type=Path)
    ap.add_argument("--min-mb", type=float, default=1.0)
    ap.add_argument("--min-age-days", type=float, default=7)
    ap.add_argument("--stale-days", type=int, default=30)
    ap.add_argument("--apply", action="store_true", help="send duplicate copies to the Recycle Bin")
    ap.add_argument("--out", type=Path, default=REPORTS)
    args = ap.parse_args(argv)
    roots = args.roots or DEFAULT_ROOTS
    start = time.time()
    stamp = time.strftime("%Y-%m-%d_%H%M")
    args.out.mkdir(parents=True, exist_ok=True)

    report = {"run": stamp, "mode": "APPLY" if args.apply else "DRY_RUN", "roots": [str(r) for r in roots],
              "free_gb_before": free_gb(HOME)}
    groups = find_duplicates(roots, int(args.min_mb * 1e6), args.min_age_days * 86400)
    report["duplicate_groups"] = len(groups)
    report["duplicate_files"] = sum(len(g["remove"]) for g in groups)
    report["reclaimable_gb"] = round(sum(g["size"] * len(g["remove"]) for g in groups) / 1e9, 2)

    moved = []
    if args.apply:
        manifest = args.out / f"recycled_{stamp}.csv"
        with open(manifest, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["recycled_path", "kept_identical_copy", "sha256", "bytes", "ok"])
            for g in groups:
                if not Path(g["keep"]).exists():
                    continue  # never remove the last copy
                for p in g["remove"]:
                    if sha256(Path(p)) != g["sha256"]:  # changed since the scan
                        continue
                    ok = recycle(p)
                    w.writerow([p, g["keep"], g["sha256"], g["size"], ok])
                    if ok:
                        moved.append(p)
        report["manifest"] = str(manifest)
    report["recycled_files"] = len(moved)
    report["git_mirrors"] = git_mirrors(roots, args.stale_days)
    report["recycle_bin_gb"] = recycle_bin_gb()
    report["free_gb_after"] = free_gb(HOME)
    report["seconds"] = round(time.time() - start)
    report["top_duplicates"] = groups[:50]

    (args.out / f"report_{stamp}.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    mirrors = [m for m in report["git_mirrors"] if m["mirror_only"] and m["stale"]]
    lines = [f"# Disk hygiene {stamp} ({report['mode']})", "",
             f"- C: free: {report['free_gb_before']} GB before, {report['free_gb_after']} GB after",
             (f"- Duplicates: {report['duplicate_files']} extra copies in {report['duplicate_groups']} groups, "
              f"{report['reclaimable_gb']} GB"),
             f"- Sent to Recycle Bin this run: {report['recycled_files']} files"
             + (f" (manifest: {report.get('manifest')})" if args.apply else " (dry run)"),
             f"- Recycle Bin now holds: {report['recycle_bin_gb']} GB (emptying it is your step)",
             f"- Stale git clones with nothing unpushed (safe to delete and re-clone): {len(mirrors)}", ""]
    for m in mirrors:
        lines.append(f"  - {m['path']} ({m['days_since_last_commit']} days, {m['remote']})")
    lines += ["", "## Largest duplicate groups (kept copy first)"]
    for g in groups[:15]:
        lines.append(f"- {g['size'] / 1e6:.1f} MB x{len(g['remove'])}: keep `{g['keep']}`; extra: "
                     + "; ".join(f"`{p}`" for p in g["remove"][:3]))
    md = args.out / f"report_{stamp}.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(md)
    print("\n".join(lines[:8]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
