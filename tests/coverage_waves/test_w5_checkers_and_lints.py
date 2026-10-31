"""Coverage wave 5 (L3): stdlib checker scripts, renderer lints, report writers.

Scripts that work on the current directory run inside ``tmp_path`` fixtures,
so the real repo tree is never read for verdicts or written to.
"""
from __future__ import annotations

import csv
import json

import pytest

from renderers.lint import navigation_lint, overflow_lint, spacing_lint
from tests.coverage_waves._loader import load, run_main
from tools.traceability import trace_report

CHECK_VERSION = "scripts/check_version.py"
CHECK_GLOBS = "scripts/check_globs.py"
CHECK_MANIFEST = "scripts/check_manifest.py"
VALIDATE_YAML = "scripts/validate_yaml.py"
RENDER_GUARD = "scripts/render_guard.py"
SVG_LINKS = "scripts/check_svg_links.py"
RUNTIME_STATUS = "scripts/emit_runtime_status.py"
HEADINGS = "scripts/validate_headings.py"
BLOCKS = "scripts/export_blocks_to_csv.py"
SARIF = "tools/security/bandit_json_to_sarif.py"


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- check_version
@pytest.mark.parametrize(
    ("payload", "match"),
    [
        (None, "VERSION.json missing"),
        ("{bad", "not valid JSON"),
        ('{"version": "1"}', "missing required values: generated_at, git"),
        ('{"version": 1, "generated_at": "t", "git": "g"}', "must be strings: version"),
        ('{"version": " ", "generated_at": "t", "git": "g"}', "must be non-empty: version"),
    ],
)
def test_check_version_rejects(tmp_path, monkeypatch, payload, match):
    monkeypatch.chdir(tmp_path)
    if payload is not None:
        _write(tmp_path / "VERSION.json", payload)
    with pytest.raises(SystemExit, match=match):
        run_main(CHECK_VERSION)


def test_check_version_prints_fields(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "VERSION.json", '{"version": "2.0", "generated_at": "now", "git": "abc"}')
    run_main(CHECK_VERSION)
    assert capsys.readouterr().out.splitlines() == ["version=2.0", "generated_at=now", "git=abc"]


# ---------------------------------------------------------------- check_globs
def test_check_globs_passes_clean_tree(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "docs" / "page.html", "x")
    _write(tmp_path / "output" / "handover_final", "allowlisted")
    run_main(CHECK_GLOBS)
    assert "glob policy check passed" in capsys.readouterr().out


@pytest.mark.parametrize(
    "bad", ["final/a.txt", "Copy of x/a.txt", "my_backup/a.txt", "report_old.md", "x_latest.json"]
)
def test_check_globs_flags_ambiguous_paths(tmp_path, monkeypatch, bad):
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / bad, "x")
    with pytest.raises(SystemExit, match="forbidden ambiguity paths found"):
        run_main(CHECK_GLOBS)


# ---------------------------------------------------------------- check_manifest
REQUIRED_PAGES = ["docs/index.html", "docs/dashboard.html", "docs/plots/index.html"]


def _manifest_tree(tmp_path, manifest, create_pages=True):
    if manifest is not None:
        _write(tmp_path / "MANIFEST.json", json.dumps(manifest))
    if create_pages:
        for page in REQUIRED_PAGES:
            _write(tmp_path / page, "x")


@pytest.mark.parametrize(
    ("manifest", "pages", "match"),
    [
        (None, True, "MANIFEST.json missing"),
        ({"canonical_entrypoint": "x"}, True, "canonical_entrypoint must be"),
        ({"canonical_entrypoint": "docs/index.html", "published_pages": []}, True, "non-empty list"),
        ({"canonical_entrypoint": "docs/index.html", "published_pages": ["site/x.html"]}, True, "invalid entries"),
        ({"canonical_entrypoint": "docs/index.html", "published_pages": ["docs/index.html"]}, True,
         "missing required entrypoints"),
        ({"canonical_entrypoint": "docs/index.html", "published_pages": REQUIRED_PAGES + ["docs/index.html"]}, True,
         "duplicates"),
        ({"canonical_entrypoint": "docs/index.html", "published_pages": REQUIRED_PAGES}, False, "required path missing"),
    ],
)
def test_check_manifest_rejects(tmp_path, monkeypatch, manifest, pages, match):
    monkeypatch.chdir(tmp_path)
    _manifest_tree(tmp_path, manifest, pages)
    with pytest.raises(SystemExit, match=match):
        run_main(CHECK_MANIFEST)


