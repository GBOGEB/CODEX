from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.parse
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


def anonymous_raw_fetch(path: str) -> tuple[int, bytes, float]:
    request = urllib.request.Request(raw_url(path), headers={"User-Agent": "QPS-M03-Parity/2.0"})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return int(response.status), response.read(), time.perf_counter() - started
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read(), time.perf_counter() - started


def api_url(path: str) -> str:
    encoded_path = urllib.parse.quote(path, safe="/")
    encoded_ref = urllib.parse.quote(TARGET_SHA, safe="")
    return f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{encoded_path}?ref={encoded_ref}"


def authenticated_api_fetch(path: str, token: str) -> tuple[int, bytes, float]:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "QPS-M03-Parity/2.0",
    }
    request = urllib.request.Request(api_url(path), headers=headers)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = int(response.status)
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read(), time.perf_counter() - started

    if status != 200:
        return status, json.dumps(payload).encode("utf-8"), time.perf_counter() - started
    if not isinstance(payload, dict) or payload.get("type") != "file":
        raise SystemExit("authenticated REST candidate did not return a file object")
    encoded = payload.get("content")
    if not isinstance(encoded, str):
        raise SystemExit("authenticated REST candidate returned no base64 content")
    return status, base64.b64decode(encoded), time.perf_counter() - started


