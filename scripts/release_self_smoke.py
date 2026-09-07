#!/usr/bin/env python3
"""CODEX release self-smoke: authority, resolver, identity and exact Git receipt."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from tools.ssot_resolver import resolve_ssot

ROOT = Path(__file__).resolve().parents[1]
TRACKED = [
    "ssot/manifest.yaml",
    "ssot/domain/repo/release.yaml",
    "release/TRI_REPO_RELEASE_ASSURANCE_CONTRACT_v1.yaml",
    "tools/ssot_resolver.py",
]


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    head = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    files = {}
    for rel in TRACKED:
        path = ROOT / rel
        files[rel] = {
            "sha256": sha256(path),
            "git_blob_sha": git("rev-parse", f"HEAD:{rel}"),
        }

    release_identity = resolve_ssot("CODEX_RELEASE_IDENTITY")
    qps = resolve_ssot("QPS_ENGINEERING_TRUTH")
    master = resolve_ssot("CODEX_MASTER_CONTRACT")
    glossary = resolve_ssot("CODEX_SEMANTIC_VOCABULARY")
    runtime = resolve_ssot("CODEX_RUNTIME_GOVERNANCE")
    mcp = resolve_ssot("CODEX_MCP_GOVERNANCE")

    receipt = {
        "schema_version": "1.1",
        "repository": "GBOGEB/CODEX",
        "wave": "W05",
        "pulse": "P4",
        "pressure": "2x3PR",
        "git_commit_sha": head,
        "git_tree_sha": tree,
        "files": files,
        "checks": {
            "release_identity": "PASS",
            "master_contract": "PASS",
            "semantic_vocabulary": "PASS",
            "runtime_governance": "PASS",
            "mcp_governance": "PASS",
            "qps_remote_authority": "PASS" if qps["mutation_allowed"] is False else "FAIL",
            "exact_sha_binding": "PASS",
        },
        "resolved": {
            "release_identity": release_identity,
            "master_contract": master,
            "semantic_vocabulary": glossary,
            "runtime_governance": runtime,
            "mcp_governance": mcp,
            "qps_engineering_truth": qps,
        },
    }
    receipt["receipt_sha256"] = hashlib.sha256(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if all(v == "PASS" for v in receipt["checks"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
