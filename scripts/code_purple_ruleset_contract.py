"""Read-only branch protection MIP contract (GitHub admin changes are external).

Consumes a SHA-bound GitHub census; produces only a staged ruleset proposal.
Does not grant merge authority or make network/write calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "code-purple.protection-mip-pilot.v1"
RULESET_NAME = "CODE_PURPLE_MAIN_ADMISSION_V1"
REQUIRED = frozenset(("deletion", "non_fast_forward", "pull_request"))
SHA = re.compile(r"^[a-f0-9]{40}$")


def checksum(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def proposed_ruleset() -> dict:
    """No check context or bypass is invented; reviewers must be real people."""
    return {
        "name": RULESET_NAME,
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": False,
                "require_last_push_approval": True,
                "required_review_thread_resolution": True,
                "allowed_merge_methods": ["merge", "squash", "rebase"],
            }},
        ],
    }


def targets_default(item: dict, branch: str) -> bool:
    if item.get("enforcement") != "active" or item.get("target") != "branch":
        return False
    ref = (item.get("conditions") or {}).get("ref_name") or {}
    acceptable = {"~DEFAULT_BRANCH", "~ALL", branch, "refs/heads/" + branch}
    return (bool(acceptable.intersection(ref.get("include") or []))
            and not acceptable.intersection(ref.get("exclude") or []))


def checks(item: dict) -> set[str]:
    found = set()
    for rule in item.get("rules") or []:
        kind = rule.get("type")
        if kind in ("deletion", "non_fast_forward"):
            found.add(kind)
        elif kind == "pull_request":
            p = rule.get("parameters") or {}
            if (type(p.get("required_approving_review_count")) is int
                    and p["required_approving_review_count"] >= 1
                    and p.get("require_last_push_approval") is True
                    and p.get("dismiss_stale_reviews_on_push") is True
                    and p.get("required_review_thread_resolution") is True):
                found.add(kind)
    return found


def assess(repo: dict) -> dict:
    name = repo.get("repo", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", name):
        raise ValueError("Invalid repository identity")
    branch = repo.get("default_branch")
    head = repo.get("head_sha")
    protected = repo.get("protected")
    out = {
        "repo": name, "default_branch": branch, "exact_head": head,
        "protected": protected, "status": "UNKNOWN", "action": "INVESTIGATE",
        "ruleset_id": None, "merge_admission": "HOLD",
    }
    if repo.get("size") == 0 or repo.get("archived") or repo.get("fork"):
        out.update(status="EXCEPTION_REVIEW", action="REVIEW_EMPTY_FORK_ARCHIVED")
        return out
    if not branch or not isinstance(head, str) or not SHA.fullmatch(head) or type(protected) is not bool:
        return out
    all_rules = repo.get("rulesets")
    if not isinstance(all_rules, list):
        return out
    active = [r for r in all_rules if targets_default(r, branch)]
    kinds = set().union(*(checks(r) for r in active)) if active else set()
    out["verified_rule_types"] = sorted(kinds)
    if protected is True and REQUIRED.issubset(kinds):
        out.update(status="CONFIGURED_NOT_ADMITTED", action="VERIFY_INDEPENDENT_REVIEW_AND_CI")
    elif len(active) == 1 and not active[0].get("rules"):
        out.update(status="ACTIVE_EMPTY_RULESET", action="UPDATE_EXISTING_EMPTY",
                   ruleset_id=active[0].get("id"))
    elif not all_rules and protected is False:
        out.update(status="NO_RULESET", action="CREATE_ONE")
    elif not all_rules and protected is True:
        out.update(status="CLASSIC_PROTECTION_UNKNOWN", action="INSPECT_CLASSIC_PROTECTION")
    else:
        out.update(status="PARTIAL_OR_CONFLICTING", action="REVIEW_WITHOUT_OVERWRITE")
    return out


def report(source: dict) -> dict:
    if source.get("schema") != SCHEMA or not isinstance(source.get("repositories"), list):
        raise ValueError("Invalid source schema")
    rows = sorted((assess(r) for r in source["repositories"]), key=lambda r: r["repo"])
    names = [r["repo"] for r in rows]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate repository identity")
    candidates = [r for r in rows if r["status"] != "EXCEPTION_REVIEW"]
    protected = sum(r["protected"] is True for r in candidates)
    configured = sum(r["status"] == "CONFIGURED_NOT_ADMITTED" for r in candidates)
    return {
        "schema": SCHEMA, "input_sha256": checksum(source),
        "policy_sha256": checksum(proposed_ruleset()),
        "scope": source.get("scope", "UNKNOWN"),
        "observed_at": source.get("observed_at"),
        "rows": rows,
        "metrics": {
            "inspected": len(rows),
            "protected_reported": {"numerator": protected, "denominator": len(candidates)},
            "baseline_configured": {"numerator": configured, "denominator": len(candidates)},
            "admission_verified": None,
        },
        "proposed_ruleset": proposed_ruleset(),
        "mutation": False, "authority_transfer": False,
        "next_dov": "owner admin action; exact-head readback; independent review and negative merge test",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    source = json.loads(args.snapshot.read_text(encoding="utf-8"))
    receipt = report(source)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PROPOSAL_ONLY", receipt["metrics"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
