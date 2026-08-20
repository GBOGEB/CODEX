"""Registry of governance runtime export formats.

The W003A export layer is renderer-independent. JSON, YAML, and Markdown are
implemented as canonical runtime outputs; Excel and HTML are reserved for later
renderer drops and intentionally remain placeholders here.
"""

from __future__ import annotations

from pathlib import Path

EXPORT_FORMATS = [
    "json",
    "yaml",
    "markdown",
    "excel",
    "html",
]

IMPLEMENTED_EXPORT_FORMATS = ("json", "yaml", "markdown")
PLACEHOLDER_EXPORT_FORMATS = ("excel", "html")

EXPORT_OUTPUTS = {
    "json": Path("generated/governance_runtime.json"),
    "yaml": Path("generated/governance_runtime.yaml"),
    "markdown": Path("generated/governance_runtime.md"),
}


def export_format_status(export_format: str) -> str:
    """Return implementation status for an export format."""
    if export_format in IMPLEMENTED_EXPORT_FORMATS:
        return "implemented"
    if export_format in PLACEHOLDER_EXPORT_FORMATS:
        return "placeholder"
    return "unsupported"


def registry_entries() -> list[dict[str, str]]:
    """Return deterministic registry entries for the canonical export model."""
    return [
        {
            "format": export_format,
            "status": export_format_status(export_format),
        }
        for export_format in EXPORT_FORMATS
    ]
