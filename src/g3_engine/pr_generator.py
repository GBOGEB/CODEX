#!/usr/bin/env python3
from __future__ import annotations

from json import JSONDecodeError
import os
import requests
from typing import Any, Dict


def issue_g3_pull_request(repo_slug: str, head_branch: str, pr_title: str, pr_body_markdown: str) -> Dict[str, Any]:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"success": False, "error": "GITHUB_TOKEN not found; skipping PR generation."}

    url = f"https://api.github.com/repos/{repo_slug}/pulls"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "title": pr_title,
        "body": pr_body_markdown,
        "head": head_branch,
        "base": "main",
        "maintainer_can_modify": True,
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return {"success": False, "error": f"PR create failed: {exc}"}

    if response.status_code == 201:
        try:
            pr_url = response.json().get("html_url", "URL not provided in response")
        except JSONDecodeError as exc:
            return {"success": False, "error": f"PR create failed: invalid JSON response ({exc})"}
        return {"success": True, "pr_url": pr_url}

    return {"success": False, "error": f"PR create failed ({response.status_code}): {response.text}"}
