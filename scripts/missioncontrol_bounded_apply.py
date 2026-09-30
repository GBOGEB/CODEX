#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from scripts.ingest_missioncontrol_sources import temporal_refresh_events
from scripts.missioncontrol_authenticated_transport import (
    GatewayError,
    TARGET_REF,
    TARGET_REPOSITORY,
    canonical_json,
    github_get,
    load_json,
    observe_target_head,
    resolve_job_id,
    sha256_text,
    validate_schema,
)

ROOT = Path(__file__).resolve().parents[1]
MC = ROOT / "mission_control" / "mycelium"
DOCS_DATA = ROOT / "docs" / "data"
REQUEST_SCHEMA = MC / "schemas" / "execution_request.schema.json"
RECEIPT_SCHEMA = MC / "schemas" / "execution_receipt.schema.json"
SOURCE_REGISTRY = MC / "source_registry.yaml"
SOURCE_STATUS = MC / "source_status.json"
PAGES_SOURCE_STATUS = DOCS_DATA / "missioncontrol_source_status.json"
CONTROL_EVENTS = MC / "control_events.json"
PAGES_CONTROL_EVENTS = DOCS_DATA / "missioncontrol_control_events.json"
RUNTIME_PROOF = (
    MC
    / "gateway"
    / "receipts"
    / "missioncontrol-stage-only-1e4df9cae241e539246c1338-36754862285-1.json"
)
RECEIPT_DIR = MC / "gateway" / "receipts"

INTENT = "REFRESH_FEDERATION_HEADS"
POLICY_ID = "MISSIONCONTROL_BOUNDED_CODEX_APPLY_V0_1"
ALLOWED_CHANGED_PATHS = {
    "mission_control/mycelium/source_status.json",
    "docs/data/missioncontrol_source_status.json",
    "mission_control/mycelium/control_events.json",
    "docs/data/missioncontrol_control_events.json",
    "mission_control/mycelium/metrics_snapshot.json",
    "docs/data/missioncontrol_metrics.json",
}


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def expected_idempotency_key(expected_sha: str, payload_sha256: str) -> str:
    return f"mc:apply:{expected_sha}:{payload_sha256}"


def artifact_name(idempotency_key: str) -> str:
    return f"missioncontrol-bounded-apply-{sha256_text(idempotency_key)[:24]}"


def validate_apply_request(
    request: dict[str, Any],
    *,
    expected_sha: str,
    actor: str,
) -> str:
    validate_schema(request, REQUEST_SCHEMA)
    if not actor.strip():
        raise GatewayError("authenticated owner actor is required")

    target = request["target"]
    if target["repo"] != TARGET_REPOSITORY:
        raise GatewayError("bounded apply is CODEX-only")
    if target["ref"] != TARGET_REF:
        raise GatewayError("bounded apply requires ref=main")
    if target["expected_head_sha"] != expected_sha:
        raise GatewayError(
            f"stale target head: request={target['expected_head_sha']} observed={expected_sha}"
        )
    if request["action_class"] != "APPLY_BOUNDED_CODEX":
        raise GatewayError("bounded apply requires action_class=APPLY_BOUNDED_CODEX")
    if request["intent"] != INTENT:
        raise GatewayError(f"intent is not allow-listed: {request['intent']!r}")

    expected_payload = sha256_text(INTENT)
    if request["payload_sha256"] != expected_payload:
        raise GatewayError("payload_sha256 must equal SHA-256(intent)")
    if request["idempotency_key"] != expected_idempotency_key(
        expected_sha, expected_payload
    ):
        raise GatewayError("idempotency_key does not bind apply class, exact head and payload")

    declared = request.get("changed_paths")
    if not isinstance(declared, list) or set(declared) != ALLOWED_CHANGED_PATHS:
        raise GatewayError("changed_paths must equal the bounded CODEX freshness allow-list")

    if not RUNTIME_PROOF.exists():
        raise GatewayError("required owner-authenticated STAGE_ONLY proof is not bound")
    runtime = load_json(RUNTIME_PROOF)
    if (
        runtime.get("decision") != "EXECUTED"
        or runtime.get("after_sha") is not None
        or runtime.get("authority_transfer") is not False
        or runtime.get("formal_credit_delta") != 0
        or runtime.get("engineering_credit_delta") != 0
    ):
        raise GatewayError("bound STAGE_ONLY runtime proof is not admissible")

    return INTENT


