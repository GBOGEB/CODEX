from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
A7 = ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime"
sys.path.insert(0, str(ROOT))

from codex.contract_governance.builder import workbook_payload
from codex.contract_governance.io import content_hash, load_ssot

SCHEMA = HERE / "receipt_schema.json"
TUPLE_LEDGER = A7 / "data" / "semantic_tuple_ledger.json"
REQUIRED_FORMATS = ("html", "pptx", "pdf", "markdown", "github_pages")
DEFAULT_EXECUTION_RECEIPT = HERE / "receipts" / "multiformat_execution_receipt.json"


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


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_path(relpath: str) -> Path:
    candidate = (HERE / relpath).resolve()
    root = HERE.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"artifact path escapes A9 boundary: {relpath}")
    return candidate


def _semantic_tokens(payload: dict[str, Any], digest: str) -> list[str]:
    tokens = [str(payload["package_id"]), digest]
    for sheet in payload["sheets"]:
        tokens.append(str(sheet["name"]))
        for row in sheet["rows"]:
            req_id = row.get("Requirement ID")
            if req_id:
                tokens.append(str(req_id))
    return list(dict.fromkeys(tokens))


def _extract_html_text(data: bytes) -> str:
    parser = _TextExtractor()
    parser.feed(data.decode("utf-8"))
    return parser.text()


