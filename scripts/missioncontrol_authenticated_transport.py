#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
MC = ROOT / "mission_control" / "mycelium"
REQUEST_SCHEMA = MC / "schemas" / "execution_request.schema.json"
RECEIPT_SCHEMA = MC / "schemas" / "execution_receipt.schema.json"
RECEIPT_DIR = MC / "gateway" / "receipts"
REX_LEDGER = ROOT / "federation" / "rex" / "GLOBAL_REX_LEDGER_v1.yaml"

TARGET_REPOSITORY = "GBOGEB/CODEX"
TARGET_REF = "main"
ALLOWED_INTENTS = {"REFRESH_FEDERATION_HEADS"}
POLICY_ID = "MISSIONCONTROL_AUTHENTICATED_STAGE_ONLY_V0_1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class GatewayError(ValueError):
    pass


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GatewayError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GatewayError(f"JSON object required at {path}")
    return value


def validate_schema(payload: dict[str, Any], schema_path: Path) -> None:
    schema = load_json(schema_path)
    try:
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(payload)
    except ValidationError as exc:
        where = ".".join(str(x) for x in exc.absolute_path) or "<root>"
        raise GatewayError(f"schema validation failed at {where}: {exc.message}") from exc


def expected_idempotency_key(expected_sha: str, payload_sha256: str) -> str:
    return f"mc:{expected_sha}:{payload_sha256}"


def artifact_name(idempotency_key: str) -> str:
    return f"missioncontrol-stage-only-{sha256_text(idempotency_key)[:24]}"


def github_get(path: str, token: str) -> Any:
    if not token:
        raise GatewayError("GITHUB_TOKEN is required for authenticated transport")
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "MissionControl-Authenticated-Transport",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read())
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise GatewayError(f"GitHub API read failed for {path}: {exc}") from exc


def observe_target_head(token: str) -> str:
    payload = github_get(f"/repos/{TARGET_REPOSITORY}/commits/{TARGET_REF}", token)
    sha = str(payload.get("sha") or "")
    if not SHA_RE.fullmatch(sha):
        raise GatewayError("live target head is not a valid 40-character SHA")
    return sha


def validate_request(
    request: dict[str, Any],
    *,
    expected_sha: str,
    actor: str,
) -> str:
    validate_schema(request, REQUEST_SCHEMA)

    if not actor.strip():
        raise GatewayError("authenticated actor is required")
    if not SHA_RE.fullmatch(expected_sha):
        raise GatewayError("expected SHA must be a 40-character lowercase SHA")

    target = request["target"]
    if target["repo"] != TARGET_REPOSITORY:
        raise GatewayError("authenticated transport is CODEX-only")
    if target["ref"] != TARGET_REF:
        raise GatewayError("authenticated transport requires ref=main")
    if target["expected_head_sha"] != expected_sha:
        raise GatewayError(
            f"stale target head: request={target['expected_head_sha']} observed={expected_sha}"
        )

    if request["action_class"] != "STAGE_ONLY":
        raise GatewayError("transport v0.1 accepts STAGE_ONLY requests only")

    intent = request["intent"]
    if intent not in ALLOWED_INTENTS:
        raise GatewayError(f"intent is not allow-listed: {intent!r}")

    expected_payload = sha256_text(intent)
    if request["payload_sha256"] != expected_payload:
        raise GatewayError("payload_sha256 must equal SHA-256(intent) in transport v0.1")

    expected_key = expected_idempotency_key(expected_sha, expected_payload)
    if request["idempotency_key"] != expected_key:
        raise GatewayError("idempotency_key does not bind exact head and payload digest")

    if request.get("changed_paths"):
        raise GatewayError("STAGE_ONLY request may not declare changed paths")

    return intent


def assert_not_replayed(idempotency_key: str, token: str) -> str:
    name = artifact_name(idempotency_key)
    query = urllib.parse.urlencode({"name": name, "per_page": 100})
    payload = github_get(f"/repos/{TARGET_REPOSITORY}/actions/artifacts?{query}", token)
    if int(payload.get("total_count", 0)) > 0:
        raise GatewayError("completed idempotency key replay is forbidden")
    return name


def resolve_job_id(*, run_id: int, job_name: str, token: str) -> int:
    payload = github_get(
        f"/repos/{TARGET_REPOSITORY}/actions/runs/{run_id}/jobs?filter=latest&per_page=100",
        token,
    )
    matches = [row for row in payload.get("jobs", []) if row.get("name") == job_name]
    if len(matches) != 1:
        raise GatewayError(f"unable to bind unique workflow job named {job_name!r}")
    return int(matches[0]["id"])