def assert_not_replayed(idempotency_key: str, token: str) -> str:
    name = artifact_name(idempotency_key)
    from urllib.parse import urlencode

    payload = github_get(
        f"/repos/{TARGET_REPOSITORY}/actions/artifacts?{urlencode({'name': name, 'per_page': 100})}",
        token,
    )
    if int(payload.get("total_count", 0)) > 0:
        raise GatewayError("completed bounded-apply idempotency key replay is forbidden")
    return name


def refresh_federation_identities(*, token: str, run_id: int) -> list[str]:
    registry = yaml.safe_load(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    previous = load_json(SOURCE_STATUS)
    current = json.loads(json.dumps(previous))
    observed_at = now_iso()
    current["generated_at"] = observed_at
    current["public_metadata_only"] = True
    current["authority_transfer"] = False
    current["engineering_state_promoted"] = False

    by_id = {
        str(row.get("id")): row
        for row in current.get("sources", [])
        if isinstance(row, dict) and row.get("id")
    }

    for source in registry.get("sources", []):
        sid = str(source["id"])
        repo = str(source["repository"])
        row = by_id.get(sid)
        if row is None:
            raise GatewayError(f"declared source missing from governed status: {sid}")

        repo_meta = github_get(f"/repos/{repo}", token)
        default_branch = str(repo_meta.get("default_branch") or "main")
        head = github_get(f"/repos/{repo}/commits/{default_branch}", token)
        head_sha = str(head.get("sha") or "")
        if len(head_sha) != 40:
            raise GatewayError(f"invalid refreshed head for {repo}: {head_sha!r}")

        prior_status = str(row.get("status") or "")
        row["status"] = (
            prior_status
            if prior_status in {"MEASURED_CHAT_CONNECTOR", "FRESH"}
            else "FRESH"
        )
        row["observed_at"] = observed_at
        row["default_branch"] = default_branch
        row["head_ref"] = default_branch
        row["head_sha"] = head_sha
        row["identity_status"] = "MEASURED"
        row["head_url"] = head.get("html_url") or f"https://github.com/{repo}/commit/{head_sha}"
        row["pushed_at"] = repo_meta.get("pushed_at")
        row["open_issue_count"] = repo_meta.get("open_issues_count")
        row["live_metadata_refresh"] = "AUTHENTICATED_BOUNDED_APPLY_V0_1"
        row["live_metadata_run"] = run_id

    text = json.dumps(current, indent=2, sort_keys=True) + "\n"
    SOURCE_STATUS.write_text(text, encoding="utf-8")
    PAGES_SOURCE_STATUS.write_text(text, encoding="utf-8")

    events = load_json(CONTROL_EVENTS)
    updated_events = temporal_refresh_events(previous, current, events)
    event_text = json.dumps(updated_events, indent=2) + "\n"
    CONTROL_EVENTS.write_text(event_text, encoding="utf-8")
    PAGES_CONTROL_EVENTS.write_text(event_text, encoding="utf-8")

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_missioncontrol_metrics.py")],
        cwd=ROOT,
        check=True,
    )

    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    changed = [line for line in result.stdout.splitlines() if line.strip()]
    unexpected = sorted(set(changed) - ALLOWED_CHANGED_PATHS)
    if unexpected:
        raise GatewayError(f"bounded apply changed non-allowlisted paths: {unexpected}")
    if not changed:
        raise GatewayError("bounded apply produced no reviewable change")
    return changed