def _fetch_hosted_match(
    url: str,
    *,
    expected_sha256: str,
    expected_tokens: list[str],
    retries: int = 12,
    delay_seconds: float = 5.0,
    required_consecutive_matches: int = 2,
) -> tuple[int, bytes, str, int]:
    if required_consecutive_matches < 2:
        raise ValueError("hosted Pages independent validation requires at least two consecutive matches")

    last_error: Exception | None = None
    consecutive_matches = 0
    last_match: tuple[int, bytes, str, int] | None = None
    observations: list[dict[str, Any]] = []

    for attempt in range(1, retries + 1):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "ABACUS-A9-independent-pages-validator/1.1",
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
                fetched_sha = hashlib.sha256(body).hexdigest()
                hosted_text = _extract_html_text(body) if body else ""
                missing_tokens = [token for token in expected_tokens if token not in hosted_text]
                governed_match = (
                    status == 200
                    and bool(body)
                    and fetched_sha == expected_sha256
                    and not missing_tokens
                )
                observation.update(
                    {
                        "http_status": status,
                        "bytes": len(body),
                        "sha256": fetched_sha,
                        "hash_match": fetched_sha == expected_sha256,
                        "semantic_pass": not missing_tokens,
                        "missing_token_count": len(missing_tokens),
                        "final_url": final_url,
                    }
                )
                if governed_match:
                    consecutive_matches += 1
                    last_match = (status, body, final_url, attempt)
                    observation["consecutive_governed_matches"] = consecutive_matches
                    observations.append(observation)
                    if consecutive_matches >= required_consecutive_matches:
                        assert last_match is not None
                        return last_match
                else:
                    consecutive_matches = 0
                    observation["consecutive_governed_matches"] = 0
                    observations.append(observation)
                    last_error = ValueError(
                        "hosted response has not converged to governed candidate: "
                        f"status={status} sha={fetched_sha} expected={expected_sha256} "
                        f"missing_tokens={len(missing_tokens)}"
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

    raise ValueError(
        "independent hosted Pages did not converge to the governed artifact after "
        f"{retries} attempts: last_error={last_error}; tail={json.dumps(observations[-5:], sort_keys=True)}"
    )


def load_and_validate_receipt(receipt_path: Path) -> dict[str, Any]:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(receipt), key=lambda error: list(error.path)
    )
    if errors:
        raise ValueError(
            "receipt schema validation failed: "
            + "; ".join(error.message for error in errors)
        )

    ssot_path = ROOT / receipt["ssot_relpath"]
    if not ssot_path.exists():
        raise ValueError(f"SSOT path does not exist: {ssot_path}")
    ssot = load_ssot(ssot_path)
    canonical = content_hash(workbook_payload(ssot, receipt["render_mode"]))

    expected_top = {
        "ssot_sha256": sha256_path(ssot_path),
        "canonical_content_sha256": canonical,
        "tuple_ledger_sha256": sha256_path(TUPLE_LEDGER),
    }
    top_mismatches = [
        f"{field}: receipt={receipt.get(field)} actual={actual}"
        for field, actual in expected_top.items()
        if receipt.get(field) != actual
    ]
    if top_mismatches:
        raise ValueError(
            "receipt top-level content-address validation failed: "
            + "; ".join(top_mismatches)
        )

    env_source = os.environ.get("ABACUS_SOURCE_SHA")
    if env_source and receipt.get("source_commit") != env_source:
        raise ValueError(
            f"receipt source_commit mismatch: receipt={receipt.get('source_commit')} env={env_source}"
        )

    format_errors: list[str] = []
    for name in REQUIRED_FORMATS:
        item = receipt["formats"][name]
        artifact = _artifact_path(item["artifact_relpath"])
        if not artifact.exists():
            format_errors.append(f"{name}: artifact missing at {artifact}")
            continue
        actual_sha = sha256_path(artifact)
        if item["artifact_sha256"] != actual_sha:
            format_errors.append(
                f"{name}: artifact sha mismatch receipt={item['artifact_sha256']} actual={actual_sha}"
            )
        actual_bytes = artifact.stat().st_size
        if item["artifact_bytes"] != actual_bytes:
            format_errors.append(
                f"{name}: artifact byte-size mismatch receipt={item['artifact_bytes']} actual={actual_bytes}"
            )
        telemetry = item["telemetry"]
        layout_pass = bool(telemetry.get("layout_pass"))
        overflow_pass = bool(telemetry.get("overflow_pass"))
        parity_pass = bool(item["semantic_parity"].get("pass"))
        expected_decision = (
            "accept" if layout_pass and overflow_pass and parity_pass else "reject"
        )
        if item["decision"] != expected_decision:
            format_errors.append(
                f"{name}: decision={item['decision']} expected={expected_decision}"
            )

    if format_errors:
        raise ValueError("format receipt validation failed: " + "; ".join(format_errors))

    html_sha = receipt["formats"]["html"]["artifact_sha256"]
    pages_sha = receipt["formats"]["github_pages"]["artifact_sha256"]
    parity_expected = (
        all(receipt["formats"][name]["semantic_parity"]["pass"] for name in REQUIRED_FORMATS)
        and html_sha == pages_sha
    )
    if receipt["cross_format_parity"]["pass"] != parity_expected:
        raise ValueError(
            "cross-format parity decision inconsistent with validated format evidence"
        )
    if receipt["cross_format_parity"]["canonical_content_sha256"] != canonical:
        raise ValueError("cross-format parity canonical content hash mismatch")

    expected_decision = (
        "accept"
        if all(receipt["formats"][name]["decision"] == "accept" for name in REQUIRED_FORMATS)
        and parity_expected
        and bool(receipt["semantic_replay"]["pass"])
        else "reject"
    )
    if receipt["decision"] != expected_decision:
        raise ValueError(
            f"receipt decision inconsistent with evidence: receipt={receipt['decision']} expected={expected_decision}"
        )
    return receipt


