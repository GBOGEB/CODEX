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

try:  # run as `python scripts/build_wave_register.py`
    import wave_claims
except ImportError:  # imported as `scripts.build_wave_register`
    from scripts import wave_claims

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


PARENT_KEYS = ("parent_wave", "parent_waves")
CHILD_KEYS = ("id", "wave", "wave_id")
# Lane suffixes (W111A, W43-M05) belong to their base wave for lineage purposes.
LANE_RE = re.compile(r"(?<![A-Za-z0-9])[Ww](\d{2,3})(?:[A-Z]|-M\d+)?(?![0-9A-Za-z])")


def wave_keys(text: str, rules: list[dict], context: str) -> list[str]:
    """Canonical keys named by a value or path; lane suffixes fold to the base wave."""
    hits = [f"{ns}:{wid}" for ns, wid, conf in classify(text, rules, context=context) if conf == "exact"]
    if not hits:
        hits = [f"QPS:W{int(m.group(1)):03d}" for m in LANE_RE.finditer(text) if int(m.group(1)) >= 10]
    return list(dict.fromkeys(hits))


def scan_lineage(repo: Path, head: str, rules: list[dict]) -> tuple[collections.Counter, int]:
    """(child, parent) edges from parent_wave/parent_waves fields in committed YAML/JSON."""
    try:
        listed = git(repo, "grep", "-l", "-E", r"parent_waves?\"?\s*:", head, "--", "*.yaml", "*.yml", "*.json")
    except subprocess.CalledProcessError:
        return collections.Counter(), 0
    edges, unresolved = collections.Counter(), 0
    for line in listed.splitlines():
        f = line.split(":", 1)[1]
        if any(s in f for s in SKIP_DIRS):
            continue
        try:
            doc = yaml.safe_load(git(repo, "show", f"{head}:{f}"))
        except (yaml.YAMLError, subprocess.CalledProcessError):
            continue
        stack = [doc]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
                continue
            if not isinstance(node, dict):
                continue
            stack.extend(node.values())
            raw = [v for k in PARENT_KEYS if k in node for v in (node[k] if isinstance(node[k], list) else [node[k]])]
            parents = [k for v in raw if isinstance(v, (str, int)) for k in wave_keys(str(v), rules, f)]
            if not parents:
                continue
            own = next((node[k] for k in CHILD_KEYS if isinstance(node.get(k), str)), None)
            if own:
                named = wave_keys(own, rules, f)
            else:  # the file name outranks folders: records are often vendored into another wave's inputs
                named = wave_keys(f.rsplit("/", 1)[-1], rules, f) or wave_keys(f, rules, f)
            children = [c for c in named if c not in parents]
            if len(children) != 1:
                unresolved += 1
                continue
            for par in parents:
                edges[(children[0], par)] += 1
    return edges, unresolved


def kahn(edges: set[tuple[str, str]]) -> dict:
    """Kahn topological sort over parent -> child; reports acyclicity and longest chain."""
    nodes = {n for e in edges for n in e}
    indeg = {n: 0 for n in nodes}
    kids = collections.defaultdict(list)
    for child, parent in edges:
        kids[parent].append(child)
        indeg[child] += 1
    queue = sorted(n for n in nodes if indeg[n] == 0)
    depth = {n: 0 for n in queue}
    seen = 0
    while queue:
        n = queue.pop(0)
        seen += 1
        for c in sorted(kids[n]):
            depth[c] = max(depth.get(c, 0), depth[n] + 1)
            indeg[c] -= 1
            if indeg[c] == 0:
                queue.append(c)
    return {"nodes": len(nodes), "roots": sum(1 for n in nodes if not any(c == n for c, _ in edges)),
            "acyclic": seen == len(nodes), "nodes_in_cycles": len(nodes) - seen,
            "longest_chain": max(depth.values(), default=0)}


