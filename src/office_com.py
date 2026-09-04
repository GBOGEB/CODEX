"""Windows-only Office COM automation.

This module must import cleanly on every platform -- only calling one of its
functions on a non-Windows platform, or on Windows without Word installed,
raises. It intentionally stays a single narrow conversion helper, not a
general COM automation framework: build out further surface only when a
concrete need arises, mirroring the scope discipline of src/confluence_client.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Word's wdExportFormatPDF enum value (Microsoft Word object model).
_WD_EXPORT_FORMAT_PDF = 17


class OfficeComError(RuntimeError):
    """Raised when Office COM automation is unavailable or a conversion fails."""


def _require_windows() -> None:
    if sys.platform != "win32":
        raise OfficeComError(
            "Office COM automation requires Windows with Microsoft Office "
            f"installed; current platform: {sys.platform!r}"
        )


def convert_document_to_pdf(input_path: Path, output_path: Path) -> Path:
    """Convert a Word document to PDF via a local Word installation.

    This is the optional, non-default, higher-fidelity alternative to
    ``codex.contract_governance.pdf_builder``'s reportlab rendering -- call
    it manually when Word-accurate PDF output is needed. It is not wired
    into ``build_artifacts`` or any CLI, since it only works on a Windows
    machine with Microsoft Word installed and would fail confusingly if
    selected from Linux CI.
    """

    _require_windows()

    try:
        import win32com.client  # noqa: PLC0415 -- intentionally lazy, see module docstring
    except ImportError as exc:  # pragma: no cover - exercised only off-Windows
        raise OfficeComError(
            "pywin32 is not installed; install the 'windows' extra "
            "(pip install -e .[windows]) on a Windows machine with Word."
        ) from exc

    resolved_input = Path(input_path).resolve()
    resolved_output = Path(output_path).resolve()

    try:
        word = win32com.client.Dispatch("Word.Application")
    except Exception as exc:  # noqa: BLE001 - COM raises opaque pywintypes.com_error
        raise OfficeComError(
            "Could not start Word via COM automation; is Microsoft Word installed "
            "and registered?"
        ) from exc

    try:
        document = word.Documents.Open(str(resolved_input))
        try:
            document.ExportAsFixedFormat(str(resolved_output), _WD_EXPORT_FORMAT_PDF)
        finally:
            document.Close(False)
    finally:
        word.Quit()

    return resolved_output
