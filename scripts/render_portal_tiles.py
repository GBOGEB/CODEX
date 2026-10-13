"""Render the CODEX portal metric tiles in docs/index.html from SSOT.

Traceability coverage is computed from the chain statuses in
ssot/traceability_dashboard.yaml. Release readiness has no measured source
yet, so the tile shows the value declared in ssot/runtime_metrics.yaml and
labels it as declared, with its date.

Usage:
    python scripts/render_portal_tiles.py          # rewrite docs/index.html
    python scripts/render_portal_tiles.py --check  # fail if it is stale
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX = REPO_ROOT / "docs" / "index.html"
RUNTIME_METRICS = REPO_ROOT / "ssot" / "runtime_metrics.yaml"
TRACEABILITY = REPO_ROOT / "ssot" / "traceability_dashboard.yaml"

BEGIN = "<!-- portal-tiles:begin -->"
END = "<!-- portal-tiles:end -->"
BLOCK = re.compile(re.escape(BEGIN) + ".*?" + re.escape(END), re.DOTALL)


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _tile(label: str, metric: str, status_class: str, status: str) -> str:
    return (
        f'<article class="card"><div class="label">{html.escape(label)}</div>'
        f'<div class="metric">{html.escape(metric)}</div>'
        f'<span class="status {status_class}">{html.escape(status)}</span></article>'
    )


def traceability_tile(trace: dict) -> str:
    chains = trace.get("chains") or []
    total = len(chains)
    complete = sum(1 for chain in chains if chain.get("status") == "complete")
    if total == 0:
        return _tile("Traceability coverage", "n/a", "partial", "no chains in SSOT")
    percent = round(100 * complete / total)
    status_class = "ready" if complete == total else "partial"
    return _tile(
        "Traceability coverage",
        f"{percent}%",
        status_class,
        f"{complete} of {total} chains complete",
    )


def readiness_tile(runtime: dict) -> str:
    declared = (runtime.get("coverage_metrics") or {}).get("release_readiness_percent")
    meta = runtime.get("runtime") or {}
    if declared is None:
        return _tile("Release readiness", "n/a", "partial", "not declared in SSOT")
    note = f"declared {meta.get('version', '')} {meta.get('generated_on', '')}, not measured"
    return _tile("Release readiness", f"{declared}%", "partial", " ".join(note.split()))


def models_tile(runtime: dict) -> str:
    count = (runtime.get("artifact_counts") or {}).get("ssot_models")
    return _tile("Runtime models", str(count if count is not None else "n/a"), "ready", "in SSOT")


def render_block(runtime: dict, trace: dict) -> str:
    return BEGIN + traceability_tile(trace) + readiness_tile(runtime) + models_tile(runtime) + END


def render(index_html: str, runtime: dict, trace: dict) -> str:
    if not BLOCK.search(index_html):
        raise SystemExit(f"{INDEX}: portal-tiles markers not found")
    return BLOCK.sub(lambda _: render_block(runtime, trace), index_html, count=1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if docs/index.html is stale")
    args = parser.parse_args(argv)

    current = INDEX.read_text(encoding="utf-8")
    rendered = render(current, _load(RUNTIME_METRICS), _load(TRACEABILITY))
    if args.check:
        if rendered != current:
            print(f"{INDEX.relative_to(REPO_ROOT)} is stale; run scripts/render_portal_tiles.py")
            return 1
        print("portal tiles match SSOT")
        return 0
    if rendered != current:
        INDEX.write_text(rendered, encoding="utf-8")
    print(f"rendered {INDEX.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
