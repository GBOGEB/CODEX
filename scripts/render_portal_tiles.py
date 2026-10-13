"""Render the CODEX portal and dashboard metric tiles from SSOT.

Each page in PAGES holds its tiles between portal-tiles markers. Traceability
coverage is computed from the chain statuses in
ssot/traceability_dashboard.yaml. Release readiness and review-gate completion
have no measured source yet, so those tiles show the value declared in
ssot/runtime_metrics.yaml and label it as declared, with its wave and date.

Usage:
    python scripts/render_portal_tiles.py          # rewrite the pages
    python scripts/render_portal_tiles.py --check  # fail if any page is stale
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
DASHBOARDS = REPO_ROOT / "docs" / "dashboards"
RUNTIME_METRICS = REPO_ROOT / "ssot" / "runtime_metrics.yaml"
TRACEABILITY = REPO_ROOT / "ssot" / "traceability_dashboard.yaml"
GOVERNANCE = REPO_ROOT / "ssot" / "governance_dashboard.yaml"

BEGIN = "<!-- portal-tiles:begin -->"
END = "<!-- portal-tiles:end -->"
BLOCK = re.compile(re.escape(BEGIN) + ".*?" + re.escape(END), re.DOTALL)
CHAIN_REFERENCES = ("rtm_reference", "contractual_gap_reference", "clarification_reference", "answer_reference")


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _tile(label: str, metric: str, status_class: str, status: str) -> str:
    return (
        f'<article class="card"><div class="label">{html.escape(label)}</div>'
        f'<div class="metric">{html.escape(metric)}</div>'
        f'<span class="status {status_class}">{html.escape(status)}</span></article>'
    )


def _declared_note(runtime: dict) -> str:
    meta = runtime.get("runtime") or {}
    return " ".join(f"declared {meta.get('version', '')} {meta.get('generated_on', '')}, not measured".split())


def traceability_tile(trace: dict, label: str = "Traceability coverage") -> str:
    chains = trace.get("chains") or []
    total = len(chains)
    complete = sum(1 for chain in chains if chain.get("status") == "complete")
    if total == 0:
        return _tile(label, "n/a", "partial", "no chains in SSOT")
    percent = round(100 * complete / total)
    status_class = "ready" if complete == total else "partial"
    return _tile(label, f"{percent}%", status_class, f"{complete} of {total} chains complete")


def chain_count_tile(trace: dict) -> str:
    chains = trace.get("chains") or []
    ids = [str(chain.get("question_id", "?")) for chain in chains]
    return _tile("Required chains", str(len(chains)), "ready", ", ".join(ids) or "none")


def missing_references_tile(trace: dict) -> str:
    chains = trace.get("chains") or []
    missing = sum(1 for chain in chains for key in CHAIN_REFERENCES if not chain.get(key))
    status_class = "ready" if missing == 0 else "partial"
    return _tile("Missing references", str(missing), status_class, f"across {len(chains)} chains")


def _declared_percent_tile(runtime: dict, key: str, label: str) -> str:
    declared = (runtime.get("coverage_metrics") or {}).get(key)
    if declared is None:
        return _tile(label, "n/a", "partial", "not declared in SSOT")
    return _tile(label, f"{declared}%", "partial", _declared_note(runtime))


def readiness_tile(runtime: dict) -> str:
    return _declared_percent_tile(runtime, "release_readiness_percent", "Release readiness")


def review_gate_tile(runtime: dict) -> str:
    return _declared_percent_tile(runtime, "review_gate_completion_percent", "Review gate")


def models_tile(runtime: dict) -> str:
    count = (runtime.get("artifact_counts") or {}).get("ssot_models")
    return _tile("Runtime models", str(count if count is not None else "n/a"), "ready", "in SSOT")


def _count_tile(counts: dict, key: str, label: str) -> str:
    count = counts.get(key)
    return _tile(label, str(count if count is not None else "n/a"), "ready", "in SSOT")


def governance_tiles(governance: dict, runtime: dict) -> str:
    counts = governance.get("artifact_counts") or {}
    risks = runtime.get("open_risks") or {}
    risk_count = risks.get("count")
    severity = str(risks.get("highest_severity") or "unrated")
    risk_class = "ready" if risk_count == 0 else "partial"
    return (
        _count_tile(counts, "governance_controls", "Governance controls")
        + _count_tile(counts, "validation_workflows", "Validation workflows")
        + _tile("Open risks", str(risk_count if risk_count is not None else "n/a"), risk_class, f"highest {severity}")
    )


def _page_blocks(ssot: dict) -> dict[Path, str]:
    runtime, trace, governance = ssot["runtime"], ssot["trace"], ssot["governance"]
    return {
        INDEX: traceability_tile(trace) + readiness_tile(runtime) + models_tile(runtime),
        DASHBOARDS / "traceability.html": (
            traceability_tile(trace, "Overall coverage") + chain_count_tile(trace) + missing_references_tile(trace)
        ),
        DASHBOARDS / "executive.html": readiness_tile(runtime) + review_gate_tile(runtime),
        DASHBOARDS / "governance.html": governance_tiles(governance, runtime),
    }


def render(page_html: str, tiles: str, name: str = "page") -> str:
    if not BLOCK.search(page_html):
        raise SystemExit(f"{name}: portal-tiles markers not found")
    return BLOCK.sub(lambda _: BEGIN + tiles + END, page_html, count=1)


def load_ssot() -> dict:
    return {"runtime": _load(RUNTIME_METRICS), "trace": _load(TRACEABILITY), "governance": _load(GOVERNANCE)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if any page is stale")
    args = parser.parse_args(argv)

    stale = []
    for path, tiles in _page_blocks(load_ssot()).items():
        rel = path.relative_to(REPO_ROOT)
        current = path.read_text(encoding="utf-8")
        rendered = render(current, tiles, str(rel))
        if rendered == current:
            continue
        if args.check:
            stale.append(str(rel))
        else:
            path.write_text(rendered, encoding="utf-8")
            print(f"rendered {rel}")
    if stale:
        print("stale; run scripts/render_portal_tiles.py: " + ", ".join(stale))
        return 1
    if args.check:
        print("portal tiles match SSOT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
