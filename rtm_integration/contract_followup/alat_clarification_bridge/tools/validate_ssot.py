#!/usr/bin/env python3
"""Validate the ALaT Clarification Bridge YAML SSOT and linked registers."""
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
BRIDGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SSOT = BRIDGE_ROOT / "ssot" / "alat_questions_ssot_v0_1.yaml"
DEFAULT_RTM_LINKS = BRIDGE_ROOT / "RTM_LINKS.yaml"
DEFAULT_OFFER_REGISTER = BRIDGE_ROOT / "OFFER_REGISTER.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping at the root")
    return data


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate_register_links(
    questions: list[dict[str, Any]],
    rtm_data: dict[str, Any],
    offer_data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    question_ids = {str(question.get("id")) for question in questions}

    rtm_links = rtm_data.get("rtm_links")
    if not isinstance(rtm_links, dict):
        return ["RTM_LINKS.yaml must contain an rtm_links mapping"]

    offer_register = offer_data.get("offer_register")
    if not isinstance(offer_register, list):
        return ["OFFER_REGISTER.yaml must contain an offer_register list"]

    offer_by_id: dict[str, dict[str, Any]] = {}
    for entry in offer_register:
        if not isinstance(entry, dict) or not entry.get("id"):
            errors.append("OFFER_REGISTER.yaml entries must be mappings with an id")
            continue
        offer_id = str(entry["id"])
        offer_by_id[offer_id] = entry
        if str(entry.get("question")) not in question_ids:
            errors.append(f"{offer_id}: OFFER register question must target one of {sorted(question_ids)}")

    for link_id, entry in rtm_links.items():
        if not isinstance(entry, dict):
            errors.append(f"{link_id}: RTM link entry must be a mapping")
            continue
        if str(entry.get("question")) not in question_ids:
            errors.append(f"{link_id}: RTM link question must target one of {sorted(question_ids)}")

    for question in questions:
        qid = str(question.get("id"))
        for link_id in as_list(question.get("rtm_links")):
            link = rtm_links.get(link_id)
            if link is None:
                errors.append(f"{qid}: RTM link {link_id!r} is not defined in RTM_LINKS.yaml")
            elif str(link.get("question")) != qid:
                errors.append(f"{qid}: RTM link {link_id!r} targets {link.get('question')!r}")

        for offer_id in as_list(question.get("offer_actions")):
            offer = offer_by_id.get(str(offer_id))
            if offer is None:
                errors.append(f"{qid}: OFFER action {offer_id!r} is not defined in OFFER_REGISTER.yaml")
            elif str(offer.get("question")) != qid:
                errors.append(f"{qid}: OFFER action {offer_id!r} targets {offer.get('question')!r}")

    return errors


def validate(
    data: dict[str, Any],
    rtm_data: dict[str, Any] | None = None,
    offer_data: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    questions = as_list(data.get("questions"))
    valid_questions = [question for question in questions if isinstance(question, dict)]
    ids = [question.get("id") for question in valid_questions]

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

        if not as_list(question.get("offer_actions")):
            errors.append(f"{qid}: parent question must have at least one OFFER action")

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

    if rtm_data is not None and offer_data is not None:
        errors.extend(validate_register_links(valid_questions, rtm_data, offer_data))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ssot", nargs="?", default=DEFAULT_SSOT, type=Path, help="Path to the ALaT questions SSOT YAML file.")
    parser.add_argument("--rtm-links", type=Path, default=DEFAULT_RTM_LINKS, help="Path to RTM_LINKS.yaml.")
    parser.add_argument("--offer-register", type=Path, default=DEFAULT_OFFER_REGISTER, help="Path to OFFER_REGISTER.yaml.")
    args = parser.parse_args()

    try:
        data = load_yaml(args.ssot)
        rtm_data = load_yaml(args.rtm_links)
        offer_data = load_yaml(args.offer_register)
    except Exception as exc:  # noqa: BLE001 - report validation-friendly error
        print(f"ERROR: YAML failed to load: {exc}", file=sys.stderr)
        return 1

    errors = validate(data, rtm_data=rtm_data, offer_data=offer_data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {args.ssot} contains exactly Q3, Q4, and Q5 with resolved RTM/OFFER controls.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
