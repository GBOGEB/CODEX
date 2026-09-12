from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

# Cross-repo target exercised by the real W56 helper.
CHILD_OWNER = "GBOGEB"
CHILD_REPO = "cryoplant-project"
CHILD_SHA = "f16d3c2e2f26309097f56cb962b3e8c25c970b13"
CHILD_PATH = "ocd-adr/20_canonical/architecture/QPS_COMPONENT_UTILITY_ICD_SSOT_W55_v0.1.yaml"
EXPECTED_CHILD_BLOB_SHA1 = "dd9098b411bb1d5b447c1630c9401c9fb4b8af71"

# Same-repo positive control already used by the independent M03 consumer.
CONTROL_OWNER = "GBOGEB"
CONTROL_REPO = "CODEX"
CONTROL_SHA = "1a80176358ffde62459cd257455a51402c847302"
CONTROL_PATH = "docs/qps_dow_keb_receipt_binding_policy.md"

OFFICIAL_SHA = "7d13a7ad6f2a17f351a6d77ce280c85ae1821f4d"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def anonymous_raw_fetch(owner: str, repo: str, sha: str, path: str) -> tuple[int, bytes, float]:
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "QPS-M03-Parity/3.0"})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return int(response.status), response.read(), time.perf_counter() - started
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read(), time.perf_counter() - started


def authenticated_api_fetch(
    owner: str,
    repo: str,
    sha: str,
    path: str,
    token: str,
) -> tuple[int, bytes, float]:
    encoded_path = urllib.parse.quote(path, safe="/")
    encoded_ref = urllib.parse.quote(sha, safe="")
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{encoded_path}?ref={encoded_ref}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "QPS-M03-Parity/3.0",
    }
    request = urllib.request.Request(url, headers=headers)
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
        raise SystemExit("authenticated REST positive control did not return a file object")
    encoded = payload.get("content")
    if not isinstance(encoded, str):
        raise SystemExit("authenticated REST positive control returned no base64 content")
    return status, base64.b64decode(encoded), time.perf_counter() - started


