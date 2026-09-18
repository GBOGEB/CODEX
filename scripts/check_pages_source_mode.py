from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REQUIRED_BUILD_TYPE = "workflow"
DEFAULT_API_VERSION = "2022-11-28"
DEFAULT_RECEIPT_PATH = (
    "abacus_render_pipeline/A9_multiformat_publication/receipts/"
    "pages_source_mode_receipt.json"
)
OWNER_ACTION = "Settings -> Pages -> Build and deployment -> Source: GitHub Actions"
REENTRY = (
    "rerun unchanged A9 exact-main proof only after build_type reports 'workflow'"
)


def inspect_pages_site(payload: Any) -> list[str]:
    """Return fail-closed diagnostics for a GitHub Pages site payload."""
    if not isinstance(payload, dict):
        return ["Pages site response is not a JSON object"]

    build_type = payload.get("build_type")
    source = payload.get("source")
    source_branch = source.get("branch") if isinstance(source, dict) else None
    source_path = source.get("path") if isinstance(source, dict) else None

    if build_type == REQUIRED_BUILD_TYPE:
        return []

    source_text = (
        f" source={source_branch or '<unknown>'}:{source_path or '<unknown>'}"
        if isinstance(source, dict)
        else " source=<none>"
    )
    return [
        f"GitHub Pages build_type={build_type!r}; required={REQUIRED_BUILD_TYPE!r}."
        f"{source_text}. A branch/Jekyll publisher can race the governed A9 deployment."
    ]


def build_receipt(
    repository: str,
    payload: Any,
    errors: list[str],
) -> dict[str, Any]:
    """Build a lossless machine-readable receipt for federation/TRIAGE consumption."""
    source = payload.get("source") if isinstance(payload, dict) else None
    return {
        "schema_version": "qps-pages-source-mode-receipt/1.0",
        "repository": repository,
        "source_sha": os.environ.get("GITHUB_SHA"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "required_build_type": REQUIRED_BUILD_TYPE,
        "observed_build_type": payload.get("build_type") if isinstance(payload, dict) else None,
        "observed_source_branch": source.get("branch") if isinstance(source, dict) else None,
        "observed_source_path": source.get("path") if isinstance(source, dict) else None,
        "status": "PASS" if not errors else "FAIL",
        "diagnostics": errors,
        "owner_action_required": bool(errors),
        "owner_action": OWNER_ACTION if errors else None,
        "reentry": REENTRY if errors else None,
        "formal_credit_delta": 0,
        "authority_transfer": False,
    }


def write_receipt(receipt: dict[str, Any], path: str | Path) -> Path:
    receipt_path = Path(path)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt_path


def fetch_pages_site(repository: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repository}/pages"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": DEFAULT_API_VERSION,
        "User-Agent": "CODEX-A9-Pages-Source-Mode-Audit/1.1",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub Pages site API returned HTTP {exc.code}: {detail[:500]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub Pages site API request failed: {exc}") from exc

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GitHub Pages site API returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("GitHub Pages site API returned a non-object JSON payload")
    return payload


def audit(repository: str | None = None, payload: Any | None = None) -> list[str]:
    repository = repository or os.environ.get("GITHUB_REPOSITORY")
    if payload is None:
        if not repository:
            return ["GITHUB_REPOSITORY is missing; cannot prove GitHub Pages source mode"]
        try:
            payload = fetch_pages_site(repository)
        except RuntimeError as exc:
            return [str(exc)]
    return inspect_pages_site(payload)


def main() -> int:
    repository = os.environ.get("GITHUB_REPOSITORY", "<unset>")
    payload: Any = None
    if repository == "<unset>":
        errors = ["GITHUB_REPOSITORY is missing; cannot prove GitHub Pages source mode"]
    else:
        try:
            payload = fetch_pages_site(repository)
            errors = inspect_pages_site(payload)
        except RuntimeError as exc:
            errors = [str(exc)]

    receipt = build_receipt(repository, payload, errors)
    receipt_path = write_receipt(
        receipt,
        os.environ.get("PAGES_SOURCE_MODE_RECEIPT", DEFAULT_RECEIPT_PATH),
    )

    if errors:
        print("PAGES SOURCE MODE AUDIT FAILED")
        print(f"repository={repository}")
        for error in errors:
            print(f"- {error}")
        print(f"receipt={receipt_path}")
        print(f"owner_action={OWNER_ACTION}")
        print(f"reentry={REENTRY}")
        return 1

    print("PAGES SOURCE MODE AUDIT PASSED")
    print(f"repository={repository}")
    print(f"required_build_type={REQUIRED_BUILD_TYPE}")
    print(f"receipt={receipt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
