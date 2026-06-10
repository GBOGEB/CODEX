"""Render ABACUS debug spine JSONL runtime evidence into Markdown."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

REQUIRED_EVENT_NAMES = [
    "session.created",
    "dap.initialized",
    "breakpoint.bound",
    "execution.paused",
    "render.snapshot",
    "session.closed",
]

REQUIRED_EVENT_FIELDS = [
    "session_id",
    "track_id",
    "adapter",
    "backbone",
    "target",
    "github",
    "event",
    "render",
]


def load_trace_jsonl(trace_path: Path) -> list[dict]:
    """Load and validate a debug spine JSONL trace."""
    events: list[dict] = []
    for line_number, raw_line in enumerate(trace_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        event = json.loads(raw_line)
        missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
        if missing:
            raise ValueError(f"Line {line_number} missing required fields: {', '.join(missing)}")
        event_name = event["event"].get("name")
        if event_name not in REQUIRED_EVENT_NAMES:
            raise ValueError(f"Line {line_number} has unexpected event name: {event_name}")
        for nested_field in ("name", "timestamp", "evidence_ref"):
            if nested_field not in event["event"]:
                raise ValueError(f"Line {line_number} event missing {nested_field}")
        events.append(event)

    observed = [event["event"]["name"] for event in events]
    missing_events = [name for name in REQUIRED_EVENT_NAMES if name not in observed]
    if missing_events:
        raise ValueError(f"Trace missing required events: {', '.join(missing_events)}")
    return events


def render_markdown(events: Iterable[dict]) -> str:
    """Render trace events as an ABACUS evidence Markdown document."""
    event_list = list(events)
    first = event_list[0]
    lines = [
        "# ABACUS Debug Spine Runtime Evidence",
        "",
        f"- Track: `{first['track_id']}`",
        f"- Session: `{first['session_id']}`",
        f"- Adapter: `{first['adapter']['name']}` / `{first['adapter']['protocol']}`",
        f"- Backbone: `{first['backbone']['language']}`",
        f"- Target: `{first['target']['language']}`",
        f"- GitHub Repository: `{first['github']['repository']}`",
        "",
        "## Event Trace",
        "",
        "| Event | Timestamp | Evidence Reference | Render Status |",
        "|---|---|---|---|",
    ]
    for event in event_list:
        lines.append(
            "| {name} | {timestamp} | `{evidence_ref}` | {render_status} |".format(
                name=event["event"]["name"],
                timestamp=event["event"]["timestamp"],
                evidence_ref=event["event"]["evidence_ref"],
                render_status=event["render"]["status"],
            )
        )
    lines.extend([
        "",
        "## Governance Disposition",
        "",
        "Runtime evidence is renderable and contains all required ABACUS debug spine events.",
    ])
    return "\n".join(lines) + "\n"


def render_trace_file(trace_path: Path, output_path: Path) -> Path:
    """Render a JSONL trace file into Markdown evidence."""
    events = load_trace_jsonl(trace_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(events), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-jsonl", required=True, type=Path)
    parser.add_argument("--output-md", required=True, type=Path)
    args = parser.parse_args()
    rendered_path = render_trace_file(args.trace_jsonl, args.output_md)
    print(f"ABACUS debug spine evidence rendered: {rendered_path}")


if __name__ == "__main__":
    main()
