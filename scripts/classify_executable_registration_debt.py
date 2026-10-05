from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "mission_control" / "mycelium" / "executable_value_report.json"
OUT = ROOT / "mission_control" / "mycelium" / "registration_debt_classification.json"
WORKFLOWS = ROOT / ".github" / "workflows"
TESTS = ROOT / "tests"

CLASSIFICATIONS = {
    "TESTED_ORPHAN",
    "LIBRARY_REFERENCE_ONLY",
    "PIPELINE_INTEGRATION_CANDIDATE",
    "ARCHIVE_REMOVE_CANDIDATE",
    "UNRESOLVED_REGISTRATION_DEBT",
}


def _test_names() -> set[str]:
    names: set[str] = set()
    for path in TESTS.rglob("test_*.py"):
        names.add(path.stem.removeprefix("test_"))
    return names


def _workflow_text() -> str:
    chunks = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def classify(report_path: Path = REPORT) -> dict[str, object]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    test_names = _test_names()
    workflow_text = _workflow_text()
    rows = []
    for asset in report["inventory"]["unregistered_assets"]:
        path = Path(asset)
        stem = path.stem
        tested = stem in test_names or f"test_{stem}.py" in workflow_text
        workflow_consumer = asset in workflow_text
        if asset.startswith("tests/"):
            classification = "LIBRARY_REFERENCE_ONLY"
        elif asset.startswith(".github/workflows/"):
            classification = "PIPELINE_INTEGRATION_CANDIDATE"
        elif tested and not workflow_consumer:
            classification = "TESTED_ORPHAN"
        elif workflow_consumer:
            classification = "PIPELINE_INTEGRATION_CANDIDATE"
        else:
            classification = "UNRESOLVED_REGISTRATION_DEBT"
        rows.append({
            "asset": asset,
            "test_evidence": tested,
            "operational_edge": workflow_consumer,
            "downstream_consumer": "github_actions" if workflow_consumer else None,
            "execution_surface": "github_actions" if workflow_consumer else None,
            "outcome_value_evidence": None,
            "classification": classification,
        })
    counts = {name: sum(r["classification"] == name for r in rows) for name in sorted(CLASSIFICATIONS)}
    return {
        "schema_version": "0.1",
        "authority_class": "DERIVED_CENSUS",
        "authority_transfer": False,
        "source_report": str(REPORT.relative_to(ROOT)),
        "candidate_count": len(rows),
        "classification_counts": counts,
        "candidates": rows,
    }


def main() -> int:
    payload = classify()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["classification_counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