def test_check_manifest_passes(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _manifest_tree(tmp_path, {"canonical_entrypoint": "docs/index.html", "published_pages": REQUIRED_PAGES})
    run_main(CHECK_MANIFEST)
    assert "manifest check passed" in capsys.readouterr().out


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: scripts/check_manifest.py joins invalid published_pages entries as strings, "
        "so a non-string entry (e.g. 5) crashes with TypeError instead of the intended SystemExit report"
    ),
)
def test_check_manifest_non_string_entry_is_reported(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _manifest_tree(tmp_path, {"canonical_entrypoint": "docs/index.html", "published_pages": REQUIRED_PAGES + [5]})
    with pytest.raises(SystemExit, match="invalid entries"):
        run_main(CHECK_MANIFEST)


# ---------------------------------------------------------------- validate_yaml
def test_validate_yaml_ok_and_fail(tmp_path, capsys):
    m = load(VALIDATE_YAML)
    good = _write(tmp_path / "g.yml", "a: 1\n")
    bad = _write(tmp_path / "b.yml", "a: [1\n")
    assert m.main([str(good)]) == 0
    assert m.main([str(good), str(bad), str(tmp_path / "missing.yml")]) == 1
    out = capsys.readouterr().out
    assert out.count("OK:") == 2 and out.count("FAIL:") == 2


def test_validate_yaml_default_targets_exist():
    m = load(VALIDATE_YAML)
    assert m.main([]) == 0
    assert all(t.is_file() for t in m.TARGETS)


# ---------------------------------------------------------------- render_guard
def test_render_guard_reports_missing_and_invalid(tmp_path, monkeypatch, capsys):
    m = load(RENDER_GUARD)
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "governance" / "runtime_governance.yml", "a: [1\n")
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "invalid YAML in" in out and "missing governance manifest" in out and "missing docs file" in out


def test_render_guard_ok(tmp_path, monkeypatch, capsys):
    m = load(RENDER_GUARD)
    monkeypatch.chdir(tmp_path)
    for p in m.REQUIRED_GOVERNANCE:
        _write(tmp_path / p, "a: 1\n")
    for p in m.REQUIRED_DOCS:
        _write(tmp_path / p, "# doc\n")
    assert m.main() == 0
    assert "render guard: OK" in capsys.readouterr().out


# ---------------------------------------------------------------- check_svg_links
def test_svg_refs_parser(tmp_path):
    m = load(SVG_LINKS)
    text = ('<img src="a.svg"> <object data=\'b.svg#frag\'></object> [x](c.svg?v=1) ![y](d.svg) '
            '<img src="https://e.com/e.svg"> [z](//cdn/f.svg)')
    names = sorted(p.name for p in m._local_svg_refs(text, tmp_path))
    # Refs carrying a #fragment or ?query never match the patterns (see PD-L3-005).
    assert names == ["a.svg", "d.svg"]


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: scripts/check_svg_links.py strips #fragment/?query from matches, but its regexes "
        "require the value to end in '.svg', so refs like 'icon.svg#id' are never matched and broken ones pass"
    ),
)
def test_svg_links_broken_ref_with_fragment_is_reported(tmp_path, monkeypatch):
    m = load(SVG_LINKS)
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "docs" / "p.html", '<img src="missing.svg#icon">')
    assert m.main() == 1


def test_svg_links_check(tmp_path, monkeypatch, capsys):
    m = load(SVG_LINKS)
    monkeypatch.chdir(tmp_path)
    assert m.main() == 0
    assert "skipping" in capsys.readouterr().out
    _write(tmp_path / "docs" / "ok.svg", "<svg/>")
    _write(tmp_path / "docs" / "page.md", "![a](ok.svg)")
    assert m.main() == 0
    _write(tmp_path / "docs" / "sub" / "bad.html", '<img src="../missing.svg">')
    assert m.main() == 1
    assert "broken SVG reference" in capsys.readouterr().out


