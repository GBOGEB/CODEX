#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

COMMAND_RE = re.compile(
    r"^/missioncontrol stage refresh-federation-heads ([0-9a-f]{40})\s*$"
)
INTENT = "REFRESH_FEDERATION_HEADS"
TARGET_REPO = "GBOGEB/CODEX"
TARGET_REF = "main"


class OwnerCommentError(ValueError):
    pass


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_command(comment: str) -> str:
    match = COMMAND_RE.fullmatch(comment.strip())
    if not match:
        raise OwnerCommentError(
            "expected '/missioncontrol stage refresh-federation-heads <40-char-main-sha>'"
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
        raise OwnerCommentError(
            f"stale owner command: requested={requested_sha} observed={observed_head_sha}"
        )
    payload_sha256 = sha256_text(INTENT)
    request_id = f"MC-OWNER-COMMENT-{run_id}-{requested_sha[:12]}"
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
        "action_class": "STAGE_ONLY",
        "intent": INTENT,
        "payload_sha256": payload_sha256,
        "idempotency_key": f"mc:{requested_sha}:{payload_sha256}",
        "evidence_refs": [
            "https://github.com/GBOGEB/CODEX/issues/879",
            "mission_control/mycelium/execution_gateway_contract.yaml",
            ".github/workflows/missioncontrol-owner-comment-transport.yml",
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
        "owner_comment_request": "PASS",
        "request_id": request["request_id"],
        "expected_head_sha": request["target"]["expected_head_sha"],
        "mutation_enabled": False,
    }, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except OwnerCommentError as exc:
        raise SystemExit(f"OWNER_COMMENT_REJECTED: {exc}")