def ambient_rex_lookup(*, intent: str, repository: str = TARGET_REPOSITORY) -> dict[str, Any]:
    """Return bounded pre-execution REX context without granting repair authority."""
    ledger = yaml.safe_load(REX_LEDGER.read_text(encoding="utf-8")) or {}
    records = [row for row in ledger.get("records", []) if isinstance(row, dict)]
    intent_tokens = {token.lower() for token in re.split(r"[^A-Za-z0-9]+", intent) if len(token) >= 4}
    exact: list[str] = []
    similar: list[str] = []
    family_hits: list[str] = []
    for row in records:
        rex_id = str(row.get("rex_id") or "")
        signature = str(row.get("signature") or "").lower()
        text = canonical_json(row).lower()
        repos = canonical_json(row.get("repo", {})).lower()
        if intent.lower() == signature:
            exact.append(rex_id)
        elif intent_tokens and any(token in text for token in intent_tokens):
            similar.append(rex_id)
        if repository.lower() in repos:
            family_hits.append(rex_id)
    return {
        "mode": "AMBIENT_PRE_EXECUTION",
        "intent": intent,
        "exact_signature_hits": sorted(set(filter(None, exact))),
        "similar_signature_hits": sorted(set(filter(None, similar))),
        "same_repo_family_hits": sorted(set(filter(None, family_hits))),
        "authority": "EVIDENCE_ONLY",
    }


def write_rex_event(
    *,
    artifact: str,
    run_id: int,
    run_attempt: int,
    request: dict[str, Any],
    lookup: dict[str, Any],
    outcome: str,
    proof_ref: str,
) -> Path:
    """Persist an event-scoped REX observation beside the execution receipt."""
    event = {
        "state": "OBSERVED_PENDING_VERIFICATION",
        "event": "TASK_EXECUTED",
        "repo": TARGET_REPOSITORY,
        "intent": request["intent"],
        "signature": f"MISSIONCONTROL.TRANSPORT.{request['intent']}",
        "lookup": lookup,
        "outcome": outcome,
        "proof_ref": proof_ref,
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
    }
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPT_DIR / f"{artifact}-{run_id}-{run_attempt}-rex.json"
    path.write_text(json.dumps(event, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_receipt(
    *,
    request: dict[str, Any],
    actor: str,
    actor_id: str,
    observed_sha: str,
    run_id: int,
    job_id: int,
) -> dict[str, Any]:
    receipt = {
        "schema_version": "0.1",
        "request_id": request["request_id"],
        "decision": "EXECUTED",
        "authenticated_principal": f"github:{actor}#{actor_id or 'unknown'}",
        "authorization_policy": POLICY_ID,
        "observed_head_sha": observed_sha,
        "after_sha": None,
        "request_sha256": sha256_text(canonical_json(request)),
        "workflow_run": run_id,
        "workflow_job": job_id,
        "result_summary": (
            "Authenticated STAGE_ONLY request executed as a no-mutation validation. "
            "APPLY_BOUNDED_CODEX remains disabled."
        ),
        "evidence_refs": sorted(
            set(
                list(request.get("evidence_refs", []))
                + [
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--actor-id", default="")
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--run-attempt", type=int, default=1)
    parser.add_argument("--job-name", required=True)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    request = load_json(args.request)
    observed_sha = observe_target_head(token)
    intent = validate_request(
        request,
        expected_sha=observed_sha,
        actor=args.actor,
    )
    rex_lookup = ambient_rex_lookup(intent=intent)
    artifact = assert_not_replayed(request["idempotency_key"], token)
    job_id = resolve_job_id(
        run_id=args.run_id,
        job_name=args.job_name,
        token=token,
    )
    receipt = build_receipt(
        request=request,
        actor=args.actor,
        actor_id=args.actor_id,
        observed_sha=observed_sha,
        run_id=args.run_id,
        job_id=job_id,
    )
    path = write_receipt(
        receipt,
        artifact=artifact,
        run_id=args.run_id,
        run_attempt=args.run_attempt,
    )
    rel = path.relative_to(ROOT).as_posix()
    rex_path = write_rex_event(
        artifact=artifact,
        run_id=args.run_id,
        run_attempt=args.run_attempt,
        request=request,
        lookup=rex_lookup,
        outcome=receipt["decision"],
        proof_ref=rel,
    )
    rex_rel = rex_path.relative_to(ROOT).as_posix()

    print(
        json.dumps(
            {
                "gateway_transport": "PASS",
                "intent": intent,
                "decision": receipt["decision"],
                "mutation_enabled": False,
                "artifact_name": artifact,
                "receipt": rel,
                "observed_head_sha": observed_sha,
                "workflow_job": job_id,
                "rex_lookup_hits": len(rex_lookup["exact_signature_hits"]) + len(rex_lookup["similar_signature_hits"]),
                "rex_event": rex_rel,
            },
            sort_keys=True,
        )
    )

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"receipt_path={rel}\n")
            handle.write(f"rex_event_path={rex_rel}\n")
            handle.write("artifact_paths<<EOF\n")
            handle.write(f"{rel}\n{rex_rel}\nEOF\n")
            handle.write(f"intent={intent}\n")
            handle.write(f"artifact_name={artifact}\n")
            handle.write(f"observed_head_sha={observed_sha}\n")
            handle.write(f"workflow_job={job_id}\n")


if __name__ == "__main__":
    try:
        main()
    except GatewayError as exc:
        print(f"GATEWAY_TRANSPORT_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(2)
