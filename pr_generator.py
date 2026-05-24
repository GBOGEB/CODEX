#!/usr/bin/env python3
import os
import sys

import requests


def issue_g3_pull_request(repo_slug, head_branch, pr_title, pr_body_markdown):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("⚠️ Secret GITHUB_TOKEN environment variable is unassigned. Skipping PR generation.")
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
        print(f"🚀 Pull Request opened successfully: {response.json().get('html_url')}")
        return True

    print(f"❌ API Pull Request initialization failed Error {response.status_code}: {response.text}")
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--trigger":
        sample_body = """### 🤖 G3 Continuous Delivery Synchronization
* **Module Scope:** Deep alignment validation across A66 and Helium Cryo units.
* **Verification Anchor:** ANOVA Covariance Matrix and Exergy calculations validated successfully.
        """
        issue_g3_pull_request(
            "gbogeb/abacus",
            "feature/g3-system-update",
            "chore(g3): execute deep-tuple synchronization",
            sample_body,
        )
