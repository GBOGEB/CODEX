"""PDF renderer for the ABACUS Contract Governance Workbench.

Renders directly from ``workbook_payload()`` rather than converting an
already-generated docx/pptx, so this works identically on any platform CI
runs on (no external Office/LibreOffice binary required). PDF byte-level
reproducibility is not pursued -- reportlab embeds a wall-clock
``/CreationDate`` with no clean override, consistent with ``io.content_hash``
already hashing canonical *content*, not generated container bytes. Text
content extracted from the rendered PDF is what stays deterministic and
tier-stripped, matching how xlsx/docx/pptx are validated via pinned
core-properties rather than byte equality.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .io import content_hash
from .schema import GovernanceSSOT

GENERATOR = "CODEX Contract Governance Generator"


def build_pdf(payload: dict[str, object], ssot: GovernanceSSOT, path: Path) -> None:
    """Render a governance payload as a tiered PDF report."""

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        title=f"{payload['package_id']} {str(payload['tier']).upper()} Governance Snapshot",
        author=GENERATOR,
    )

    story: list[object] = [
        Paragraph(
            f"{payload['package_id']} {str(payload['tier']).upper()} Governance Snapshot",
            styles["Title"],
        ),
        Paragraph(f"Content hash (sha256): {content_hash(payload)}", styles["Normal"]),
        Spacer(1, 12),
    ]

    for sheet_payload in payload["sheets"]:  # type: ignore[index]
        # GeneratedSheet.name has no character-class restriction in schema.py,
        # unlike package_id -- escape before handing to reportlab's mini-XML Paragraph markup.
        story.append(Paragraph(escape(str(sheet_payload["name"])), styles["Heading2"]))
        columns = sheet_payload["columns"]
        rows = sheet_payload["rows"]
        table_data = [columns] + [
            [str(row.get(column, "")) for column in columns] for row in rows
        ]
        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 18))

    doc.build(story)
