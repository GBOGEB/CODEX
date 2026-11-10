#!/usr/bin/env python3
"""Shadow-only alias resolver consuming CODEX's existing mesh action/status owners.

This is NOT a scheduler, command dispatcher, reviewer, source authority, or merge gate.
Candidate routing is exact phrase allowlisting; unknown/ambiguous input fails closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "federation/mesh/PROMPT_ALIAS_SHADOW_PROFILE_v1.json"
ACTION_PATH = ROOT / "federation/mesh/GLOBAL_ACTION_TAXONOMY_v1.yaml"
STATUS_PATH = ROOT / "governance/mesh/MESH_STATUS_CONTRACT_v1.yaml"


class AliasPolicyError(ValueError):
    """A phrase is unknown, ambiguous, or unsafe to route."""


def git_blob_oid(data: bytes) -> str:
    # Git object identity uses SHA-1 by specification; never use this as an auth hash.
    payload = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    return hashlib.sha1(payload, usedforsecurity=False).hexdigest()


def normalize_phrase(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 120:
        raise AliasPolicyError("EMPTY_OR_OVERSIZE_PHRASE")
    if not value.isascii():
        raise AliasPolicyError("NON_ASCII_PHRASE_UNREVIEWED")
    value = re.sub(r"[-_.!?]+", " ", value.casefold()).strip()
    value = " ".join(value.split())
    if not re.fullmatch(r"[a-z0-9 ]+", value):
        raise AliasPolicyError("UNSUPPORTED_PUNCTUATION_OR_INSTRUCTIONS")
    return value


def top_level_yaml_keys(contents: bytes, section: str) -> set[str]:
    """Strict textual discovery of top-level mapping keys, not a YAML authority parser."""
    text = contents.decode("utf-8")
    match = re.search(r"(?ms)^" + re.escape(section)
                      + r":\s*\n(.*?)(?=^[A-Za-z][A-Za-z0-9_-]*:|\Z)", text)
    if not match:
        raise AliasPolicyError("MISSING_CANONICAL_SECTION_" + section)
    keys = set(re.findall(r"(?m)^  ([A-Z][A-Z0-9_]*):(?:\s|$)", match.group(1)))
    if not keys:
        raise AliasPolicyError("EMPTY_CANONICAL_SECTION_" + section)
    return keys


def load_profile(path: Path = PROFILE_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_profile(profile: dict, *, action_bytes: bytes | None = None,
                     status_bytes: bytes | None = None) -> dict:
    if (profile.get("schema") != "gbogeb.prompt-alias-shadow.v1"
            or profile.get("status") != "SHADOW_NO_DISPATCH"
            or profile.get("owner_repo") != "GBOGEB/CODEX"
            or profile.get("authority_transfer") is not False
            or profile.get("formal_credit_delta") != 0
            or profile.get("dispatch_authorized") is not False):
        raise AliasPolicyError("PROFILE_AUTHORITY_OR_SCHEMA_VIOLATION")
    action_bytes = ACTION_PATH.read_bytes() if action_bytes is None else action_bytes
    status_bytes = STATUS_PATH.read_bytes() if status_bytes is None else status_bytes
    expected = profile["source_binding"]
    if (git_blob_oid(action_bytes) != expected["action_taxonomy_git_blob"]
            or git_blob_oid(status_bytes) != expected["mesh_status_git_blob"]):
        raise AliasPolicyError("CANONICAL_SOURCE_OID_DRIFT_REQUALIFICATION_REQUIRED")
    action_ids = top_level_yaml_keys(action_bytes, "action_monikers")
    status_ids = top_level_yaml_keys(status_bytes, "code_semantics")
    reserved = set(profile["reserved_status_keys"])
    if reserved != status_ids or reserved.intersection(action_ids):
        raise AliasPolicyError("STATUS_ACTION_NAMESPACE_COLLISION")
    if profile.get("deprecation", {}).get("automatic_phase_transition") is not False:
        raise AliasPolicyError("UNAUTHORIZED_AUTOMATIC_DEPRECATION")
    if profile.get("deprecation", {}).get("phase") != "SHADOW_WARN":
        raise AliasPolicyError("OWNER_DEPRECATION_TRANSITION_NOT_ADMITTED")

    forbidden = {normalize_phrase(x) for x in profile.get("explicit_non_aliases", [])}
    index: dict[str, tuple[str, str, str, bool]] = {}
    def register(phrase: str, kind: str, route_id: str, contract: str,
                 deprecated: bool = False) -> None:
        token = normalize_phrase(phrase)
        if token in forbidden:
            raise AliasPolicyError("FORBIDDEN_STATUS_OR_AMBIGUOUS_ALIAS_" + token)
        if token in index:
            raise AliasPolicyError("ALIAS_COLLISION_" + token)
        index[token] = (kind, route_id, contract, deprecated)

    for row in profile["atomic_actions"]:
        if row["id"] not in action_ids:
            raise AliasPolicyError("ACTION_ID_NOT_CANONICAL_" + row["id"])
        for phrase in row["aliases"]:
            register(phrase, "ATOMIC", row["id"], profile["output_contract"])
        for phrase in row.get("legacy_warn", []):
            register(phrase, "ATOMIC", row["id"], profile["output_contract"], True)
    for row in profile["composite_selectors"]:
        if row["id"] not in {"G3A", "MESH_CLOSURE_CONTROL"}:
            raise AliasPolicyError("UNREVIEWED_COMPOSITE_SELECTOR")
        for phrase in row["aliases"]:
            register(phrase, "COMPOSITE", row["id"], row["output_contract"])
    return {"index": index, "action_ids": action_ids, "reserved_status_keys": reserved}


def resolve_phrase(phrase: str, profile: dict | None = None,
                   *, validated: dict | None = None) -> dict:
    profile = load_profile() if profile is None else profile
    validated = validate_profile(profile) if validated is None else validated
    token = normalize_phrase(phrase)
    if token in {normalize_phrase(x) for x in profile["explicit_non_aliases"]}:
        raise AliasPolicyError("AMBIGUOUS_OR_RESERVED_TOKEN")
    found = validated["index"].get(token)
    if found is None:
        raise AliasPolicyError("UNKNOWN_PHRASE_NO_FUZZY_DISPATCH")
    kind, route_id, contract, deprecated = found
    required = ["scope", "exact_source_sha", "owner_boundary"]
    if kind == "COMPOSITE":
        required = next(x["required_inputs"] for x in profile["composite_selectors"]
                        if x["id"] == route_id)
    route = {
        "schema": contract,
        "kind": kind,
        "canonical_id": route_id,
        "owner_repo": profile["owner_repo"],
        "required_inputs": required,
        "dispatch_authorized": False,
        "authority_transfer": False,
        "formal_credit_delta": 0,
    }
    # Diagnostics are deliberately OUTSIDE route so all allowed synonyms produce
    # byte-identical canonical action candidate payloads.
    return {"route": route, "diagnostic": ("DEPRECATED_ALIAS_WARNING"
            if deprecated else "EXPLICIT_ALIAS_MATCH")}


def canonical_digest(route: dict) -> str:
    data = json.dumps(route, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--resolve", metavar="EXACT_PHRASE")
    args = parser.parse_args(argv)
    try:
        profile = load_profile()
        state = validate_profile(profile)
        if args.resolve is not None:
            outcome = resolve_phrase(args.resolve, profile, validated=state)
            outcome["candidate_sha256"] = canonical_digest(outcome["route"])
            print(json.dumps(outcome, sort_keys=True))
        else:
            print("PROMPT_ALIAS_SHADOW=PASS aliases=" + str(len(state["index"]))
                  + " actions=" + str(len(profile["atomic_actions"]))
                  + " composites=" + str(len(profile["composite_selectors"])))
        return 0
    except (AliasPolicyError, ValueError, KeyError, OSError) as exc:
        print("PROMPT_ALIAS_SHADOW=FAIL " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