def read_claims(repo: Path, head: str) -> dict | None:
    """The repo's own wave claims (its prerogative), read at the exact source commit."""
    try:
        return yaml.safe_load(git(repo, "show", f"{head}:{wave_claims.CLAIMS_PATH}"))
    except subprocess.CalledProcessError:
        return None
    except yaml.YAMLError:
        return {"schema": "unparseable"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", action="append", default=[], help="OWNER/NAME=PATH (public)")
    ap.add_argument("--private", action="append", default=[], help="OWNER/NAME=PATH (private: ids and counts only)")
    ap.add_argument("--out", default=str(OUT_FILE))
    ap.add_argument("--strict", action="store_true", help="exit 2 when the claims roll-up has errors")
    a = ap.parse_args()
    rules = load_rules()
    ns_keys = [n["key"] for n in rules]

    sources, merged = {}, collections.defaultdict(dict)
    lineage: dict[tuple[str, str], dict] = collections.defaultdict(dict)
    claim_sets: dict[str, tuple[dict, bool]] = {}
    for spec, private in [(s, False) for s in a.repo] + [(s, True) for s in a.private]:
        name, path = spec.split("=", 1)
        meta, waves = scan(name, Path(path).resolve(), private, rules)
        meta["visibility"] = "private" if private else "public"
        sources[name] = meta
        edges, unresolved = scan_lineage(Path(path).resolve(), meta["head"], rules)
        meta["lineage_unresolved"] = unresolved
        doc = read_claims(Path(path).resolve(), meta["head"])
        meta["claims_file"] = doc is not None
        if doc is not None:
            claim_sets[name] = (doc, private)
        for (child, parent), n in edges.items():
            lineage[(child, parent)][name] = n
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
            "key": f"{ns}:{wid}", "namespace": ns, "id": wid,
            "confidence": "exact" if "exact" in conf else "inferred",
            "status": "OBSERVED", "repos": dict(sorted(repos.items())),
        })

    naming = wave_claims.load_naming_rules()
    observed = {e["key"]: set(e["repos"]) for e in entries}
    # Retired names and aliases stay reserved: carry the previous register's index forward.
    previous: list[dict] = []
    if Path(a.out).is_file():
        try:
            prior = yaml.safe_load(Path(a.out).read_text(encoding="utf-8")) or {}
            previous = list((prior.get("dedup") or {}).get("reserved") or [])
        except yaml.YAMLError:
            previous = []
    claims, violations, census = wave_claims.rollup(
        claim_sets, observed, set(lineage), naming, reserved=previous
    )
    reserved = census.pop("reserved")
    for e in entries:
        c = claims.get(e["key"])
        if c:
            e["claim"] = c
            if c["owner"] != "CONTESTED":
                e["status"] = c["status"]

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
        "lineage": {
            "source_fields": list(PARENT_KEYS),
            "stats": {"edges": len(lineage), **kahn(set(lineage))},
            "edges": [{"child": c, "parent": par, "repos": dict(sorted(r.items()))}
                      for (c, par), r in sorted(lineage.items(), key=lambda kv: (sort_key(tuple(kv[0][0].split(":", 1))),
                                                                                 kv[0][1]))],
        },
        "dedup": {
            "rules": "federation/waves/WAVE_NAMING_RULES.yaml",
            "claims_file": wave_claims.CLAIMS_PATH,
            "census": census,
            "reserved": reserved,
            "claimed_unobserved": {k: v for k, v in sorted(claims.items()) if k not in observed},
            "violations": violations,
        },
        "waves": entries,
    }
    text = "# GENERATED by scripts/build_wave_register.py -- do not edit by hand.\n" + \
        yaml.safe_dump(register, sort_keys=False, width=120, allow_unicode=False)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(text, encoding="ascii", newline="\n")
    lo, hi = (qps[0], qps[-1]) if qps else ("-", "-")
    print(f"wave register: {len(entries)} entries, namespaces {dict(by_ns)}, "
          f"QPS W{lo}..W{hi}, {len(gaps)} gaps -> {a.out}")
    errors = census["violations"]["error"]
    print(f"claims roll-up: {census['claims_files']} claims files, {census['claimed_keys']} claimed keys, "
          f"{errors} errors, {census['violations']['warning']} warnings")
    return 2 if a.strict and errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
