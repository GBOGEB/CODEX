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
        "BOUNDED_CODEX_APPLY_IMPLEMENTED_PENDING_RUNTIME_PROOF",
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
    enabled_mutation = authn.get("enabled_mutation_transports")
    if state in {"DESIGN_ONLY_NO_MUTATION_BACKEND", "AUTHENTICATED_TRANSPORT_IMPLEMENTED_NO_MUTATION"}:
        if enabled_mutation != []:
            errors.append("pre-apply gateway state may not enable a mutation transport")
    elif enabled_mutation != ["OWNER_COMMENT_AUTOMATION_PR"]:
        errors.append("bounded apply state must enable only OWNER_COMMENT_AUTOMATION_PR")
    if state in {
        "AUTHENTICATED_TRANSPORT_IMPLEMENTED_NO_MUTATION",
        "BOUNDED_CODEX_APPLY_IMPLEMENTED_PENDING_RUNTIME_PROOF",
    }:
        if authn.get("selected_transport") != "GITHUB_ACTIONS_WORKFLOW_DISPATCH":
            errors.append("transport implementation must select GitHub Actions workflow_dispatch")
        expected_transport_state = (
            "AUTHENTICATED_STAGE_ONLY"
            if state == "AUTHENTICATED_TRANSPORT_IMPLEMENTED_NO_MUTATION"
            else "AUTHENTICATED_STAGE_ONLY_PLUS_OWNER_BOUNDED_APPLY"
        )
        if authn.get("transport_state") != expected_transport_state:
            errors.append("authenticated transport state mismatch")

    authz = contract.get("authorization", {})
    if authz.get("default") != "DENY":
        errors.append("authorization must default deny")
    if authz.get("remote_mutation_default") != "DENY":
        errors.append("remote mutation must default deny")
    apply_rule = authz.get("action_classes", {}).get("APPLY_BOUNDED_CODEX", {})
    expected_apply_enabled = state == "BOUNDED_CODEX_APPLY_IMPLEMENTED_PENDING_RUNTIME_PROOF"
    if apply_rule.get("enabled") is not expected_apply_enabled:
        errors.append("bounded Apply enabled state does not match gateway state")
    if apply_rule.get("allowed_repositories") != ["GBOGEB/CODEX"]:
        errors.append("bounded Apply may target CODEX only")
    if expected_apply_enabled:
        if apply_rule.get("allowed_intents") != ["REFRESH_FEDERATION_HEADS"]:
            errors.append("bounded Apply may enable only REFRESH_FEDERATION_HEADS")
        if apply_rule.get("direct_main_write") is not False:
            errors.append("bounded Apply may not write main directly")
        if apply_rule.get("review_pr_required") is not True:
            errors.append("bounded Apply requires review PR")
    if state in {
        "AUTHENTICATED_TRANSPORT_IMPLEMENTED_NO_MUTATION",
        "BOUNDED_CODEX_APPLY_IMPLEMENTED_PENDING_RUNTIME_PROOF",
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

    if state == "BOUNDED_CODEX_APPLY_IMPLEMENTED_PENDING_RUNTIME_PROOF":
        bounded = contract.get("bounded_apply_runtime", {})
        if bounded.get("workflow") != ".github/workflows/missioncontrol-owner-bounded-apply.yml":
            errors.append("bounded Apply workflow mismatch")
        if bounded.get("executor") != "scripts/missioncontrol_bounded_apply.py":
            errors.append("bounded Apply executor mismatch")
        if bounded.get("approval_surface") != "ISSUE_879_OWNER_COMMENT":
            errors.append("bounded Apply must require owner issue-comment approval")
        if bounded.get("required_author_association") != "OWNER":
            errors.append("bounded Apply requires OWNER author association")
        if bounded.get("mutation_mode") != "AUTOMATION_BRANCH_PR_ONLY":
            errors.append("bounded Apply mutation mode must be automation branch/PR only")
        if bounded.get("direct_main_write") is not False:
            errors.append("bounded Apply direct-main write must remain false")
        if bounded.get("review_pr_required") is not True:
            errors.append("bounded Apply requires a review PR")
        if bounded.get("runtime_proof") != "WITHHELD_OWNER_APPLY_COMMAND_REQUIRED":
            errors.append("bounded Apply runtime proof must remain withheld before owner command")
        if bounded.get("remote_authority_mutation") is not False:
            errors.append("bounded Apply may not mutate remote authority")
        expected_paths = {
            "mission_control/mycelium/source_status.json",
            "docs/data/missioncontrol_source_status.json",
            "mission_control/mycelium/control_events.json",
            "docs/data/missioncontrol_control_events.json",
            "mission_control/mycelium/metrics_snapshot.json",
            "docs/data/missioncontrol_metrics.json",
        }
        if set(bounded.get("changed_path_allowlist", [])) != expected_paths:
            errors.append("bounded Apply changed-path allow-list drifted")
        workflow_path = ROOT / ".github/workflows/missioncontrol-owner-bounded-apply.yml"
        request_builder = ROOT / "scripts/missioncontrol_owner_bounded_apply_request.py"
        executor = ROOT / "scripts/missioncontrol_bounded_apply.py"
        for path, label in (
            (workflow_path, "bounded Apply workflow"),
            (request_builder, "bounded Apply request builder"),
            (executor, "bounded Apply executor"),
        ):
            if not path.exists():
                errors.append(f"{label} is missing")
        if workflow_path.exists():
            workflow = workflow_path.read_text(encoding="utf-8")
            for token in (
                "github.event.issue.number == 879",
                "github.event.comment.author_association == 'OWNER'",
                "gh pr create",
                "direct_main_write=false",
                "remote_authority_mutation=false",
            ):
                if token not in workflow:
                    errors.append(f"bounded Apply workflow missing guard: {token}")
            if "git push origin main" in workflow or "git push origin HEAD:main" in workflow:
                errors.append("bounded Apply workflow contains forbidden direct-main push")

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
