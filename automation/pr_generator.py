#!/usr/bin/env python3
import os

import requests


def issue_g5_gated_pull_request(repo_slug, head_branch, title, body_markdown):
    """
    Automates GitHub Pull Request initialization to enforce Single Source of Truth validation.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ GITHUB_TOKEN environment variable is unassigned. Skipping PR synchronization loop.")
        return False

    url = f"https://api.github.com/repos/{repo_slug}/pulls"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "title": title,
        "body": body_markdown,
        "head": head_branch,
        "base": "main",
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print(f"🚀 G5 Pull Request deployed successfully: {response.json().get('html_url')}")
        return True

    print(f"❌ Pull Request initialization failed [{response.status_code}]: {response.text}")
    return False
