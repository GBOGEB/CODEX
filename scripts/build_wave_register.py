#!/usr/bin/env python3
"""Build the federation wave register from local clones of member repos.

Usage:
  python scripts/build_wave_register.py --repo GBOGEB/CODEX=. \
      --repo GBOGEB/ABACUS=../ABACUS --private GBOGEB/cryoplant-project=../cryoplant-project ...

Writes federation/waves/WAVE_REGISTER.yaml (deterministic: no timestamps; each
repo is anchored by its HEAD SHA). Private repos (--private) contribute only
wave ids, path counts and their first directory anchor: no file names, titles
or content, because CODEX is public.

Stdlib + PyYAML. ASCII-only output.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NS_FILE = ROOT / "federation" / "waves" / "WAVE_NAMESPACES.yaml"
OUT_FILE = ROOT / "federation" / "waves" / "WAVE_REGISTER.yaml"
CONTENT_SOURCES = ("CODE_PURPLE_ITERATION_SERIES_v1.json", "CODE_PURPLE_BD_QUEUE_v1.json")
SKIP_DIRS = ("node_modules/", "vendor/", ".venv/", "site-packages/", "third_party/")

CP_RE = re.compile(r"(?<![A-Za-z0-9])W(\d+)\.C(\d+)\.I(\d+)(?:\.S(\d+))?")
BOOT_RE = re.compile(r"(?<![A-Za-z0-9])(?:[Ww]ave-0|W00([0-9]))(?![0-9])")
JADE_RE = re.compile(r"(?<![A-Za-z0-9])(?:N\+(\d+)|[Nn](\d+)_|P(\d{4}))(?![0-9])")
NUM_RE = re.compile(r"(?<![A-Za-z0-9])[Ww](?:ave[-_]?)?(\d{1,3})(?![0-9A-Za-z])")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def classify(path: str) -> list[tuple[str, str, str]]:
    """Return [(namespace, local_id, confidence)] for one tracked path."""
    hits: list[tuple[str, str, str]] = []
    low = path.lower()
    for m in CP_RE.finditer(path):
        hits.append(("CP", "W%s.C%s.I%s" % m.groups()[:3] + (".S%s" % m.group(4) if m.group(4) else ""), "exact"))
    if "mission-control/jade_temple/" in low:
        for m in JADE_RE.finditer(path):
            if m.group(3):
                hits.append(("JADE", "P" + m.group(3), "exact"))
            else:
                hits.append(("JADE", "N+" + (m.group(1) or m.group(2)), "exact"))
    for m in BOOT_RE.finditer(path):
        hits.append(("BOOT", "W00" + m.group(1) if m.group(1) else "Wave-0", "exact"))
    cp_spans = [m.span() for m in CP_RE.finditer(path)]
    for m in NUM_RE.finditer(path):
        if any(a <= m.start() < b for a, b in cp_spans):
            continue
        n = int(m.group(1))
        raw = m.group(0)
        if raw.upper().startswith("W00") or (n == 0 and "wave-0" in low):
            continue  # BOOT handled above
        if "governance/branch_hygiene/" in low and n <= 10:
            hits.append(("HYG", "W%d" % n, "exact"))
        elif "qps-triage-ultra/" in low and n <= 2:
            hits.append(("ULTRA", "W%d" % n, "exact"))
        elif n >= 10:
            hits.append(("QPS", "W%03d" % n, "exact"))
        else:
            hits.append(("QPS", "W%03d" % n, "inferred"))
    return hits


def read_pointers(repo: Path) -> dict:
    """Current-wave claims a repo makes about itself (agent entry pointers)."""
    out = {}
    cur = repo / "handover" / "CURRENT.json"
    if cur.is_file():
        try:
            d = json.loads(cur.read_text(encoding="utf-8"))
            if isinstance(d, dict) and d.get("wave"):
                out["handover/CURRENT.json"] = str(d["wave"])
        except (ValueError, OSError):
            pass
    dock = repo / ".mesh" / "MESH_DOCK.yaml"
    if dock.is_file():
        try:
            d = yaml.safe_load(dock.read_text(encoding="utf-8"))
            obj = ((d or {}).get("current_focus") or {}).get("object") if isinstance(d, dict) else None
            if obj:
                m = NUM_RE.search(str(obj))
                out[".mesh/MESH_DOCK.yaml#current_focus"] = "QPS:W%03d" % int(m.group(1)) if m else str(obj)[:60]
        except (yaml.YAMLError, OSError, AttributeError):
            pass
    return out


def scan(name: str, repo: Path, private: bool):
    files = [f for f in git(repo, "ls-files", "-z").split("\0") if f and not any(s in f for s in SKIP_DIRS)]
    waves: dict[tuple[str, str], dict] = {}
    hits_by_file = {f: set(classify(f)) for f in files}
    # Content sources: coordinates that live inside a file rather than in path names.
    for f in files:
        if f.endswith(CONTENT_SOURCES):
            try:
                text = (repo / f).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in CP_RE.finditer(text):
                wid = "W%s.C%s.I%s" % m.groups()[:3] + (".S%s" % m.group(4) if m.group(4) else "")
                hits_by_file[f].add(("CP", wid, "exact"))
    for f in files:
        for ns, wid, conf in hits_by_file[f]:
            e = waves.setdefault((ns, wid), {"paths": 0, "conf": set(), "anchors": collections.Counter(), "ev": []})
            e["paths"] += 1
            e["conf"].add(conf)
            seg = f.split("/")
            anchor = next(("/".join(seg[: i + 1]) for i, s in enumerate(seg[:-1]) if NUM_RE.search(s) or CP_RE.search(s)),
                          "/".join(seg[:-1]) or ".")
            e["anchors"][anchor] += 1
            if not private and len(e["ev"]) < 3:
                e["ev"].append(f)
    return {"head": git(repo, "rev-parse", "HEAD").strip(), "files": len(files),
            "pointers": {} if private else read_pointers(repo)}, waves


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", action="append", default=[], help="OWNER/NAME=PATH (public)")
    ap.add_argument("--private", action="append", default=[], help="OWNER/NAME=PATH (private: ids and counts only)")
    ap.add_argument("--out", default=str(OUT_FILE))
    a = ap.parse_args()
    ns_keys = [n["key"] for n in yaml.safe_load(NS_FILE.read_text(encoding="utf-8"))["namespaces"]]

    sources, merged = {}, collections.defaultdict(dict)
    for spec, private in [(s, False) for s in a.repo] + [(s, True) for s in a.private]:
        name, path = spec.split("=", 1)
        meta, waves = scan(name, Path(path).resolve(), private)
        meta["visibility"] = "private" if private else "public"
        sources[name] = meta
        for key, e in waves.items():
            entry = {"paths": e["paths"], "anchor": e["anchors"].most_common(1)[0][0]}
            if e["ev"]:
                entry["evidence"] = sorted(e["ev"])
            merged[key][name] = entry
            merged[key].setdefault("__conf", set()).update(e["conf"])

    def sort_key(k):
        ns, wid = k
        nums = [int(x) for x in re.findall(r"\d+", wid)] or [0]
        return (ns_keys.index(ns) if ns in ns_keys else 99, nums, wid)

    entries = []
    for (ns, wid) in sorted(merged, key=sort_key):
        repos = {r: v for r, v in merged[(ns, wid)].items() if r != "__conf"}
        conf = merged[(ns, wid)]["__conf"]
        entries.append({
            "key": "%s:%s" % (ns, wid), "namespace": ns, "id": wid,
            "confidence": "exact" if "exact" in conf else "inferred",
            "status": "OBSERVED", "repos": dict(sorted(repos.items())),
        })

    qps = sorted(int(e["id"][1:]) for e in entries if e["namespace"] == "QPS" and e["confidence"] == "exact")
    gaps = [n for n in range(qps[0], qps[-1] + 1) if n not in set(qps)] if qps else []
    by_ns = collections.Counter(e["namespace"] for e in entries)
    multi = sum(1 for e in entries if len(e["repos"]) > 1)
    pointers = {r: m["pointers"] for r, m in sorted(sources.items()) if m["pointers"]}
    register = {
        "schema": "codex.wave_register/0.1",
        "generated_by": "scripts/build_wave_register.py",
        "namespaces_ssot": "federation/waves/WAVE_NAMESPACES.yaml",
        "authority": "index_only",
        "authority_transfer": False,
        "maturity": "CANDIDATE",
        "sources": {r: {k: v for k, v in m.items() if k != "pointers"} for r, m in sorted(sources.items())},
        "stats": {
            "entries": len(entries),
            "by_namespace": dict(sorted(by_ns.items())),
            "multi_repo_entries": multi,
            "single_repo_entries": len(entries) - multi,
            "qps_exact_range": [qps[0], qps[-1]] if qps else None,
            "qps_exact_count": len(qps),
            "qps_gap_count": len(gaps),
        },
        "current_pointers": pointers,
        "waves": entries,
    }
    text = "# GENERATED by scripts/build_wave_register.py -- do not edit by hand.\n" + \
        yaml.safe_dump(register, sort_keys=False, width=120, allow_unicode=False)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(text, encoding="ascii", newline="\n")
    print("wave register: %d entries, namespaces %s, QPS W%s..W%s, %d gaps -> %s" % (
        len(entries), dict(by_ns), qps[0] if qps else "-", qps[-1] if qps else "-", len(gaps), a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
