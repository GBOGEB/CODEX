#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MC = ROOT / "mission_control" / "mycelium"
CONTRACT = MC / "execution_gateway_contract.yaml"
REQUEST_SCHEMA = MC / "schemas" / "execution_request.schema.json"
RECEIPT_SCHEMA = MC / "schemas" / "execution_receipt.schema.json"
DESIGN = MC / "AUTHENTICATED_EXECUTION_GATEWAY_DESIGN.md"
BOUNDED_APPLY_POLICY = MC / "bounded_apply_policy.yaml"
BOUNDED_APPLY_LEDGER = MC / "gateway" / "bounded_apply_ledger.json"
BOUNDED_APPLY_PLANNER = ROOT / "scripts" / "missioncontrol_bounded_apply.py"
BOUNDED_APPLY_TEST = ROOT / "tests" / "test_missioncontrol_bounded_apply.py"


def validate() -> list[str]:
    errors: list[str] = []
    contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    request = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
    design = DESIGN.read_text(encoding="utf-8")

    state = contract.get("state")
    allowed_states = {
        "DESIGN_ONLY_NO_MUTATION_BACKEND",
        "AUTHENTICATED_TRANSPORT_IMPLEMENTED_NO_MUTATION",
        "BOUNDED_APPLY_IMPLEMENTED_DISABLED_PENDING_EXACT_HEAD_PROOF",
    }
    if state not in allowed_states:
        errors.append("gateway state is not a governed design/transport state")
    authority = contract.get("authority", {})
    if authority.get("authority_transfer") is not False:
        errors.append("gateway may not transfer authority")
    if authority.get("formal_credit_delta") != 0 or authority.get("engineering_credit_delta") != 0:
        errors.append("gateway design may not create credit")
    if authority.get("remote_engineering_authority_mutation") is not False:
        errors.append("remote engineering mutation must remain disabled")
    if authority.get("remote_execution_authority_mutation") is not False:
        errors.append("remote execution mutation must remain disabled")

    client = contract.get("client_boundary", {})
    if client.get("static_pages_mode") != "STAGE_OR_DRY_RUN_ONLY":
        errors.append("static Pages must remain stage/dry-run only")
    if client.get("secrets_in_browser_forbidden") is not True:
        errors.append("browser secrets must be forbidden")
    if client.get("client_asserted_identity_is_trusted") is not False:
        errors.append("client-asserted identity must not be trusted")

    authn = contract.get("authentication", {})
    if authn.get("required") is not True or authn.get("principal_bound_server_side") is not True:
        errors.append("server-side authentication principal binding is required")
    if authn.get("enabled_mutation_transports") != []:
        errors.append("gateway must not enable a mutation transport in v0.1")
    if state in {
        "AUTHENTICATED_TRANSPORT_IMPLEMENTED_NO_MUTATION",
        "BOUNDED_APPLY_IMPLEMENTED_DISABLED_PENDING_EXACT_HEAD_PROOF",
    }:
        if authn.get("selected_transport") != "GITHUB_ACTIONS_WORKFLOW_DISPATCH":
            errors.append("transport implementation must select GitHub Actions workflow_dispatch")
        if authn.get("transport_state") != "AUTHENTICATED_STAGE_ONLY":
            errors.append("transport implementation must remain authenticated STAGE_ONLY")

    authz = contract.get("authorization", {})
    if authz.get("default") != "DENY":
        errors.append("authorization must default deny")
    if authz.get("remote_mutation_default") != "DENY":
        errors.append("remote mutation must default deny")
    apply_rule = authz.get("action_classes", {}).get("APPLY_BOUNDED_CODEX", {})
    if apply_rule.get("enabled") is not False:
        errors.append("Apply must remain disabled in design slice")
    if apply_rule.get("allowed_repositories") != ["GBOGEB/CODEX"]:
        errors.append("future bounded Apply may target CODEX only in this design")
    if state in {
        "AUTHENTICATED_TRANSPORT_IMPLEMENTED_NO_MUTATION",
        "BOUNDED_APPLY_IMPLEMENTED_DISABLED_PENDING_EXACT_HEAD_PROOF",
    }:
        runtime = contract.get("transport_runtime", {})
        if runtime.get("enabled_action_class") != "STAGE_ONLY":
            errors.append("transport runtime must enable STAGE_ONLY only")
        if runtime.get("mutation_enabled") is not False:
            errors.append("transport runtime must keep mutation disabled")
        if runtime.get("receipt_storage") != "GITHUB_ACTION_ARTIFACT":
            errors.append("transport receipt storage must be GitHub Actions artifact")
        if runtime.get("workflow_run_job_bound_in_receipt") is not True:
            errors.append("transport receipt must bind workflow run/job")

    guards = contract.get("execution_guards", {})
    for key in (
        "idempotency_key_required",
        "replay_of_completed_request_forbidden",
        "changed_path_allowlist_required_for_mutation",
        "dry_run_before_apply_required",
        "approval_before_mutation_required",
    ):
        if guards.get(key) is not True:
            errors.append(f"missing gateway guard: {key}")

    for schema, name in ((request, "request"), (receipt, "receipt")):
        required = set(schema.get("required", []))
        for field in ("authority_transfer", "formal_credit_delta", "engineering_credit_delta"):
            if field not in required:
                errors.append(f"{name} schema does not require {field}")

    if state == "BOUNDED_APPLY_IMPLEMENTED_DISABLED_PENDING_EXACT_HEAD_PROOF":
        for path in (
            BOUNDED_APPLY_POLICY,
            BOUNDED_APPLY_LEDGER,
            BOUNDED_APPLY_PLANNER,
            BOUNDED_APPLY_TEST,
        ):
            if not path.exists():
                errors.append(f"missing bounded-apply surface: {path.relative_to(ROOT)}")
        policy = yaml.safe_load(BOUNDED_APPLY_POLICY.read_text(encoding="utf-8"))
        if policy.get("state") != "IMPLEMENTED_DISABLED_PENDING_EXACT_HEAD_PROOF":
            errors.append("bounded-apply policy state mismatch")
        if policy.get("mutation_enabled") is not False:
            errors.append("bounded-apply policy may not enable mutation")
        if policy.get("enabled_mutation_transports") != []:
            errors.append("bounded-apply mutation transports must remain empty")
        target = policy.get("target", {})
        if target.get("repository") != "GBOGEB/CODEX" or target.get("ref") != "main":
            errors.append("bounded-apply policy must remain CODEX main only")
        bounded = contract.get("bounded_apply_runtime", {})
        if bounded.get("implementation_state") != "IMPLEMENTED_DISABLED_PENDING_EXACT_HEAD_PROOF":
            errors.append("bounded-apply runtime implementation state mismatch")
        if bounded.get("mutation_enabled") is not False or bounded.get("execute_permitted") is not False:
            errors.append("bounded-apply implementation must remain non-executable")
        if bounded.get("enabled_mutation_transports") != []:
            errors.append("bounded-apply implementation may not enable a mutation transport")
        for key in (
            "exact_head_required",
            "changed_path_allowlist_required",
            "explicit_approval_ref_required",
            "exact_head_dry_run_receipt_required",
            "completed_replay_forbidden",
        ):
            if bounded.get(key) is not True:
                errors.append(f"bounded-apply runtime guard missing: {key}")
        props = request.get("properties", {})
        for field in ("approval_ref", "dry_run_receipt_ref"):
            if field not in props:
                errors.append(f"bounded-apply request field missing: {field}")

    for token in ("Default authorization is DENY", "Browser secrets are forbidden", "CODEX-only bounded actions"):
        if token not in design:
            errors.append(f"design documentation missing token: {token}")

    return errors


if __name__ == "__main__":
    found = validate()
    if found:
        for item in found:
            print(f"ERROR: {item}")
        raise SystemExit(1)
    print("MissionControl authenticated execution gateway design: PASS")
