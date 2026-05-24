#!/usr/bin/env python3
from __future__ import annotations

import os
import requests


def issue_g3_pull_request(repo_slug: str, head_branch: str, pr_title: str, pr_body_markdown: str) -> bool:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not found; skipping PR generation.")
        return False

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
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code == 201:
        print(f"PR opened: {response.json().get('html_url')}")
        return True

    print(f"PR create failed ({response.status_code}): {response.text}")
    return False
