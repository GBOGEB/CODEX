"""tools/qa/html_qa.py: page discovery, link resolution, baseline comparison and the deploy-generated list."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _qa():
    spec = importlib.util.spec_from_file_location("html_qa", REPO_ROOT / "tools/qa/html_qa.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_published_pages_cover_the_manifest_and_exist():
    qa = _qa()
    pages = qa.published_pages()
    assert "index.html" in pages and "gistau/index.html" in pages
    assert all((qa.DOCS / p).is_file() for p in pages)


def test_link_resolution():
    qa = _qa()
    assert qa._link_target_exists("gistau/index.html", "../gistau-ch3/index.html")
    assert qa._link_target_exists("gistau/index.html", "../gistau-ch15/")  # directory with index.html
    assert qa._link_target_exists("gistau/index.html", "https://example.org/x")
    assert qa._link_target_exists("gistau/index.html", "#chapters")
    assert not qa._link_target_exists("gistau/index.html", "../no-such-page.html")


def test_baseline_comparison_reports_new_and_fixed():
    qa = _qa()
    results = [
        {"page": "a.html", "findings": [{"kind": "no_title", "detail": "empty <title>"}, {"kind": "no_lang", "detail": "x"}]},
        {"page": "b.html", "findings": []},
    ]
    new, fixed = qa.compare(results, {"b.html": ["broken_link: x.html"]})
    assert new == {"a.html": ["no_title: empty <title>"]}  # WARN kinds never gate
    assert fixed == {"b.html": ["broken_link: x.html"]}


def test_deploy_generated_files_are_still_produced_by_the_pages_build():
    qa = _qa()
    pages_yml = (REPO_ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    for path, producer in qa.DEPLOY_GENERATED.items():
        assert producer in pages_yml, f"{path}: producer {producer} no longer in pages.yml"


def test_baseline_only_lists_published_pages():
    qa = _qa()
    baseline = json.loads(qa.BASELINE.read_text(encoding="utf-8"))["errors"]
    assert set(baseline) <= set(qa.published_pages())
    assert all(k.split(":", 1)[0] in qa.ERROR_KINDS for keys in baseline.values() for k in keys)