def test_svg_links_outside_repo_path_is_reported_absolute(tmp_path, monkeypatch, capsys):
    m = load(SVG_LINKS)
    work = tmp_path / "repo"
    work.mkdir()
    monkeypatch.chdir(work)
    _write(work / "docs" / "p.md", "![a](../../outside.svg)")
    assert m.main() == 1
    assert "outside.svg" in capsys.readouterr().out


# ---------------------------------------------------------------- emit_runtime_status
@pytest.mark.parametrize(
    ("dep", "real", "status"),
    [(95, 60, "passed"), (89.9, 60, "failed"), (95, 49, "failed")],
)
def test_build_runtime_status_gate(dep, real, status):
    m = load(RUNTIME_STATUS)
    res = m.build_runtime_status({"completion_percent": dep}, {"average_actual": real})
    assert res["status"] == status
    assert res["release_gate"]["deployment_passed"] is (dep >= 90)
    assert res["release_gate"]["reality_passed"] is (real >= 50)


def test_build_runtime_status_defaults():
    m = load(RUNTIME_STATUS)
    res = m.build_runtime_status({}, {})
    assert res["release_gate"]["deployment_score"] == 0.0 and res["status"] == "failed"


def test_emit_runtime_status_main_writes_report(tmp_path):
    m = load(RUNTIME_STATUS)
    dep = _write(tmp_path / "d.json", '{"completion_percent": 100}')
    real = _write(tmp_path / "r.json", '{"average_actual": 70}')
    out = tmp_path / "reports" / "s.json"
    assert m.main(["--deployment-json", str(dep), "--reality-json", str(real), "--out", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "passed" and data["deployment"] == {"completion_percent": 100}


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: scripts/emit_runtime_status.py prints a non-ASCII arrow (U+2192), which raises "
        "UnicodeEncodeError on the cp1252 Windows console (CODEX CLAUDE.md: keep CLI prints ASCII)"
    ),
)
def test_emit_runtime_status_output_is_cp1252_safe(tmp_path, capsys):
    m = load(RUNTIME_STATUS)
    dep = _write(tmp_path / "d.json", "{}")
    real = _write(tmp_path / "r.json", "{}")
    m.main(["--deployment-json", str(dep), "--reality-json", str(real), "--out", str(tmp_path / "o.json")])
    capsys.readouterr().out.encode("cp1252")


# ---------------------------------------------------------------- validate_headings
def _heading(hid, level=1, **extra):
    base = {"heading_id": hid, "title": hid, "level": level, "word_style": f"Heading {level}",
            "numbering": {"mode": "generated_by_word", "list_template": "L"}, "sort_order": 1}
    base.update(extra)
    return base


def test_validate_heading_happy_path():
    m = load(HEADINGS)
    assert m.validate_heading(_heading("H1"), 0) == []


def test_validate_heading_all_errors():
    m = load(HEADINGS)
    errs = m.validate_heading({"level": "one", "numbering": "x", "children": "c"}, 3)
    joined = " | ".join(errs)
    assert "heading[3]: missing required fields" in joined
    assert "level must be an integer" in joined
    assert "numbering must be a mapping" in joined
    assert "children must be a list" in joined
    errs = m.validate_heading(_heading("H", 2, word_style="Heading 1", numbering={"mode": "manual"}), 0)
    assert any("should be 'Heading 2'" in e for e in errs)
    assert any("numbering.mode" in e for e in errs) and any("list_template" in e for e in errs)


def test_validate_file_cross_references(tmp_path):
    import yaml as _yaml
    m = load(HEADINGS)
    doc = {"headings": [
        _heading("A", children=["B", "Z"]),
        _heading("B", 2, parent_id="A"),
        _heading("C", parent_id="NOPE"),
        _heading("A"),
        "junk",
    ]}
    count, errors = m.validate_file(_write(tmp_path / "h.yaml", _yaml.safe_dump(doc)))
    assert count == 5
    assert "A: child heading 'Z' does not exist" in errors
    assert "C: parent_id 'NOPE' does not exist" in errors
    assert "duplicate heading_id: A" in errors
    assert "heading[4] must be a mapping" in errors


def test_validate_file_root_errors(tmp_path):
    m = load(HEADINGS)
    assert m.validate_file(_write(tmp_path / "a.yaml", "headings: 1\n")) == (0, ["root key 'headings' must be a list"])
    with pytest.raises(ValueError, match="YAML mapping"):
        m.load_yaml(_write(tmp_path / "b.yaml", "- 1\n"))
    assert m.load_yaml(_write(tmp_path / "c.yaml", "")) == {}


