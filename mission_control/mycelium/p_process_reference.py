"""Read-only CODEX MYCELIUM consumer for QPS P-process native artifacts.

This tool verifies a pinned producer artifact and emits a DEFER receipt, never
mutating CODEX SSOT, authorizing execution, or accepting QPS engineering truth.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

SCHEMA = "mycelium.p_process.candidate/1.0"
REPOS = frozenset("GBOGEB/" + p for p in (
    "ABACUS", "CODEX", "Q_engineering_tools", "cryoplant-project",
    "gg_MATH", "pipeline-automation-hub"))
PATHS = {
    "state": "p-process/data/p_state.json",
    "census": "p-process/code-purple/kit/census.json",
    "everred": "p-process/everred/data/everred.json",
    "drift": "p-process/rulesets/drift.json",
}
SHA = re.compile(r"[0-9a-f]{40}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
ROOT = re.compile(r"root:([A-Z]+-RC-\d{4}-\d{4})\Z")
OWNERS = {"ABACUS": "ABACUS", "CODEX": "CODEX", "CRYO": "cryoplant-project",
          "GGMATH": "gg_MATH", "QET": "Q_engineering_tools", "PAH": "pipeline-automation-hub"}


def need(condition: bool, msg: str) -> None:
    if not condition:
        raise ValueError("MYCELIUM_DEFER: " + msg)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate(candidate: dict, blobs: dict[str, bytes], expected_sha: str) -> dict:
    """Semantic parity is evidence only. CODEX owner acceptance stays separate."""
    need(isinstance(expected_sha, str) and SHA.fullmatch(expected_sha),
         "invalid expected SHA")
    need(isinstance(candidate, dict) and candidate.get("schema") == SCHEMA,
         "candidate schema")
    for key in ("authority_transfer", "mutation_enabled", "dispatch_authorized"):
        need(candidate.get(key) is False, "forbidden promotion " + key)
    for key in ("formal_credit_delta", "engineering_credit_delta"):
        need(type(candidate.get(key)) is int and candidate[key] == 0,
             "forbidden promotion " + key)
    need(candidate.get("merge_admission") == "HOLD" and
         candidate.get("consumer_acceptance") == "WITHHELD",
         "forbidden admission or acceptance promotion")
    target = candidate.get("target") or {}
    need(target.get("repository") == "GBOGEB/CODEX" and
         target.get("surface") == "mission_control/mycelium" and
         target.get("mechanism") == "REFERENCE_CANDIDATE" and
         target.get("owner_acceptance_required") is True, "target authority")
    src = candidate.get("source") or {}
    need(src.get("repository") == "GBOGEB/pipeline-automation-hub" and
         src.get("commit_sha") == expected_sha, "stale producer head")
    digests = src.get("data_digests_sha256")
    need(isinstance(digests, dict) and set(digests) == set(PATHS) and
         isinstance(blobs, dict) and set(blobs) == set(PATHS), "source population")
    for k in PATHS:
        need(isinstance(digests[k], str) and DIGEST.fullmatch(digests[k]) and
             isinstance(blobs[k], bytes) and sha256(blobs[k]) == digests[k],
             "source digest " + k)
    evidence = {key: json.loads(raw) for key, raw in blobs.items()}
    inc = candidate.get("incident") or {}
    c = evidence["census"]
    need(evidence["state"].get("lifted") is False and c.get("lifted") is False
         and inc.get("lifted") is False, "lift cannot be inferred")
    need(isinstance(c.get("lift"), list) and
         inc.get("criteria_total") == len(c["lift"]) and
         inc.get("criteria_met") == sum(x.get("ok") is True for x in c["lift"]),
         "lift denominator")
    need(set(evidence["state"].get("repos", {})) == REPOS and
         set(evidence["drift"].get("repos", {})) == REPOS, "repo population")
    roots = evidence["everred"].get("roots")
    need(isinstance(roots, list) and bool(roots), "root source absent")
    ids = ["root:" + r["id"] for r in roots]
    need(len(set(ids)) == len(ids), "duplicate source roots")
    root_ids = set(ids)
    repo_ids = {"repo:" + repo for repo in REPOS}
    nodes, edges = candidate.get("nodes"), candidate.get("edges")
    need(isinstance(nodes, list) and isinstance(edges, list), "graph absent")
    index = {}
    for node in nodes:
        need(isinstance(node, dict) and isinstance(node.get("id"), str),
             "node malformed")
        nid = node["id"]
        need(nid not in index and node.get("evidence") == "PRODUCER_SNAPSHOT",
             "duplicate or promoted node")
        index[nid] = node
    need(set(index) == repo_ids | root_ids and len(index) == len(repo_ids)+len(root_ids),
         "node population mismatch")
    for repo in REPOS:
        node = index["repo:"+repo]
        state = evidence["state"]["repos"][repo]
        need(node.get("kind") == "repository" and node.get("owner") == repo and
             node.get("mode") == state["mode"] and
             node.get("ruleset") == state["ruleset"], "repo state drift")
    for root in roots:
        rid = "root:" + root["id"]
        need(ROOT.fullmatch(rid), "malformed root identity")
        family = root["id"].split("-")[0]
        need(family in OWNERS, "unknown root authority")
        repo = "GBOGEB/" + OWNERS[family]
        node = index[rid]
        need(node.get("kind") == "issue" and node.get("owner") == repo and
             node.get("state") == root.get("state") and
             node.get("severity") == root.get("severity"),
             "root state drift")
    need(len(edges) == len(root_ids), "edge denominator mismatch")
    seen = set()
    for edge in edges:
        need(isinstance(edge, dict) and edge.get("kind") == "references" and
             edge.get("evidence") == "DECLARED_SOURCE_LINK", "promoted edge")
        fr, to = edge.get("from"), edge.get("to")
        need(fr in root_ids and to in repo_ids and (fr, to) not in seen,
             "orphan or duplicate edge")
        need(to == "repo:" + index[fr]["owner"], "cross-authority edge")
        seen.add((fr, to))
    return {
        "schema": "mycelium.p_process.review_receipt/1.0",
        "producer_repository": src["repository"], "producer_sha": expected_sha,
        "source_digests_sha256": digests,
        "checked_repos": len(REPOS), "checked_roots": len(root_ids),
        "checked_edges": len(edges), "source_parity": "PASS",
        "binding_class": "PRODUCER_NATIVE_ARTIFACT_VALIDATED_LOCALLY",
        "decision": "DEFER", "consumer_acceptance": "WITHHELD",
        "native_consumer_run": None, "independent_review": None,
        "merge_admission": "HOLD", "mutation_enabled": False,
        "authority_transfer": False, "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
        "next_legal_transition": "OWNER_REVIEW_THEN_NATIVE_CONSUMER_REPLAY"
    }


def members(z: zipfile.ZipFile) -> set[str]:
    names = set()
    total = 0
    for info in z.infolist():
        name = info.filename
        need(name and name not in names and not name.startswith("/") and
             "\\" not in name and all(p not in ("", ".", "..") for p in name.split("/")),
             "unsafe archive member")
        need(info.file_size <= 50_000_000, "archive member over limit")
        need((info.external_attr >> 16) & 0o170000 != 0o120000,
             "archive symlink")
        total += info.file_size
        need(total <= 150_000_000, "archive size over limit")
        names.add(name)
    need(z.testzip() is None, "archive CRC")
    return names


def from_archives(path: Path, expected_sha: str) -> dict:
    """Validate Actions artifact outer ZIP and deterministic site inner ZIP."""
    with zipfile.ZipFile(path) as outer:
        names = members(outer)
        need("mycelium-p-process-candidate.json" in names, "candidate missing")
        candidate = json.loads(outer.read("mycelium-p-process-candidate.json"))
        zips = [name for name in names if name.startswith("p-process-site-") and name.endswith(".zip")]
        need(len(zips) == 1, "ambiguous nested site archive")
        nested = outer.read(zips[0])
        need(zips[0]+".sha256" in names and
             outer.read(zips[0]+".sha256").decode().split()[0] == sha256(nested),
             "nested ZIP SHA mismatch")
    with zipfile.ZipFile(io.BytesIO(nested)) as site:
        names = members(site)
        need("p-process/manifest.json" in names, "manifest absent")
        manifest = json.loads(site.read("p-process/manifest.json"))
        digests = manifest.get("files_sha256")
        need(isinstance(digests, dict) and
             {"p-process/"+k for k in digests} | {"p-process/manifest.json"} == names,
             "site manifest population")
        for name, digest in digests.items():
            need(isinstance(digest, str) and DIGEST.fullmatch(digest) and
                 sha256(site.read("p-process/"+name)) == digest,
                 "site member digest " + name)
        blobs = {name: site.read(rel) for name, rel in PATHS.items()}
    result = validate(candidate, blobs, expected_sha)
    result["outer_sha256"] = sha256(path.read_bytes())
    result["site_zip_sha256"] = sha256(nested)
    result["manifest_verified_files"] = len(digests)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact-zip", type=Path, required=True)
    ap.add_argument("--producer-sha", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    result = from_archives(args.artifact_zip, args.producer_sha)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print("MYCELIUM_SOURCE_PARITY=PASS; ACCEPTANCE=WITHHELD")


if __name__ == "__main__":
    main()
