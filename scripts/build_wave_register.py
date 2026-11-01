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
# What each indexed pointer means. Only "current" roles count toward consensus.
POINTER_ROLES = {
    "GLOB.yaml#wave": "current",
    ".mesh/MESH_DOCK.yaml#current_focus": "current",
    # Pinned to Wave-0/near-complete by scripts/validate_all.py: an open
    # bootstrap HOLD record, not a claim about the current federation wave.
    "handover/CURRENT.json": "bootstrap_record",
}
SKIP_DIRS = ("node_modules/", "vendor/", ".venv/", "site-packages/", "third_party/")

NUM_RE = re.compile(r"(?<![A-Za-z0-9])[Ww](?:ave[-_]?)?(\d{1,3})(?![0-9A-Za-z])")
INCUBATOR_PREFIX_RE = re.compile(r"^\d{2}_[Ww]\d{2}_\d{2}_\d{2}__")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def load_rules() -> list[dict]:
    rules = yaml.safe_load(NS_FILE.read_text(encoding="utf-8"))["namespaces"]
    return [{**rule, "regex": re.compile(rule["id_regex"])} for rule in rules]


def normalize(rule: dict, raw: str) -> str:
    kind = rule["normalization"]
    if kind == "numeric":
        number = int(re.search(r"\d+", raw).group())
        return rule["id_format"].format(number=number)
    if kind == "coordinate":
        return raw.upper()
    if kind == "bootstrap":
        return "Wave-0" if raw.lower() == "wave-0" else raw.upper()
    if kind == "pulse":
        return raw if raw.startswith("P") else "N+" + re.search(r"\d+", raw).group()
    raise ValueError(f"Unknown normalization: {kind}")


def classify(path: str, rules: list[dict] | None = None, *,
             context: str | None = None, content: bool = False) -> list[tuple[str, str, str]]:
    """Return [(namespace, local_id, confidence)] for one tracked path."""
    hits: list[tuple[str, str, str]] = []
    rules = load_rules() if rules is None else rules
    low = (context if context is not None else path).lower()
    if not content and (low.startswith("incubator/") or "/incubator/" in low):
        parent, sep, filename = path.rpartition("/")
        path = parent + sep + INCUBATOR_PREFIX_RE.sub("", filename)
    claimed = []
    for rule in rules:
        if rule.get("path_context", "").lower() not in low:
            continue
        if content and not low.endswith(tuple(s.lower() for s in rule.get("content_sources", []))):
            continue
        for m in rule["regex"].finditer(path):
            if any(a < m.end() and m.start() < b for a, b in claimed):
                continue
            if rule["normalization"] == "numeric":
                n = int(re.search(r"\d+", m.group()).group())
                if not rule.get("min_id", 0) <= n <= rule.get("max_id", 999):
                    continue
            hits.append((rule["key"], normalize(rule, m.group()), "exact"))
            claimed.append(m.span())
    if not content:
        for m in NUM_RE.finditer(path):
            if not any(a < m.end() and m.start() < b for a, b in claimed):
                hits.append(("QPS", f"W{int(m.group(1)):03d}", "inferred"))
    return hits


def read_pointers(repo: Path, head: str, files: list[str], rules: list[dict]) -> tuple[dict, dict]:
    """Current-wave claims a repo makes about itself (agent entry pointers)."""
    out = {}
    observations = {}
    cur = "handover/CURRENT.json"
    if cur in files:
        try:
            d = json.loads(git(repo, "show", f"{head}:{cur}"))
            if isinstance(d, dict) and d.get("wave"):
                out["handover/CURRENT.json"] = str(d["wave"])
                observations[cur] = classify(str(d["wave"]), rules, context=cur)
        except (ValueError, subprocess.CalledProcessError):
            pass
    dock = ".mesh/MESH_DOCK.yaml"
    if dock in files:
        try:
            d = yaml.safe_load(git(repo, "show", f"{head}:{dock}"))
            obj = ((d or {}).get("current_focus") or {}).get("object") if isinstance(d, dict) else None
            if obj:
                hits = classify(str(obj), rules, context=dock)
                out[".mesh/MESH_DOCK.yaml#current_focus"] = f"{hits[0][0]}:{hits[0][1]}" if hits else str(obj)[:60]
                observations[dock] = hits
        except (yaml.YAMLError, subprocess.CalledProcessError, AttributeError):
            pass
    glob = "GLOB.yaml"
    if glob in files:
        try:
            d = yaml.safe_load(git(repo, "show", f"{head}:{glob}"))
            declared = d.get("wave") if isinstance(d, dict) else None
            if declared:
                hits = classify(str(declared), rules, context=glob)
                out["GLOB.yaml#wave"] = f"{hits[0][0]}:{hits[0][1]}" if hits else str(declared)[:60]
                observations[glob] = hits
        except (yaml.YAMLError, subprocess.CalledProcessError):
            pass
    return out, observations


def scan(name: str, repo: Path, private: bool, rules: list[dict] | None = None):
    rules = load_rules() if rules is None else rules
    head = git(repo, "rev-parse", "HEAD").strip()
    files = [f for f in git(repo, "ls-tree", "-r", "--name-only", "-z", head).split("\0")
             if f and not any(s in f for s in SKIP_DIRS)]
    waves: dict[tuple[str, str], dict] = {}
    hits_by_file = {f: set(classify(f, rules)) for f in files}
    # Content sources: coordinates that live inside a file rather than in path names.
    for f in files:
        if any(f.endswith(tuple(rule.get("content_sources", []))) for rule in rules):
            try:
                text = git(repo, "show", f"{head}:{f}")
            except subprocess.CalledProcessError:
                continue
            hits_by_file[f].update(classify(text, rules, context=f, content=True))
    pointers, pointer_hits = ({}, {}) if private else read_pointers(repo, head, files, rules)
    for f, hits in pointer_hits.items():
        hits_by_file[f].update(hits)
    for f in files:
        for ns, wid, conf in sorted(hits_by_file[f]):
            e = waves.setdefault((ns, wid), {"paths": 0, "conf": set(), "anchors": collections.Counter(), "ev": []})
            e["paths"] += 1
            e["conf"].add(conf)
            seg = f.split("/")
            anchor = next(("/".join(seg[: i + 1]) for i, s in enumerate(seg[:-1]) if classify(s, rules, context=f)),
                          "/".join(seg[:-1]) or ".")
            e["anchors"][anchor] += 1
            if not private and len(e["ev"]) < 3:
                e["ev"].append(f)
    return {"head": head, "files": len(files), "pointers": pointers}, waves


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", action="append", default=[], help="OWNER/NAME=PATH (public)")
    ap.add_argument("--private", action="append", default=[], help="OWNER/NAME=PATH (private: ids and counts only)")
    ap.add_argument("--out", default=str(OUT_FILE))
    a = ap.parse_args()
    rules = load_rules()
    ns_keys = [n["key"] for n in rules]

    sources, merged = {}, collections.defaultdict(dict)
    for spec, private in [(s, False) for s in a.repo] + [(s, True) for s in a.private]:
        name, path = spec.split("=", 1)
        meta, waves = scan(name, Path(path).resolve(), private, rules)
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
        "pointer_roles": POINTER_ROLES,
        "current_wave_consensus": sorted({v for m in pointers.values() for k, v in m.items()
                                          if POINTER_ROLES.get(k) == "current"}),
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
