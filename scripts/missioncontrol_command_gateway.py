#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_STATUS = ROOT / "mission_control" / "mycelium" / "source_status.json"
PAGES_SOURCE_STATUS = ROOT / "docs" / "data" / "missioncontrol_source_status.json"
RECEIPT_DIR = ROOT / "mission_control" / "mycelium" / "gateway" / "receipts"
ALLOWED_ACTIONS = {"REFRESH_FEDERATION_HEADS"}
ALLOWED_LANES = {"CODEX_UI", "FEDERATION"}
TARGET_REPOSITORY = "GBOGEB/CODEX"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class GatewayError(ValueError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_envelope(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GatewayError(f"invalid envelope JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise GatewayError("envelope must be a JSON object")
    return payload


def validate_envelope(envelope: dict[str, Any], *, expected_sha: str, actor: str) -> str:
    if not actor.strip():
        raise GatewayError("authenticated actor is required")
    if envelope.get("schema_version") != "0.2.1":
        raise GatewayError("schema_version must be 0.2.1")
    if envelope.get("event_type") != "USER_STEER":
        raise GatewayError("event_type must be USER_STEER")
    if envelope.get("requested_mode") != "APPLY":
        raise GatewayError("requested_mode must be APPLY")
    if envelope.get("effective_mode") not in {
        "STAGED_APPLY_WITHHELD_NO_AUTHENTICATED_GATEWAY",
        "AUTHENTICATED_APPLY_REQUEST",
    }:
        raise GatewayError("effective_mode is not accepted by gateway")
    if envelope.get("repository") != TARGET_REPOSITORY:
        raise GatewayError("gateway target repository must be GBOGEB/CODEX")
    if envelope.get("lane") not in ALLOWED_LANES:
        raise GatewayError("lane is not allow-listed")
    source_sha = str(envelope.get("source_authority_sha") or "")
    if not SHA_RE.fullmatch(source_sha):
        raise GatewayError("source_authority_sha must be a 40-character lowercase SHA")
    if source_sha != expected_sha:
        raise GatewayError(
            f"stale source authority: envelope={source_sha} expected={expected_sha}"
        )
    invariants = envelope.get("invariants")
    if not isinstance(invariants, dict):
        raise GatewayError("invariants object is required")
    expected_invariants = {
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
        "replay_completed_atoms": False,
    }
    for key, expected in expected_invariants.items():
        if invariants.get(key) != expected:
            raise GatewayError(f"invariant violation: {key} must be {expected!r}")
    command = envelope.get("command")
    if not isinstance(command, dict):
        raise GatewayError("command must be a JSON object for authenticated execution")
    action = command.get("action")
    if action not in ALLOWED_ACTIONS:
        raise GatewayError(f"action is not allow-listed: {action!r}")
    return str(action)


def github_json(path: str, token: str) -> Any:
    if not token:
        raise GatewayError("GITHUB_TOKEN is required for authenticated execution")
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "MissionControl-Authenticated-Gateway",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def refresh_federation_heads(*, token: str, observed_at: str) -> list[str]:
    payload = json.loads(SOURCE_STATUS.read_text(encoding="utf-8"))
    for row in payload.get("sources", []):
        repo = row.get("repository")
        if not repo:
            continue
        meta = github_json(f"/repos/{repo}", token)
        branch = meta.get("default_branch") or "main"
        commit = github_json(f"/repos/{repo}/commits/{branch}", token)
        row["status"] = "AUTHENTICATED_GATEWAY"
        row["observed_at"] = observed_at
        row["head_sha"] = commit["sha"]
        row["default_branch"] = branch
        row["measurement_basis"] = "GitHub Actions authenticated gateway repository-head refresh"
        if row.get("role") == "ENGINEERING_TRUTH_QPS":
            row["authority_preserved"] = True
            row["engineering_truth_promoted"] = False
    payload["generated_at"] = observed_at
    payload["authority_transfer"] = False
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    SOURCE_STATUS.write_text(text, encoding="utf-8")
    PAGES_SOURCE_STATUS.parent.mkdir(parents=True, exist_ok=True)
    PAGES_SOURCE_STATUS.write_text(text, encoding="utf-8")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_missioncontrol_metrics.py")],
        cwd=ROOT,
        check=True,
    )
    return [
        "mission_control/mycelium/source_status.json",
        "docs/data/missioncontrol_source_status.json",
        "mission_control/mycelium/metrics_snapshot.json",
        "docs/data/missioncontrol_metrics.json",
    ]


def write_receipt(
    *,
    envelope: dict[str, Any],
    action: str,
    actor: str,
    actor_id: str,
    run_id: str,
    run_attempt: str,
    expected_sha: str,
    execute: bool,
    changed_paths: list[str],
) -> Path:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{run_id}-{run_attempt}.json"
    path = RECEIPT_DIR / name
    receipt = {
        "schema_version": "0.1",
        "gateway_version": "0.1.0",
        "generated_at": now_iso(),
        "actor": actor,
        "actor_id": actor_id,
        "run_id": run_id,
        "run_attempt": run_attempt,
        "source_authority_sha": expected_sha,
        "envelope_sha256": sha256_text(canonical_json(envelope)),
        "action": action,
        "status": "AUTHENTICATED_EXECUTED_TO_PR_STAGE" if execute else "AUTHENTICATED_DRY_RUN_VALIDATED",
        "mutation_mode": "AUTOMATION_BRANCH_PR_ONLY",
        "changed_paths": changed_paths,
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
        "remote_truth_auto_promotable": False,
    }
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--actor-id", default="")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", default="1")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    envelope = load_envelope(args.envelope)
    action = validate_envelope(envelope, expected_sha=args.expected_sha, actor=args.actor)
    changed: list[str] = []
    if args.execute:
        if action == "REFRESH_FEDERATION_HEADS":
            changed = refresh_federation_heads(
                token=os.environ.get("GITHUB_TOKEN", ""),
                observed_at=now_iso(),
            )
        else:
            raise GatewayError(f"no executor implemented for action {action}")
    receipt = write_receipt(
        envelope=envelope,
        action=action,
        actor=args.actor,
        actor_id=args.actor_id,
        run_id=args.run_id,
        run_attempt=args.run_attempt,
        expected_sha=args.expected_sha,
        execute=args.execute,
        changed_paths=changed,
    )
    rel_receipt = receipt.relative_to(ROOT).as_posix()
    print(json.dumps({
        "gateway": "PASS",
        "action": action,
        "execute": args.execute,
        "receipt": rel_receipt,
        "changed_paths": changed,
    }, sort_keys=True))
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"action={action}\n")
            handle.write(f"receipt_path={rel_receipt}\n")
            handle.write(f"execute={'true' if args.execute else 'false'}\n")


if __name__ == "__main__":
    try:
        main()
    except GatewayError as exc:
        print(f"GATEWAY_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(2)
