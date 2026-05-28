"""KEB (Knowledge Exchange Bridge) client.

Provides read-only access to the shared governance artifacts hosted in
``KEB/governance/``:

- ``GLOSSARY.yml``       — authoritative term definitions
- ``governance_rules.yml`` — runtime debug and convergence rules
- ``metrics.yml``        — KPI categories and confidence levels

The client is intentionally read-only and stateless: every call re-reads from
the YAML files so that any update to governance artifacts is immediately
visible without restarting the process.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


#: Default location of the KEB governance directory relative to the repo root.
# parents[0] = src/keb, parents[1] = src, parents[2] = repo root
_DEFAULT_KEB_DIR = Path(__file__).resolve().parents[2] / "KEB" / "governance"


class KebClient:
    """Read-only client for KEB governance artifacts.

    Parameters
    ----------
    keb_dir:
        Path to the ``KEB/governance/`` directory.  Defaults to the standard
        location inside the CODEX repository clone.

    Examples
    --------
    >>> client = KebClient()
    >>> client.resolve_term("KEB")
    'Knowledge Exchange Bridge...'
    >>> rules = client.get_governance_rules()
    """

    def __init__(self, keb_dir: Path | str | None = None) -> None:
        self._dir = Path(keb_dir) if keb_dir is not None else _DEFAULT_KEB_DIR

    # ── private helpers ────────────────────────────────────────────────────

    def _load_yaml(self, filename: str) -> dict[str, Any]:
        path = self._dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"KEB governance file not found: {path}. "
                "Ensure KEB/governance/ is present in the repository."
            )
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data or {}

    # ── public API ─────────────────────────────────────────────────────────

    def resolve_term(self, term: str) -> str | None:
        """Look up *term* in the KEB glossary.

        Parameters
        ----------
        term:
            Case-sensitive term key (e.g. ``"KEB"``, ``"DRIFT"``).

        Returns
        -------
        str or None
            The definition string, or ``None`` if the term is not present.
        """
        data = self._load_yaml("GLOSSARY.yml")
        terms: dict = data.get("terms", {})
        entry = terms.get(term)
        if entry is None:
            return None
        if isinstance(entry, dict):
            return entry.get("definition")
        return str(entry)

    def list_terms(self) -> list[str]:
        """Return all term keys defined in the KEB glossary."""
        data = self._load_yaml("GLOSSARY.yml")
        return list(data.get("terms", {}).keys())

    def get_governance_rules(self) -> list[dict[str, str]]:
        """Return all runtime-debug and convergence governance rules.

        Returns
        -------
        list[dict]
            Each entry has ``"id"`` and ``"rule"`` (or ``"text"``) keys.
        """
        data = self._load_yaml("governance_rules.yml")
        rules: list[dict[str, str]] = []

        # runtime_debug_governance → principles list
        rtd = data.get("runtime_debug_governance", {})
        for principle in rtd.get("principles", []):
            rules.append(
                {"id": principle.get("id", ""), "rule": principle.get("rule", "")}
            )

        # convergence_rules → flat dict of CR-XXX: text
        convergence = data.get("convergence_rules", {})
        for rule_id, text in convergence.items():
            rules.append({"id": rule_id, "rule": str(text).strip()})

        return rules

    def get_kpi_categories(self) -> list[str]:
        """Return the KPI category names from KEB metrics."""
        data = self._load_yaml("metrics.yml")
        telemetry = data.get("telemetry_overview", {})
        return list(telemetry.get("KPI_categories", []))

    def get_confidence_levels(self) -> dict[str, dict[str, list[float]]]:
        """Return confidence-level range definitions from KEB metrics."""
        data = self._load_yaml("metrics.yml")
        return data.get("confidence_levels", {})
