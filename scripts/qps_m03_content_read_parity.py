from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.request

OWNER = "GBOGEB"
REPO = "cryoplant-project"
TARGET_SHA = "f16d3c2e2f26309097f56cb962b3e8c25c970b13"
TARGET_PATH = "ocd-adr/20_canonical/architecture/QPS_COMPONENT_UTILITY_ICD_SSOT_W55_v0.1.yaml"
MISSING_PATH = "__qps_m03_missing__/definitely-not-present.yaml"
EXPECTED_BLOB_SHA1 = "dd9098b411bb1d5b447c1630c9401c9fb4b8af71"
OFFICIAL_SHA = "7d13a7ad6f2a17f351a6d77ce280c85ae1821f4d"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def raw_url(path: str) -> str:
    return f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{TARGET_SHA}/{path}"


def raw_fetch(path: str) -> tuple[int, bytes]:
    request = urllib.request.Request(raw_url(path), headers={"User-Agent": "QPS-M03-Parity/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return int(response.status), response.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read()


def run_official(
    mcpcurl: Path,
    server: Path,
    path: str,
) -> tuple[dict, bytes]:
    server_cmd = f"{server} stdio --toolsets=repos"
    command = [
        str(mcpcurl),
        "--pretty=false",
        "--stdio-server-cmd",
        server_cmd,
        "tools",
        "get_file_contents",
        "--owner",
        OWNER,
        "--repo",
        REPO,
        "--path",
        path,
        "--sha",
        TARGET_SHA,
    ]
    completed = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
        timeout=45,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"official MCP process failed rc={completed.returncode}: "
            f"{completed.stderr.decode('utf-8', errors='replace')}"
        )
    payload = json.loads(completed.stdout.decode("utf-8"))
    return payload, completed.stdout


def result_content(payload: dict) -> list[dict]:
    if "error" in payload:
        raise SystemExit(f"official MCP JSON-RPC error: {payload['error']}")
    result = payload.get("result") or {}
    content = result.get("content") or []
    if not isinstance(content, list):
        raise SystemExit("official MCP content is not a list")
    return [item for item in content if isinstance(item, dict)]


def extract_embedded_bytes(payload: dict) -> tuple[bytes, str, list[str]]:
    result = payload.get("result") or {}
    if result.get("isError") is True:
        raise SystemExit("positive official MCP read returned isError=true")
    content = result_content(payload)
    texts = [str(item.get("text", "")) for item in content if item.get("type") == "text"]
    resources = [item.get("resource") or {} for item in content if item.get("type") == "resource"]
    if not resources:
        raise SystemExit("positive official MCP read returned no embedded resource")
    resource = resources[0]
    uri = str(resource.get("uri", ""))
    text = resource.get("text")
    if not isinstance(text, str):
        raise SystemExit("positive official MCP embedded resource has no text body")
    return text.encode("utf-8"), uri, texts


def classify_official_not_found(payload: dict) -> tuple[bool, str]:
    result = payload.get("result") or {}
    content = result_content(payload)
    texts = [str(item.get("text", "")) for item in content if item.get("type") == "text"]
    message = "\n".join(texts)
    normalized = message.lower()
    is_error = result.get("isError") is True
    not_found = (
        "404" in normalized
        or "not found" in normalized
        or "no such" in normalized
        or "failed to get" in normalized
    )
    return bool(is_error and not_found), message


def main() -> int:
    parser = argparse.ArgumentParser(description="QPS M03 exact content-read transport parity")
    parser.add_argument("--mcpcurl", required=True, type=Path)
    parser.add_argument("--server", required=True, type=Path)
    parser.add_argument("--out", default="m03_content_read_parity_receipt.json", type=Path)
    args = parser.parse_args()

    raw_status, raw_bytes = raw_fetch(TARGET_PATH)
    if raw_status != 200:
        raise SystemExit(f"legacy raw transport positive read returned HTTP {raw_status}")

    raw_blob = git_blob_sha1(raw_bytes)
    if raw_blob != EXPECTED_BLOB_SHA1:
        raise SystemExit(f"legacy raw transport blob SHA mismatch: {raw_blob}")

    official_payload, official_wire = run_official(args.mcpcurl, args.server, TARGET_PATH)
    official_bytes, embedded_uri, success_texts = extract_embedded_bytes(official_payload)

    if TARGET_SHA not in embedded_uri:
        raise SystemExit("official embedded resource URI is not bound to exact target SHA")
    if raw_bytes != official_bytes:
        raise SystemExit(
            "positive transport parity failed: legacy raw bytes differ from official MCP embedded bytes"
        )

    raw_missing_status, _ = raw_fetch(MISSING_PATH)
    if raw_missing_status != 404:
        raise SystemExit(f"legacy missing-path classification expected 404, got {raw_missing_status}")

    official_missing_payload, official_missing_wire = run_official(
        args.mcpcurl, args.server, MISSING_PATH
    )
    official_not_found, official_missing_message = classify_official_not_found(
        official_missing_payload
    )
    if not official_not_found:
        raise SystemExit(
            "official missing-path response did not map to NOT_FOUND/isError semantics"
        )

    text_sha_candidates = []
    for text in success_texts:
        text_sha_candidates.extend(re.findall(r"\b[0-9a-f]{40}\b", text.lower()))

    receipt = {
        "schema": "qps.m03.content_read_transport_parity.v1",
        "mission_id": "M03_GITHUB_MCP_SERVER",
        "pulse_id": "P_M03_CONTENT_READ_PARITY_01",
        "local_duplicate": {
            "repo": "GBOGEB/CODEX",
            "path": "scripts/qps_w56_verify_hash_receipt_v2.py",
            "transport": "raw.githubusercontent.com_via_urllib",
            "function": "fetch_bytes",
        },
        "target": {
            "repo": f"{OWNER}/{REPO}",
            "sha": TARGET_SHA,
            "path": TARGET_PATH,
            "expected_blob_sha1": EXPECTED_BLOB_SHA1,
        },
        "official_transport": {
            "repo": "github/github-mcp-server",
            "source_sha": OFFICIAL_SHA,
            "toolset": "repos",
            "tool": "get_file_contents",
        },
        "positive_parity": {
            "legacy_http_status": raw_status,
            "raw_sha256": sha256(raw_bytes),
            "official_embedded_sha256": sha256(official_bytes),
            "byte_exact": raw_bytes == official_bytes,
            "embedded_uri": embedded_uri,
            "official_wire_sha256": sha256(official_wire),
            "official_success_text_sha_candidates": sorted(set(text_sha_candidates)),
        },
        "missing_resource_parity": {
            "legacy_http_status": raw_missing_status,
            "legacy_class": "NOT_FOUND",
            "official_is_error_and_not_found": official_not_found,
            "official_class": "NOT_FOUND" if official_not_found else "UNCLASSIFIED",
            "official_wire_sha256": sha256(official_missing_wire),
            "official_message_sha256": sha256(official_missing_message.encode("utf-8")),
        },
        "permission_parity": {
            "status": "DEFER_NO_SAFE_DETERMINISTIC_PERMISSION_DENIED_FIXTURE",
            "credit": "NONE",
        },
        "result": "PASS_POSITIVE_AND_NOT_FOUND_PARITY_PERMISSION_DEFERRED",
        "cutover_authority": "NONE_PARITY_EVIDENCE_ONLY",
    }
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