def load_and_validate_hosted_pages_receipt(
    hosted_receipt_path: Path,
    execution_receipt_path: Path = DEFAULT_EXECUTION_RECEIPT,
    *,
    refetch: bool = False,
) -> dict[str, Any]:
    execution = load_and_validate_receipt(execution_receipt_path)
    hosted = json.loads(hosted_receipt_path.read_text(encoding="utf-8"))
    required = {
        "receipt_version",
        "publication_id",
        "source_commit",
        "page_url",
        "http_status",
        "local_artifact_relpath",
        "local_artifact_sha256",
        "hosted_sha256",
        "hosted_bytes",
        "semantic_parity",
        "decision",
    }
    missing = sorted(required - set(hosted))
    if missing:
        raise ValueError(f"hosted Pages receipt missing fields: {missing}")
    if hosted["receipt_version"] != "A9.3-PAGES":
        raise ValueError(f"unexpected hosted Pages receipt version: {hosted['receipt_version']}")
    if hosted["publication_id"] != execution["publication_id"]:
        raise ValueError("hosted Pages publication_id mismatch")
    if hosted["source_commit"] != execution["source_commit"]:
        raise ValueError("hosted Pages source_commit mismatch")

    env_source = os.environ.get("ABACUS_SOURCE_SHA")
    if env_source and hosted["source_commit"] != env_source:
        raise ValueError(
            f"hosted Pages source_commit mismatch: receipt={hosted['source_commit']} env={env_source}"
        )

    pages_item = execution["formats"]["github_pages"]
    if hosted["local_artifact_relpath"] != pages_item["artifact_relpath"]:
        raise ValueError("hosted Pages local artifact path mismatch")
    local_path = _artifact_path(pages_item["artifact_relpath"])
    local_sha = sha256_path(local_path)
    if local_sha != pages_item["artifact_sha256"]:
        raise ValueError("governed Pages candidate no longer matches execution receipt")
    if hosted["local_artifact_sha256"] != local_sha:
        raise ValueError("hosted Pages local artifact hash mismatch")
    if hosted["hosted_sha256"] != local_sha:
        raise ValueError("hosted Pages bytes do not match governed deployment candidate")
    if int(hosted["http_status"]) != 200:
        raise ValueError(f"hosted Pages HTTP status is not 200: {hosted['http_status']}")
    if int(hosted["hosted_bytes"]) <= 0:
        raise ValueError("hosted Pages byte count must be positive")
    if not bool(hosted["semantic_parity"].get("pass")):
        raise ValueError("hosted Pages semantic parity did not pass")
    if float(hosted["semantic_parity"].get("coverage", 0.0)) != 1.0:
        raise ValueError("hosted Pages semantic parity coverage is not 1.0")
    if int(hosted.get("required_consecutive_matches", 0)) < 2:
        raise ValueError("hosted Pages receipt did not require stable consecutive convergence")
    if hosted["decision"] != "accept":
        raise ValueError(f"hosted Pages receipt decision is not accept: {hosted['decision']}")

    if refetch:
        ssot_path = ROOT / execution["ssot_relpath"]
        ssot = load_ssot(ssot_path)
        payload = workbook_payload(ssot, execution["render_mode"])
        canonical = content_hash(payload)
        expected_tokens = _semantic_tokens(payload, canonical)
        status, body, final_url, _ = _fetch_hosted_match(
            str(hosted["page_url"]),
            expected_sha256=local_sha,
            expected_tokens=expected_tokens,
        )
        if status != 200:
            raise ValueError(f"independent hosted Pages HTTP status is not 200: {status}")
        if hashlib.sha256(body).hexdigest() != local_sha:
            raise ValueError("independent hosted Pages hash mismatch")
        missing_tokens = [token for token in expected_tokens if token not in _extract_html_text(body)]
        if missing_tokens:
            raise ValueError(
                "independent hosted Pages semantic parity failed: missing=" + ", ".join(missing_tokens)
            )
        if hosted.get("fetched_url") and str(hosted["fetched_url"]) != final_url:
            raise ValueError(
                f"independent hosted Pages final URL changed: receipt={hosted['fetched_url']} actual={final_url}"
            )
    return hosted


if __name__ == "__main__":
    receipt_path = DEFAULT_EXECUTION_RECEIPT
    validated = load_and_validate_receipt(receipt_path)
    print(
        json.dumps(
            {
                "status": "PASS",
                "decision": validated["decision"],
                "formats": list(validated["formats"]),
                "cross_format_parity": validated["cross_format_parity"]["pass"],
            },
            indent=2,
        )
    )
