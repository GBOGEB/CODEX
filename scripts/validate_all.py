#!/usr/bin/env python3
"""Validate Wave-0 federation bootstrap artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: str) -> str:
    target = ROOT / path
    if not target.exists():
        fail(f"Missing required file: {path}")
    return target.read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    target = ROOT / path
    if not target.exists():
        fail(f"Missing required JSON file: {path}")
    with target.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_workflow() -> None:
    workflow = read(".github/workflows/validate-federation.yml")
    required = ["on:", "push:", "pull_request:", "python scripts/validate_all.py"]
    for marker in required:
        if marker not in workflow:
            fail(f"Workflow missing marker: {marker}")


def validate_schema(path: str, required_fields: set[str]) -> None:
    schema = load_json(path)
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail(f"{path} must declare JSON Schema draft 2020-12")
    if schema.get("type") != "object":
        fail(f"{path} must validate an object")
    declared = set(schema.get("required", []))
    missing = required_fields - declared
    if missing:
        fail(f"{path} missing required fields: {sorted(missing)}")


def validate_ts_tests() -> None:
    job_queue_test = read("tests/job_queue.test.ts")
    for marker in ["enqueue", "dequeue", "empty queue"]:
        if marker not in job_queue_test:
            fail(f"tests/job_queue.test.ts missing coverage marker: {marker}")

    federation_test = read("tests/federation_validation.test.ts")
    for marker in ["federation.schema.json", "handover.schema.json"]:
        if marker not in federation_test:
            fail(f"tests/federation_validation.test.ts missing schema marker: {marker}")


def validate_handover() -> None:
    handover = load_json("handover/CURRENT.json")
    if handover.get("wave") != "Wave-0":
        fail("handover/CURRENT.json wave must be Wave-0")
    if handover.get("status") != "near-complete":
        fail("handover/CURRENT.json status must be near-complete")
    completed = set(handover.get("completed_tasks", []))
    missing = {f"W0-{task}" for task in range(21, 27)} - completed
    if missing:
        fail(f"handover/CURRENT.json missing completed tasks: {sorted(missing)}")


def validate_report() -> None:
    report = read("CODEX_EXECUTION_REPORT.md")
    for marker in ["Commit SHAs", "Issue-001", "Wave-0 completion", "Wave-1 completion"]:
        if marker not in report:
            fail(f"CODEX_EXECUTION_REPORT.md missing marker: {marker}")


def run_pytest_smoke() -> None:
    smoke_tests = [
        "tests/federation/test_schema_validation.py",
        "tests/test_federation_runtime_registry.py",
        "tests/test_phase0_federation_bridge.py",
    ]
    existing = [test for test in smoke_tests if (ROOT / test).exists()]
    if not existing:
        return
    subprocess.run([sys.executable, "-m", "pytest", *existing], cwd=ROOT, check=True)


def main() -> int:
    checks = [
        validate_workflow,
        lambda: validate_schema("schemas/federation.schema.json", {"federation_id", "version", "participants", "validation"}),
        lambda: validate_schema("schemas/handover.schema.json", {"wave", "status", "completed_tasks"}),
        validate_ts_tests,
        validate_handover,
        validate_report,
        run_pytest_smoke,
    ]
    for check in checks:
        check()
    print("Wave-0 federation validation passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Validation command failed with exit code {exc.returncode}: {exc.cmd}", file=sys.stderr)
        raise SystemExit(exc.returncode)
    except Exception as exc:  # noqa: BLE001 - command-line validation should print concise failures.
        print(f"Validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
