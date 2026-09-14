from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from codex.contract_governance.builder import workbook_payload
from codex.contract_governance.io import content_hash, load_ssot
from receipt_validation import load_and_validate_receipt

EXECUTION_RECEIPT = HERE / "receipts" / "multiformat_execution_receipt.json"
HOSTED_RECEIPT = HERE / "receipts" / "github_pages_hosted_receipt.json"


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if value:
            self.parts.append(value)

    def text(self) -> str:
        return "\n".join(self.parts)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _semantic_tokens(payload: dict[str, Any], digest: str) -> list[str]:
    tokens = [str(payload["package_id"]), digest]
    for sheet in payload["sheets"]:
        tokens.append(str(sheet["name"]))
        for row in sheet["rows"]:
            req_id = row.get("Requirement ID")
            if req_id:
                tokens.append(str(req_id))
    return list(dict.fromkeys(tokens))


def _parity(text: str, expected_tokens: list[str]) -> dict[str, Any]:
    missing = [token for token in expected_tokens if token not in text]
    present = len(expected_tokens) - len(missing)
    return {
        "pass": not missing,
        "expected_token_count": len(expected_tokens),
        "present_token_count": present,
        "coverage": round(present / max(len(expected_tokens), 1), 6),
        "missing_tokens": missing,
    }


def _extract_text(data: bytes) -> str:
    parser = _TextExtractor()
    parser.feed(data.decode("utf-8"))
    return parser.text()


def _fetch_until_governed_match(
    url: str,
    *,
    expected_sha256: str,
    expected_tokens: list[str],
    retries: int = 24,
    delay_seconds: float = 5.0,
    required_consecutive_matches: int = 2,
) -> tuple[int, bytes, str, int, list[dict[str, Any]], dict[str, Any]]:
    last_error: Exception | None = None
    consecutive_matches = 0
    observations: list[dict[str, Any]] = []
    matched: tuple[int, bytes, str, int, dict[str, Any]] | None = None

    for attempt in range(1, retries + 1):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "ABACUS-A9-hosted-pages-proof/1.1",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
        )
        observation: dict[str, Any] = {"attempt": attempt}
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = int(getattr(response, "status", 200))
                body = response.read()
                final_url = str(response.geturl())
                hosted_sha = _sha256(body)
                parity = _parity(_extract_text(body), expected_tokens) if body else {
                    "pass": False,
                    "expected_token_count": len(expected_tokens),
                    "present_token_count": 0,
                    "coverage": 0.0,
                    "missing_tokens": expected_tokens,
                }
                hash_match = hosted_sha == expected_sha256
                governed_match = status == 200 and bool(body) and hash_match and parity["pass"]
                observation.update(
                    {
                        "http_status": status,
                        "bytes": len(body),
                        "sha256": hosted_sha,
                        "hash_match": hash_match,
                        "semantic_pass": bool(parity["pass"]),
                        "semantic_coverage": parity["coverage"],
                        "final_url": final_url,
                    }
                )
                if governed_match:
                    consecutive_matches += 1
                    matched = (status, body, final_url, attempt, parity)
                    observation["consecutive_governed_matches"] = consecutive_matches
                    observations.append(observation)
                    if consecutive_matches >= required_consecutive_matches:
                        assert matched is not None
                        return (*matched[:4], observations, matched[4])
                else:
                    consecutive_matches = 0
                    observation["consecutive_governed_matches"] = 0
                    observations.append(observation)
                    last_error = RuntimeError(
                        "hosted response has not converged to governed candidate: "
                        f"status={status} sha={hosted_sha} expected={expected_sha256} "
                        f"semantic_coverage={parity['coverage']}"
                    )
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            consecutive_matches = 0
            last_error = exc
            observation.update(
                {
                    "network_error": str(exc),
                    "consecutive_governed_matches": 0,
                }
            )
            observations.append(observation)

        if attempt < retries:
            time.sleep(delay_seconds)

    tail = observations[-5:]
    raise RuntimeError(
        "hosted Pages did not converge to the governed artifact after "
        f"{retries} attempts; last_error={last_error}; tail={json.dumps(tail, sort_keys=True)}"
    )


def execute(page_url: str | None = None) -> dict[str, Any]:
    execution = load_and_validate_receipt(EXECUTION_RECEIPT)
    source_commit = os.environ.get("ABACUS_SOURCE_SHA") or os.environ.get("GITHUB_SHA") or execution["source_commit"]
    if source_commit != execution["source_commit"]:
        raise ValueError(
            f"hosted proof source commit mismatch: execution={execution['source_commit']} env={source_commit}"
        )

    resolved_url = page_url or os.environ.get("ABACUS_PAGES_URL")
    if not resolved_url:
        raise ValueError("ABACUS_PAGES_URL is required for hosted GitHub Pages proof")

    pages_item = execution["formats"]["github_pages"]
    local_path = (HERE / pages_item["artifact_relpath"]).resolve()
    local_bytes = local_path.read_bytes()
    local_sha = _sha256(local_bytes)
    if local_sha != pages_item["artifact_sha256"]:
        raise ValueError(
            f"local Pages candidate hash mismatch: execution={pages_item['artifact_sha256']} actual={local_sha}"
        )

    ssot_path = ROOT / execution["ssot_relpath"]
    ssot = load_ssot(ssot_path)
    payload = workbook_payload(ssot, execution["render_mode"])
    canonical_digest = content_hash(payload)
    if canonical_digest != execution["canonical_content_sha256"]:
        raise ValueError("canonical content hash changed before hosted Pages proof")
    expected_tokens = _semantic_tokens(payload, canonical_digest)

    status, hosted_bytes, final_url, fetch_count, observations, parity = _fetch_until_governed_match(
        resolved_url,
        expected_sha256=local_sha,
        expected_tokens=expected_tokens,
    )
    hosted_sha = _sha256(hosted_bytes)
    hash_match = hosted_sha == local_sha == pages_item["artifact_sha256"]
    accepted = status == 200 and hash_match and parity["pass"]

    receipt = {
        "receipt_version": "A9.3-PAGES",
        "publication_id": execution["publication_id"],
        "source_commit": source_commit,
        "page_url": resolved_url,
        "fetched_url": final_url,
        "http_status": status,
        "deployment_run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "local_artifact_relpath": pages_item["artifact_relpath"],
        "local_artifact_sha256": local_sha,
        "hosted_sha256": hosted_sha,
        "hosted_bytes": len(hosted_bytes),
        "semantic_parity": parity,
        "network_fetch_count": fetch_count,
        "fetch_method": "network_get_after_actions_deploy_pages_until_governed_match",
        "required_consecutive_matches": 2,
        "propagation_observations": observations,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "accept" if accepted else "reject",
    }

    HOSTED_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    HOSTED_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    result = execute()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"] == "accept" else 1)