def build_receipt(
    *,
    request: dict[str, Any],
    actor: str,
    actor_id: str,
    observed_sha: str,
    after_sha: str,
    run_id: int,
    job_id: int,
    pr_url: str,
) -> dict[str, Any]:
    receipt = {
        "schema_version": "0.1",
        "request_id": request["request_id"],
        "decision": "EXECUTED",
        "authenticated_principal": f"github:{actor}#{actor_id or 'unknown'}",
        "authorization_policy": POLICY_ID,
        "observed_head_sha": observed_sha,
        "after_sha": after_sha,
        "request_sha256": sha256_text(canonical_json(request)),
        "workflow_run": run_id,
        "workflow_job": job_id,
        "result_summary": (
            "Authenticated bounded CODEX-only freshness apply committed to an "
            "automation branch and published for pull-request review; main was not written directly."
        ),
        "evidence_refs": sorted(
            set(
                list(request.get("evidence_refs", []))
                + [
                    pr_url,
                    "mission_control/mycelium/execution_gateway_contract.yaml",
                    "mission_control/mycelium/schemas/execution_request.schema.json",
                    "mission_control/mycelium/schemas/execution_receipt.schema.json",
                ]
            )
        ),
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
    }
    validate_schema(receipt, RECEIPT_SCHEMA)
    return receipt


def write_receipt(
    receipt: dict[str, Any],
    *,
    artifact: str,
    run_id: int,
    run_attempt: int,
) -> Path:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPT_DIR / f"{artifact}-{run_id}-{run_attempt}.json"
    path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def command_apply(args: argparse.Namespace) -> None:
    token = os.environ.get("GITHUB_TOKEN", "")
    request = load_json(args.request)
    observed_sha = observe_target_head(token)
    intent = validate_apply_request(
        request,
        expected_sha=observed_sha,
        actor=args.actor,
    )
    artifact = assert_not_replayed(request["idempotency_key"], token)
    changed = refresh_federation_identities(token=token, run_id=args.run_id)

    print(json.dumps({
        "bounded_apply": "PASS",
        "intent": intent,
        "observed_head_sha": observed_sha,
        "artifact_name": artifact,
        "changed_paths": changed,
        "mutation_scope": "AUTOMATION_BRANCH_PR_ONLY",
    }, sort_keys=True))

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"artifact_name={artifact}\n")
            handle.write(f"observed_head_sha={observed_sha}\n")
            handle.write("changed_paths=" + json.dumps(changed, separators=(',', ':')) + "\n")


def command_receipt(args: argparse.Namespace) -> None:
    token = os.environ.get("GITHUB_TOKEN", "")
    request = load_json(args.request)
    observed_sha = str(request["target"]["expected_head_sha"])
    job_id = resolve_job_id(
        run_id=args.run_id,
        job_name=args.job_name,
        token=token,
    )
    artifact = artifact_name(request["idempotency_key"])
    receipt = build_receipt(
        request=request,
        actor=args.actor,
        actor_id=args.actor_id,
        observed_sha=observed_sha,
        after_sha=args.after_sha,
        run_id=args.run_id,
        job_id=job_id,
        pr_url=args.pr_url,
    )
    path = write_receipt(
        receipt,
        artifact=artifact,
        run_id=args.run_id,
        run_attempt=args.run_attempt,
    )
    rel = path.relative_to(ROOT).as_posix()
    print(json.dumps({
        "bounded_apply_receipt": "PASS",
        "receipt": rel,
        "after_sha": args.after_sha,
        "workflow_job": job_id,
    }, sort_keys=True))
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"receipt_path={rel}\n")
            handle.write(f"workflow_job={job_id}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument("--request", type=Path, required=True)
    apply_parser.add_argument("--actor", required=True)
    apply_parser.add_argument("--run-id", type=int, required=True)
    apply_parser.set_defaults(func=command_apply)

    receipt_parser = sub.add_parser("receipt")
    receipt_parser.add_argument("--request", type=Path, required=True)
    receipt_parser.add_argument("--actor", required=True)
    receipt_parser.add_argument("--actor-id", default="")
    receipt_parser.add_argument("--run-id", type=int, required=True)
    receipt_parser.add_argument("--run-attempt", type=int, default=1)
    receipt_parser.add_argument("--job-name", required=True)
    receipt_parser.add_argument("--after-sha", required=True)
    receipt_parser.add_argument("--pr-url", required=True)
    receipt_parser.set_defaults(func=command_receipt)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except GatewayError as exc:
        print(f"BOUNDED_APPLY_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(2)
