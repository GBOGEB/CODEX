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


def _fetch(url: str, retries: int = 12, delay_seconds: float = 5.0) -> tuple[int, bytes, str, int]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "ABACUS-A9-hosted-pages-proof/1.0",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = int(getattr(response, "status", 200))
                body = response.read()
                final_url = str(response.geturl())
                if status == 200 and body:
                    return status, body, final_url, attempt
                last_error = RuntimeError(f"unexpected hosted response status={status} bytes={len(body)}")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
        if attempt < retries:
            time.sleep(delay_seconds)
    raise RuntimeError(f"hosted Pages fetch failed after {retries} attempts: {last_error}")


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

    status, hosted_bytes, final_url, fetch_count = _fetch(resolved_url)
    hosted_sha = _sha256(hosted_bytes)

    ssot_path = ROOT / execution["ssot_relpath"]
    ssot = load_ssot(ssot_path)
    payload = workbook_payload(ssot, execution["render_mode"])
    canonical_digest = content_hash(payload)
    if canonical_digest != execution["canonical_content_sha256"]:
        raise ValueError("canonical content hash changed before hosted Pages proof")

    parser = _TextExtractor()
    parser.feed(hosted_bytes.decode("utf-8"))
    parity = _parity(parser.text(), _semantic_tokens(payload, canonical_digest))
    hash_match = hosted_sha == local_sha == pages_item["artifact_sha256"]
    accepted = status == 200 and hash_match and parity["pass"]

    receipt = {
        "receipt_version": "A9.1-PAGES",
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
        "fetch_method": "network_get_after_actions_deploy_pages",
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