def run_official(
    mcpcurl: Path,
    server: Path,
    path: str,
) -> tuple[dict, bytes, float]:
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
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
        timeout=45,
    )
    elapsed = time.perf_counter() - started
    if completed.returncode != 0:
        raise SystemExit(
            f"official MCP process failed rc={completed.returncode}: "
            f"{completed.stderr.decode('utf-8', errors='replace')}"
        )
    payload = json.loads(completed.stdout.decode("utf-8"))
    return payload, completed.stdout, elapsed


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
    parser = argparse.ArgumentParser(description="QPS M03 pragmatic content-read transport decision probe")
    parser.add_argument("--mcpcurl", required=True, type=Path)
    parser.add_argument("--server", required=True, type=Path)
    parser.add_argument("--out", default="m03_content_read_parity_receipt.json", type=Path)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GitHub token missing: cannot execute authenticated REST or official MCP candidate")

    # Preserve the FIRST RED as evidence. The local W56 helper currently uses this exact
    # anonymous raw transport. A 404 is therefore a measured viability defect, not a
    # reason to rewrite history or silently pretend that the legacy transport passed.
    anonymous_status, anonymous_bytes, anonymous_elapsed = anonymous_raw_fetch(TARGET_PATH)
    anonymous_viable = anonymous_status == 200

    # Pragmatic low-complexity candidate: GitHub Contents REST with the workflow token.
    # This is intentionally separate from the official MCP candidate so the cutover
    # decision can distinguish transport standardization benefit from runtime overhead.
    rest_status, rest_bytes, rest_elapsed = authenticated_api_fetch(TARGET_PATH, token)
    if rest_status != 200:
        raise SystemExit(f"authenticated REST candidate positive read returned HTTP {rest_status}")
    rest_blob = git_blob_sha1(rest_bytes)
    if rest_blob != EXPECTED_BLOB_SHA1:
        raise SystemExit(f"authenticated REST candidate blob SHA mismatch: {rest_blob}")

    official_payload, official_wire, official_elapsed = run_official(args.mcpcurl, args.server, TARGET_PATH)
    official_bytes, embedded_uri, success_texts = extract_embedded_bytes(official_payload)
    if TARGET_SHA not in embedded_uri:
        raise SystemExit("official embedded resource URI is not bound to exact target SHA")
    if rest_bytes != official_bytes:
        raise SystemExit("positive parity failed: authenticated REST bytes differ from official MCP embedded bytes")

    anonymous_missing_status, _, anonymous_missing_elapsed = anonymous_raw_fetch(MISSING_PATH)
    rest_missing_status, _, rest_missing_elapsed = authenticated_api_fetch(MISSING_PATH, token)
    if rest_missing_status != 404:
        raise SystemExit(f"authenticated REST missing-path classification expected 404, got {rest_missing_status}")

    official_missing_payload, official_missing_wire, official_missing_elapsed = run_official(
        args.mcpcurl, args.server, MISSING_PATH
    )
    official_not_found, official_missing_message = classify_official_not_found(official_missing_payload)
    if not official_not_found:
        raise SystemExit("official missing-path response did not map to NOT_FOUND/isError semantics")

    text_sha_candidates: list[str] = []
    for text in success_texts:
        text_sha_candidates.extend(re.findall(r"\b[0-9a-f]{40}\b", text.lower()))

    if anonymous_viable:
        anonymous_sha = sha256(anonymous_bytes)
        anonymous_byte_exact = anonymous_bytes == rest_bytes
        anonymous_disposition = "VIABLE_BUT_REDUNDANT_CANDIDATE"
    else:
        anonymous_sha = None
        anonymous_byte_exact = False
        anonymous_disposition = "CURRENTLY_NONVIABLE_IN_ACTIONS_CONTEXT"

    receipt = {
        "schema": "qps.m03.content_read_transport_decision.v2",
        "mission_id": "M03_GITHUB_MCP_SERVER",
        "pulse_id": "P_M03_CONTENT_READ_PARITY_FIRST_RED_REPAIR_01",
        "first_red": {
            "source_run_id": "34625309676",
            "job_id": "103348864135",
            "step": "Execute exact positive and NOT_FOUND parity",
            "observed_error": "legacy raw transport positive read returned HTTP 404",
            "classification": "LOCAL_LEGACY_TRANSPORT_ACCESS_VIABILITY",
            "not_official_mcp_failure": True,
        },
        "local_duplicate": {
            "repo": "GBOGEB/CODEX",
            "path": "scripts/qps_w56_verify_hash_receipt_v2.py",
            "transport": "raw.githubusercontent.com_via_urllib_without_auth_header",
            "function": "fetch_bytes",
        },
        "target": {
            "repo": f"{OWNER}/{REPO}",
            "sha": TARGET_SHA,
            "path": TARGET_PATH,
            "expected_blob_sha1": EXPECTED_BLOB_SHA1,
        },
        "legacy_anonymous_raw": {
            "positive_http_status": anonymous_status,
            "positive_sha256": anonymous_sha,
            "byte_exact_when_available": anonymous_byte_exact,
            "missing_http_status": anonymous_missing_status,
            "positive_elapsed_s": round(anonymous_elapsed, 6),
            "missing_elapsed_s": round(anonymous_missing_elapsed, 6),
            "disposition": anonymous_disposition,
        },
        "minimal_authenticated_rest_candidate": {
            "transport": "api.github.com_contents_with_workflow_token",
            "positive_http_status": rest_status,
            "positive_sha256": sha256(rest_bytes),
            "blob_sha1": rest_blob,
            "missing_http_status": rest_missing_status,
            "missing_class": "NOT_FOUND",
            "positive_elapsed_s": round(rest_elapsed, 6),
            "missing_elapsed_s": round(rest_missing_elapsed, 6),
            "runtime_dependencies": ["python_stdlib", "workflow_token"],
            "result": "PASS",
        },
        "official_mcp_candidate": {
            "repo": "github/github-mcp-server",
            "source_sha": OFFICIAL_SHA,
            "toolset": "repos",
            "tool": "get_file_contents",
            "positive_embedded_sha256": sha256(official_bytes),
            "positive_byte_exact_vs_rest": rest_bytes == official_bytes,
            "embedded_uri": embedded_uri,
            "positive_wire_sha256": sha256(official_wire),
            "missing_class": "NOT_FOUND",
            "missing_is_error_and_not_found": official_not_found,
            "missing_wire_sha256": sha256(official_missing_wire),
            "missing_message_sha256": sha256(official_missing_message.encode("utf-8")),
            "positive_elapsed_s": round(official_elapsed, 6),
            "missing_elapsed_s": round(official_missing_elapsed, 6),
            "official_success_text_sha_candidates": sorted(set(text_sha_candidates)),
            "result": "PASS",
        },
        "permission_parity": {
            "status": "DEFER_NO_SAFE_DETERMINISTIC_PERMISSION_DENIED_FIXTURE",
            "credit": "NONE",
        },
        "decision_rule": {
            "agent_or_orchestration_transport": "PREFER_OFFICIAL_MCP_WHEN_SEMANTICS_AND_RUNTIME_COST_ARE_ACCEPTABLE",
            "tiny_deterministic_ci_fetch": "PREFER_MINIMAL_AUTHENTICATED_REST_WHEN_FULL_MCP_ADDS_NO_CONTROL_VALUE",
            "anonymous_raw_private_repo_path": "RETIRE_OR_REPAIR_DO_NOT_PRESERVE_AS_FALLBACK",
        },
        "result": "PASS_PRAGMATIC_PARITY_WITH_LEGACY_FIRST_RED_PRESERVED",
        "cutover_authority": "DECISION_EVIDENCE_ONLY_NO_DELETION",
    }
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
