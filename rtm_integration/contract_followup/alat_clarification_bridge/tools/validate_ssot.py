#!/usr/bin/env python3
"""Validate the ALaT Clarification Bridge YAML SSOT."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

EXPECTED_QUESTIONS = ["Q3", "Q4", "Q5"]
BOUNDARY_STATES = ["nominal", "transient", "abnormal"]
BOUNDARY_LINES = ["Line W", "Line S"]
FORBIDDEN_BIDDER_TERMS = ["slide", "slides"]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping at the root")
    return data


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    questions = as_list(data.get("questions"))
    ids = [question.get("id") for question in questions if isinstance(question, dict)]

    if ids != EXPECTED_QUESTIONS:
        errors.append(f"questions must be exactly {EXPECTED_QUESTIONS}; found {ids}")

    dbe_coverage: set[tuple[str, str]] = set()
    for question in questions:
        if not isinstance(question, dict):
            errors.append("each question must be a mapping")
            continue

        qid = question.get("id", "<missing>")
        if not as_list(question.get("rtm_links")):
            errors.append(f"{qid}: parent question must have at least one RTM link")

        stakeholders = question.get("stakeholders")
        if not isinstance(stakeholders, dict):
            errors.append(f"{qid}: stakeholders mapping is required")
        else:
            for owner_key in ("discipline_owner", "contract_owner", "rtm_owner"):
                if not stakeholders.get(owner_key):
                    errors.append(f"{qid}: stakeholder {owner_key} is required")

        bidder_answer = "\n".join(str(item) for item in as_list(question.get("bidder_answer"))).lower()
        for forbidden in FORBIDDEN_BIDDER_TERMS:
            if re.search(rf"\b{re.escape(forbidden)}\b", bidder_answer):
                errors.append(f"{qid}: bidder-facing answer must not reference {forbidden!r}")

        controlled = question.get("controlled_references")
        if not isinstance(controlled, dict) or controlled.get("pressure_temperature_flow") != "main input/interface tables":
            errors.append(f"{qid}: pressure/temperature/flow must reference main input/interface tables")

        for action in as_list(question.get("dbe_actions")):
            if not isinstance(action, dict):
                continue
            boundary = str(action.get("boundary", ""))
            action_text = str(action.get("action", ""))
            combined = f"{boundary} {action_text}"
            for line in BOUNDARY_LINES:
                for state in BOUNDARY_STATES:
                    if line.lower() in combined.lower() and state in combined.lower():
                        dbe_coverage.add((line, state))

    for line in BOUNDARY_LINES:
        for state in BOUNDARY_STATES:
            if (line, state) not in dbe_coverage:
                errors.append(f"DBE action missing for {line} {state} handover boundary")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "ssot",
        nargs="?",
        default=Path(__file__).resolve().parents[1] / "ssot" / "alat_questions_ssot_v0_1.yaml",
        type=Path,
        help="Path to the ALaT questions SSOT YAML file.",
    )
    args = parser.parse_args()

    try:
        data = load_yaml(args.ssot)
    except Exception as exc:  # noqa: BLE001 - report validation-friendly error
        print(f"ERROR: YAML failed to load: {exc}", file=sys.stderr)
        return 1

    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {args.ssot} contains exactly Q3, Q4, and Q5 with required traceability controls.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