def run_official(
    mcpcurl: Path,
    server: Path,
    owner: str,
    repo: str,
    sha: str,
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
        owner,
        "--repo",
        repo,
        "--path",
        path,
        "--sha",
        sha,
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


def extract_success_bytes(payload: dict) -> tuple[bytes, str]:
    result = payload.get("result") or {}
    if result.get("isError") is True:
        raise SystemExit("official MCP positive control returned isError=true")
    resources = [item.get("resource") or {} for item in result_content(payload) if item.get("type") == "resource"]
    if not resources:
        raise SystemExit("official MCP positive control returned no embedded resource")
    resource = resources[0]
    uri = str(resource.get("uri", ""))
    text = resource.get("text")
    if not isinstance(text, str):
        raise SystemExit("official MCP positive control embedded resource has no text body")
    return text.encode("utf-8"), uri


def classify_official_not_found(payload: dict) -> tuple[bool, str]:
    result = payload.get("result") or {}
    texts = [str(item.get("text", "")) for item in result_content(payload) if item.get("type") == "text"]
    message = "\n".join(texts)
    normalized = message.lower()
    is_error = result.get("isError") is True
    not_found = "404" in normalized or "not found" in normalized or "failed to get" in normalized
    return bool(is_error and not_found), message


def main() -> int:
    parser = argparse.ArgumentParser(description="QPS M03 pragmatic transport/auth-boundary decision probe")
    parser.add_argument("--mcpcurl", required=True, type=Path)
    parser.add_argument("--server", required=True, type=Path)
    parser.add_argument("--out", default="m03_content_read_parity_receipt.json", type=Path)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GitHub token missing")

    # Positive same-repo control: prove both viable transports work with this job token.
    rest_control_status, rest_control_bytes, rest_control_elapsed = authenticated_api_fetch(
        CONTROL_OWNER, CONTROL_REPO, CONTROL_SHA, CONTROL_PATH, token
    )
    if rest_control_status != 200:
        raise SystemExit(f"same-repo REST positive control returned HTTP {rest_control_status}")

    mcp_control_payload, mcp_control_wire, mcp_control_elapsed = run_official(
        args.mcpcurl, args.server, CONTROL_OWNER, CONTROL_REPO, CONTROL_SHA, CONTROL_PATH
    )
    mcp_control_bytes, mcp_control_uri = extract_success_bytes(mcp_control_payload)
    if CONTROL_SHA not in mcp_control_uri:
        raise SystemExit("same-repo official MCP control URI is not bound to exact SHA")
    if rest_control_bytes != mcp_control_bytes:
        raise SystemExit("same-repo REST and official MCP control bytes differ")

    # Consume both observed FIRST REDs without hiding them. The real W56 helper uses
    # anonymous raw access to a sibling repository. The CODEX workflow token is also
    # repository-scoped and therefore cannot read that sibling through REST.
    raw_child_status, raw_child_bytes, raw_child_elapsed = anonymous_raw_fetch(
        CHILD_OWNER, CHILD_REPO, CHILD_SHA, CHILD_PATH
    )
    rest_child_status, rest_child_bytes, rest_child_elapsed = authenticated_api_fetch(
        CHILD_OWNER, CHILD_REPO, CHILD_SHA, CHILD_PATH, token
    )
    mcp_child_payload, mcp_child_wire, mcp_child_elapsed = run_official(
        args.mcpcurl, args.server, CHILD_OWNER, CHILD_REPO, CHILD_SHA, CHILD_PATH
    )
    mcp_child_not_found, mcp_child_message = classify_official_not_found(mcp_child_payload)

    # Current expected topology: all three routes are denied/not-found from CODEX.
    # If access is later widened, fail closed and demand a fresh parity decision rather
    # than silently converting credential drift into transport authority.
    if raw_child_status != 404:
        raise SystemExit(f"cross-repo anonymous raw expectation changed: HTTP {raw_child_status}")
    if rest_child_status != 404:
        raise SystemExit(f"cross-repo workflow-token REST expectation changed: HTTP {rest_child_status}")
    if not mcp_child_not_found:
        raise SystemExit("cross-repo official MCP expectation changed: no NOT_FOUND/isError classification")

    receipt = {
        "schema": "qps.m03.content_read_transport_auth_boundary.v3",
        "mission_id": "M03_GITHUB_MCP_SERVER",
        "pulse_id": "P_M03_CONTENT_READ_AUTH_BOUNDARY_01",
        "first_red_history": [
            {
                "run_id": "34625309676",
                "job_id": "103348864135",
                "error": "legacy raw transport positive read returned HTTP 404",
                "classification": "CROSS_REPO_ACCESS_BOUNDARY",
            },
            {
                "run_id": "34683452950",
                "job_id": "103526160395",
                "error": "authenticated REST candidate positive read returned HTTP 404",
                "classification": "REPOSITORY_SCOPED_ACTIONS_TOKEN_CANNOT_READ_SIBLING",
            },
        ],
        "same_repo_positive_control": {
            "repo": f"{CONTROL_OWNER}/{CONTROL_REPO}",
            "sha": CONTROL_SHA,
            "path": CONTROL_PATH,
            "rest_status": rest_control_status,
            "rest_sha256": sha256(rest_control_bytes),
            "rest_elapsed_s": round(rest_control_elapsed, 6),
            "official_mcp_sha256": sha256(mcp_control_bytes),
            "official_mcp_wire_sha256": sha256(mcp_control_wire),
            "official_mcp_elapsed_s": round(mcp_control_elapsed, 6),
            "byte_exact": rest_control_bytes == mcp_control_bytes,
            "result": "PASS",
        },
        "cross_repo_child_access": {
            "repo": f"{CHILD_OWNER}/{CHILD_REPO}",
            "sha": CHILD_SHA,
            "path": CHILD_PATH,
            "known_blob_sha1_from_child_governance": EXPECTED_CHILD_BLOB_SHA1,
            "anonymous_raw_status": raw_child_status,
            "anonymous_raw_elapsed_s": round(raw_child_elapsed, 6),
            "workflow_token_rest_status": rest_child_status,
            "workflow_token_rest_elapsed_s": round(rest_child_elapsed, 6),
            "official_mcp_not_found": mcp_child_not_found,
            "official_mcp_elapsed_s": round(mcp_child_elapsed, 6),
            "official_mcp_wire_sha256": sha256(mcp_child_wire),
            "official_mcp_message_sha256": sha256(mcp_child_message.encode("utf-8")),
            "result": "DENIED_OR_HIDDEN_BY_PARENT_CREDENTIAL_SCOPE",
        },
        "local_duplicate": {
            "repo": "GBOGEB/CODEX",
            "path": "scripts/qps_w56_verify_hash_receipt_v2.py",
            "function": "fetch_bytes",
            "current_transport": "anonymous_raw_sibling_fetch",
            "runtime_disposition": "BROKEN_UNDER_CURRENT_CROSS_REPO_AUTH_TOPOLOGY",
        },
        "pragmatic_architecture_decision": {
            "do_not": [
                "do_not_add_broad_PAT_only_to_preserve_parent_pull_fetch",
                "do_not_replace_broken_raw_with_official_MCP_using_same_insufficient_token",
                "do_not_claim_transport_parity_when_credential_scope_is_the_blocker",
            ],
            "preferred_route": "CHILD_SOURCE_OWNER_EMITS_EXACT_SHA_RECEIPT_AND_PARENT_CONSUMES_RETURNED_EVIDENCE",
            "secondary_route_if_direct_parent_read_is_operationally_required": "DEDICATED_LEAST_PRIVILEGE_CROSS_REPO_GITHUB_APP_CREDENTIAL",
            "same_repo_transport_rule": "MINIMAL_REST_FOR_TINY_DETERMINISTIC_FETCH_OFFICIAL_MCP_FOR_AGENT_ORCHESTRATION_STANDARDIZATION",
        },
        "result": "PASS_AUTH_BOUNDARY_LOCALIZED_NO_FORCED_MCP_CUTOVER",
        "cutover_authority": "NONE_MOVE_TO_CHILD_EMITTER_DESIGN",
    }
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
