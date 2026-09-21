from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/static.yml"


def test_static_candidate_excludes_git_checkout_metadata():
    doc = YAML(typ="safe").load(WORKFLOW.read_text(encoding="utf-8"))
    steps = doc["jobs"]["package"]["steps"]
    checkout = next(step for step in steps if str(step.get("uses", "")).startswith("actions/checkout@"))
    upload = next(step for step in steps if str(step.get("uses", "")).startswith("actions/upload-artifact@"))

    assert checkout.get("with", {}).get("persist-credentials") is False
    scope = str(upload["with"]["path"])
    assert "!.git" in scope
    assert "!.git/**" in scope
    assert upload["with"]["include-hidden-files"] is True
