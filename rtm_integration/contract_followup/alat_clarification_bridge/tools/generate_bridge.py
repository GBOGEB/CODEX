#!/usr/bin/env python3
"""Generate bidder-facing and review artifacts from the ALaT SSOT."""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path
from typing import Any

import yaml

BRIDGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SSOT = BRIDGE_ROOT / "ssot" / "alat_questions_ssot_v0_1.yaml"
DEFAULT_OUTPUT = BRIDGE_ROOT / "build"


def load_ssot(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("SSOT root must be a mapping")
    return data


def questions(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in data.get("questions", []) if isinstance(item, dict)]


def md_list(items: list[Any]) -> str:
    return "\n".join(f"- {item}" for item in items)


def generate_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = [
        "# ALaT Clarification Bridge — Bidder Answer Roll-up",
        "",
        "> Generated from `ssot/alat_questions_ssot_v0_1.yaml`. Do not edit generated output directly.",
        "",
        "## Control notes",
        "",
    ]
    for rule in data.get("meta", {}).get("bidder_facing_rules", []):
        if "Slides" in str(rule) or "slides" in str(rule):
            continue
        lines.append(f"- {rule}")
    lines.append("")

    for question in questions(data):
        lines.extend(
            [
                f"## {question['id']} — {question['title']}",
                "",
                f"**Theme:** {question.get('theme', '')}",
                "",
                "**Bidder-facing roll-up:**",
                "",
                md_list(question.get("bidder_answer", [])),
                "",
                "**RTM links:** " + ", ".join(question.get("rtm_links", [])),
                "",
                "**OFFER actions:** " + ", ".join(question.get("offer_actions", [])),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def generate_html(data: dict[str, Any]) -> str:
    body: list[str] = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        "  <title>ALaT Clarification Bridge</title>",
        "  <style>body{font-family:Arial,sans-serif;max-width:960px;margin:2rem auto;line-height:1.5}code{background:#f3f3f3;padding:0.1rem 0.3rem}section{border-top:1px solid #ddd;padding-top:1rem}</style>",
        "</head>",
        "<body>",
        "<h1>ALaT Clarification Bridge — Bidder Answer Roll-up</h1>",
        "<p><strong>Generated from SSOT.</strong> Do not edit generated output directly.</p>",
    ]
    for question in questions(data):
        body.extend(
            [
                "<section>",
                f"<h2>{html.escape(question['id'])} — {html.escape(question['title'])}</h2>",
                f"<p><strong>Theme:</strong> {html.escape(question.get('theme', ''))}</p>",
                "<h3>Bidder-facing roll-up</h3>",
                "<ul>",
            ]
        )
        body.extend(f"<li>{html.escape(str(item))}</li>" for item in question.get("bidder_answer", []))
        body.extend(
            [
                "</ul>",
                f"<p><strong>RTM links:</strong> {html.escape(', '.join(question.get('rtm_links', [])))}</p>",
                f"<p><strong>OFFER actions:</strong> {html.escape(', '.join(question.get('offer_actions', [])))}</p>",
                "</section>",
            ]
        )
    body.extend(["</body>", "</html>"])
    return "\n".join(body) + "\n"


def generate_review_summary(data: dict[str, Any]) -> str:
    lines = ["# ALaT Clarification Bridge — Review Checklist", ""]
    for question in questions(data):
        stakeholders = question.get("stakeholders", {})
        lines.extend(
            [
                f"## {question['id']} — {question['title']}",
                "",
                f"- [ ] RTM links confirmed: {', '.join(question.get('rtm_links', []))}",
                f"- [ ] Discipline owner: {stakeholders.get('discipline_owner', '')}",
                f"- [ ] Contract owner: {stakeholders.get('contract_owner', '')}",
                f"- [ ] RTM owner: {stakeholders.get('rtm_owner', '')}",
                "- [ ] Bidder-facing text uses short bullet roll-ups.",
                "- [ ] Controlled pressure/temperature/flow values are not duplicated.",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def generate_excel_if_available(data: dict[str, Any], output_dir: Path) -> Path | None:
    try:
        from openpyxl import Workbook
    except ImportError:
        return None

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "ALaT Bridge"
    sheet.append(["Question", "Title", "Theme", "RTM links", "OFFER actions", "Stakeholders"])
    for question in questions(data):
        stakeholders = question.get("stakeholders", {})
        sheet.append(
            [
                question.get("id"),
                question.get("title"),
                question.get("theme"),
                ", ".join(question.get("rtm_links", [])),
                ", ".join(question.get("offer_actions", [])),
                "; ".join(f"{key}: {value}" for key, value in stakeholders.items()),
            ]
        )
    output_path = output_dir / "alat_clarification_bridge.xlsx"
    workbook.save(output_path)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ssot", type=Path, default=DEFAULT_SSOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        data = load_ssot(args.ssot)
    except Exception as exc:  # noqa: BLE001 - report generation-friendly error
        print(f"ERROR: failed to load SSOT: {exc}", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    markdown_path = args.out / "bidder_response.md"
    html_path = args.out / "bidder_response.html"
    review_path = args.out / "review_checklist.md"

    markdown_path.write_text(generate_markdown(data), encoding="utf-8")
    html_path.write_text(generate_html(data), encoding="utf-8")
    review_path.write_text(generate_review_summary(data), encoding="utf-8")
    excel_path = generate_excel_if_available(data, args.out)

    outputs = [markdown_path, html_path, review_path]
    if excel_path is not None:
        outputs.append(excel_path)
    print("Generated artifacts:")
    for output in outputs:
        print(f"- {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