def test_validate_headings_main(tmp_path, monkeypatch, capsys):
    import yaml as _yaml
    m = load(HEADINGS)
    good = _write(tmp_path / "g.yaml", _yaml.safe_dump({"headings": [_heading("A")]}))
    bad = _write(tmp_path / "b.yaml", _yaml.safe_dump({"headings": [{"heading_id": "X"}]}))
    monkeypatch.setattr("sys.argv", ["v", str(good)])
    assert m.main() == 0
    monkeypatch.setattr("sys.argv", ["v", str(bad)])
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "PASS:" in out and "FAIL:" in out


# ---------------------------------------------------------------- export_blocks_to_csv
def test_flatten_block_full_and_empty():
    m = load(BLOCKS)
    row = m.flatten_block({
        "block_id": "B1", "section": {"heading_id": "H", "heading_level": 2, "word_style": "Heading 2"},
        "lineage": {"created_from": "p", "source_prompt_id": "P1"}, "render": {"markdown": True},
        "dependencies": {"requires": ["X", "Y"]}, "tags": ["a", "b"], "target_runtime": "html",
        "content": "line1\nline2 " + "z" * 300,
    })
    assert row["dependencies"] == "X, Y" and row["tags"] == "a, b" and row["target_runtime"] == "html"
    assert row["content_preview"].startswith("line1 line2") and len(row["content_preview"]) == 240
    empty = m.flatten_block({})
    assert set(empty) == set(m.COLUMNS) and empty["tags"] == "" and empty["content_preview"] == ""


def test_export_csv_and_main(tmp_path, monkeypatch, capsys):
    m = load(BLOCKS)
    src = _write(tmp_path / "b.yaml", "blocks:\n  - {block_id: B1, title: T}\n  - {block_id: B2}\n")
    out = tmp_path / "out" / "r.csv"
    m.export_csv(src, out)
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert [r["block_id"] for r in rows] == ["B1", "B2"] and rows[0]["title"] == "T"
    monkeypatch.setattr("sys.argv", ["x", str(src), str(tmp_path / "o2.csv")])
    assert m.main() == 0 and "Wrote block register" in capsys.readouterr().out
    with pytest.raises(ValueError, match="must be a list"):
        m.load_blocks(_write(tmp_path / "bad.yaml", "blocks: 3\n"))
    assert m.load_blocks(_write(tmp_path / "e.yaml", "")) == []


# ---------------------------------------------------------------- bandit sarif
def test_bandit_convert_maps_findings():
    m = load(SARIF)
    sarif = m.convert({"results": [
        {"test_id": "B602", "test_name": "subprocess", "issue_text": "shell", "issue_severity": "high",
         "issue_confidence": "medium", "more_info": "https://x", "filename": "a\\b.py", "line_number": "7"},
        {"test_id": "B101", "issue_severity": "LOW", "filename": "c.py", "line_number": "x"},
        {"issue_severity": "WEIRD"},
    ]})
    run = sarif["runs"][0]
    assert [r["id"] for r in run["tool"]["driver"]["rules"]] == ["B101", "B602", "BANDIT"]
    assert run["tool"]["driver"]["rules"][1]["helpUri"] == "https://x"
    r0, r1, r2 = run["results"]
    assert r0["level"] == "error" and r0["message"]["text"] == "shell (confidence: MEDIUM)"
    loc = r0["locations"][0]["physicalLocation"]
    assert loc["artifactLocation"]["uri"] == "a/b.py" and loc["region"]["startLine"] == 7
    assert r1["level"] == "note" and r1["locations"][0]["physicalLocation"]["region"]["startLine"] == 1
    assert r2["level"] == "warning" and "locations" not in r2


def test_bandit_main_roundtrip(tmp_path, monkeypatch, capsys):
    m = load(SARIF)
    src = _write(tmp_path / "b.json", json.dumps({"results": [{"test_id": "B1", "filename": "f.py"}]}))
    out = tmp_path / "o.sarif"
    monkeypatch.setattr("sys.argv", ["x", str(src), str(out)])
    assert m.main() == 0
    assert json.loads(out.read_text(encoding="utf-8"))["version"] == "2.1.0"
    assert "Converted 1 Bandit finding(s)" in capsys.readouterr().out


