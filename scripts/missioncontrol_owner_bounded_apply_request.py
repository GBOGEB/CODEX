#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

COMMAND_RE = re.compile(
    r"^/missioncontrol apply refresh-federation-heads ([0-9a-f]{40})\s*$"
)
INTENT = "REFRESH_FEDERATION_HEADS"
TARGET_REPO = "GBOGEB/CODEX"
TARGET_REF = "main"
CHANGED_PATHS = [
    "mission_control/mycelium/source_status.json",
    "docs/data/missioncontrol_source_status.json",
    "mission_control/mycelium/control_events.json",
    "docs/data/missioncontrol_control_events.json",
    "mission_control/mycelium/metrics_snapshot.json",
    "docs/data/missioncontrol_metrics.json",
]


class OwnerApplyError(ValueError):
    pass


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_command(comment: str) -> str:
    match = COMMAND_RE.fullmatch(comment.strip())
    if not match:
        raise OwnerApplyError(
            "expected '/missioncontrol apply refresh-federation-heads <40-char-main-sha>'"
        )
    return match.group(1)


def build_request(
    *,
    comment: str,
    observed_head_sha: str,
    run_id: str,
    actor: str,
    created_at: str | None = None,
) -> dict:
    requested_sha = parse_command(comment)
    if requested_sha != observed_head_sha:
        raise OwnerApplyError(
            f"stale owner command: requested={requested_sha} observed={observed_head_sha}"
        )
    payload_sha256 = sha256_text(INTENT)
    request_id = f"MC-OWNER-APPLY-{run_id}-{requested_sha[:12]}"
    return {
        "schema_version": "0.1",
        "request_id": request_id,
        "created_at": created_at or datetime.now(UTC).isoformat(),
        "requested_by_hint": actor,
        "target": {
            "repo": TARGET_REPO,
            "ref": TARGET_REF,
            "expected_head_sha": requested_sha,
        },
        "action_class": "APPLY_BOUNDED_CODEX",
        "intent": INTENT,
        "payload_sha256": payload_sha256,
        "idempotency_key": f"mc:apply:{requested_sha}:{payload_sha256}",
        "changed_paths": CHANGED_PATHS,
        "evidence_refs": [
            "https://github.com/GBOGEB/CODEX/issues/879",
            "mission_control/mycelium/execution_gateway_contract.yaml",
            "mission_control/mycelium/gateway/receipts/missioncontrol-stage-only-1e4df9cae241e539246c1338-36754862285-1.json",
            ".github/workflows/missioncontrol-owner-bounded-apply.yml",
        ],
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comment", required=True)
    parser.add_argument("--observed-head", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    request = build_request(
        comment=args.comment,
        observed_head_sha=args.observed_head,
        run_id=args.run_id,
        actor=args.actor,
    )
    args.out.write_text(
        json.dumps(request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "owner_bounded_apply_request": "PASS",
        "request_id": request["request_id"],
        "expected_head_sha": request["target"]["expected_head_sha"],
        "action_class": request["action_class"],
        "changed_paths": request["changed_paths"],
    }, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except OwnerApplyError as exc:
        raise SystemExit(f"OWNER_BOUNDED_APPLY_REJECTED: {exc}")
