from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

REQUIRED_BUILD_TYPE = "workflow"
DEFAULT_API_VERSION = "2022-11-28"


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


def fetch_pages_site(repository: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repository}/pages"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": DEFAULT_API_VERSION,
        "User-Agent": "CODEX-A9-Pages-Source-Mode-Audit/1.0",
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
    errors = audit(repository=repository if repository != "<unset>" else None)
    if errors:
        print("PAGES SOURCE MODE AUDIT FAILED")
        print(f"repository={repository}")
        for error in errors:
            print(f"- {error}")
        print(
            "owner_action=Settings -> Pages -> Build and deployment -> Source: GitHub Actions"
        )
        print(
            "reentry=rerun unchanged A9 exact-main proof only after build_type reports 'workflow'"
        )
        return 1

    print("PAGES SOURCE MODE AUDIT PASSED")
    print(f"repository={repository}")
    print(f"required_build_type={REQUIRED_BUILD_TYPE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