# ---------------------------------------------------------------- renderer lints
def test_overflow_thresholds():
    assert overflow_lint.validate_title_length("x" * 72) == []
    assert overflow_lint.validate_title_length("x" * 73)[0].component == "title-overflow"
    assert overflow_lint.validate_card_body_lines(18) == []
    assert overflow_lint.validate_card_body_lines(19)[0].component == "card-overflow"


@pytest.mark.parametrize(
    ("mod", "argv", "code"),
    [
        (overflow_lint, [], 0),
        (overflow_lint, ["--title", "x" * 100, "--card-body-lines", "30"], 1),
        (spacing_lint, [], 0),
        (spacing_lint, ["--card-padding", "4", "--section-spacing", "2"], 1),
    ],
)
def test_lint_mains(mod, argv, code, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["lint", *argv])
    assert mod.main() == code
    captured = capsys.readouterr()
    if code:
        assert captured.err.count("[warning]") == 2
    else:
        assert "checks passed" in captured.out


def test_spacing_thresholds():
    assert spacing_lint.validate_card_padding(12) == []
    assert spacing_lint.validate_card_padding(11)[0].component == "card-padding"
    assert spacing_lint.validate_section_spacing(16) == []
    assert spacing_lint.validate_section_spacing(15)[0].component == "section-spacing"


def test_navigation_boundaries(tmp_path):
    docs = tmp_path / "docs"
    _write(docs / "index.html", '<a href="sub/p.html#x">a</a><img src="../outputs/c.png">'
                                '<a href="https://e.com">e</a><a href="#top">t</a><a href=" ">b</a>'
                                '<a href="../secret.txt">s</a><link href="../outputs">')
    _write(docs / "sub" / "p.html", '<script src="../../../etc/x.js"></script><a href="mailto:a@b">m</a>')
    issues = navigation_lint.validate_docs_link_boundaries(docs)
    links = sorted(i.message.split("'")[1] for i in issues)
    assert links == ["../../../etc/x.js", "../secret.txt"]
    assert all(i.severity == "error" for i in issues)
    assert navigation_lint.validate_docs_link_boundaries(tmp_path / "none") == []
    assert navigation_lint.validate_navigation_ids() == []


def test_navigation_main(monkeypatch, capsys):
    monkeypatch.setattr(navigation_lint, "validate_docs_link_boundaries", list)
    assert navigation_lint.main() == 0
    issue = navigation_lint.NavigationIssue("c", "error", "bad")
    monkeypatch.setattr(navigation_lint, "validate_docs_link_boundaries", lambda: [issue])
    assert navigation_lint.main() == 1
    assert "[error] c: bad" in capsys.readouterr().out


# ---------------------------------------------------------------- trace_report
def _report(errors):
    return {"status": "pass" if not errors else "fail", "checked_at": "t", "node_count": 2,
            "error_count": len(errors), "errors": errors,
            "nodes": [{"stage": "Requirement", "title": "R", "id": "R1", "parent": None, "source_path": "a.md"},
                      {"stage": "Review", "title": "V", "id": "V1", "parent": "R1"}]}


def test_trace_report_pass(tmp_path):
    paths = trace_report.generate_reports(_report([]), tmp_path / "j" / "t.json", tmp_path / "m" / "t.md",
                                          tmp_path / "c" / "t.csv")
    md = paths["markdown"].read_text(encoding="utf-8")
    assert "**PASS**" in md and "| Review | V | `V1` | `R1` |" in md and "No dependency trace" in md
    rows = list(csv.DictReader(paths["csv"].open(encoding="utf-8")))
    assert rows[0]["source_path"] == "a.md" and rows[0]["parent"] == "" and rows[1]["source_path"] == ""
    assert json.loads(paths["json"].read_text(encoding="utf-8"))["node_count"] == 2


def test_trace_report_fail_lists_errors(tmp_path):
    rep = _report([{"code": "E1", "message": "orphan", "node_id": "V1"}, {"code": "E2", "message": "x"}])
    paths = trace_report.generate_reports(rep, tmp_path / "t.json", tmp_path / "t.md", tmp_path / "t.csv")
    md = paths["markdown"].read_text(encoding="utf-8")
    assert "**FAIL**" in md and "- `E1` (`V1`): orphan" in md and "- `E2`: x" in md
