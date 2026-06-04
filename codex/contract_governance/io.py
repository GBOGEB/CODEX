"""YAML loading and canonical content hashing for governance artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from .schema import GovernanceSSOT


def load_ssot(path: Path) -> GovernanceSSOT:
    """Load and validate the authoritative YAML SSOT with ruamel.yaml."""

    yaml = YAML(typ="rt")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.load(handle)
    return GovernanceSSOT.model_validate(data)


def canonicalize(value: Any) -> Any:
    """Return a JSON-stable representation for content hashing."""

    if isinstance(value, dict):
        return {str(key): canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    return value


def content_hash(payload: Any) -> str:
    """Hash canonical content, not generated binary container bytes."""

    canonical = json.dumps(canonicalize(payload), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
