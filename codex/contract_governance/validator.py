"""Validation gates for generated governance artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from openpyxl import load_workbook

from .builder import workbook_payload
from .io import content_hash
from .schema import Audience, GovernanceSSOT

Tier = Literal["internal", "bidder"]


class ValidationError(RuntimeError):
    """Raised when a generated governance artifact fails a gate."""


def validate_generated(ssot: GovernanceSSOT, out_dir: Path, tier: Tier) -> None:
    """Validate tier stripping, content hash, and header binding invariants."""

    tier_dir = out_dir / tier
    manifest_path = tier_dir / f"{ssot.package_id}_{tier}_manifest.json"
    xlsx_path = tier_dir / f"{ssot.package_id}_{tier}.xlsx"
    if not manifest_path.exists() or not xlsx_path.exists():
        raise ValidationError(f"missing generated artifacts for tier {tier}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_payload = workbook_payload(ssot, tier)
    expected_hash = content_hash(expected_payload)
    if manifest.get("content_hash") != expected_hash:
        raise ValidationError("manifest content hash does not match canonical generated content")

    workbook = load_workbook(xlsx_path, read_only=True, data_only=True)
    expected_sheets = [sheet["name"] for sheet in expected_payload["sheets"]]
    if workbook.sheetnames != expected_sheets:
        raise ValidationError(f"workbook sheets drifted: expected {expected_sheets}, observed {workbook.sheetnames}")

    if tier == "bidder":
        forbidden = [sheet.name for sheet in ssot.generated_sheets if sheet.audience in {Audience.internal, Audience.evaluation}]
        leaked = sorted(set(forbidden) & set(workbook.sheetnames))
        if leaked:
            raise ValidationError(f"bidder workbook leaked non-bidder sheets: {leaked}")

    _validate_header_bindings(ssot)


def _validate_header_bindings(ssot: GovernanceSSOT) -> None:
    for req in ssot.requirements:
        by_name = {binding.header_name: binding for binding in req.header_bindings}
        if len(by_name) != len(req.header_bindings):
            raise ValidationError(f"duplicate header binding names on {req.req_id}")
        for binding in req.header_bindings:
            if binding.observed_index < 1 or not binding.observed_column:
                raise ValidationError(f"invalid observed position for {req.req_id}:{binding.header_name}")
