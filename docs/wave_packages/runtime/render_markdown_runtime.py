from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_TEMPLATE = """# Runtime Status\n\nGenerated: `{timestamp}`\n\n## Runtime Summary\n\n| Domain | Status | Score |\n|---|---|---:|\n{rows}\n\n## Continuity\n\n- topology persistence active\n- Pages continuity scaffold active\n- synchronization runtime active\n- federation runtime executable\n"""


def render_markdown(runtime: dict) -> str:
    rows = []
    for name, value in runtime.items():
        if isinstance(value, dict) and "score" in value:
            rows.append(f"| {name} | {value.get('status', 'ok')} | {value['score']} |")

    return RUNTIME_TEMPLATE.format(
        timestamp=datetime.now(timezone.utc).isoformat(),
        rows="\n".join(rows),
    )


def load_runtime(path: str | None):
    if path is None:
        return {
            "bridge": {"status": "operational", "score": 88},
            "synchronization": {"status": "operational", "score": 91},
            "covariance": {"status": "emerging", "score": 68},
            "pages": {"status": "medium-high", "score": 82},
        }

    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Render markdown runtime reports")
    parser.add_argument("--input")
    parser.add_argument("--out", default="docs/wave_packages/runtime/out/runtime_status.md")
    args = parser.parse_args()

    markdown = render_markdown(load_runtime(args.input))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")

    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
