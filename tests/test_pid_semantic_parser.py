from pathlib import Path

from tools.pid_semantic_parser import build_models, parse_svg


def test_parse_svg_bins_lines_and_resolved_marker_arrow(tmp_path: Path) -> None:
    svg = tmp_path / "pid.svg"
    svg.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
          <defs><marker id="arrow"><path d="M 0 0 L 10 5 L 0 10 z" /></marker></defs>
          <text id="tag_pt">PT-101 QM</text>
          <path id="line_a" d="M 10 10 L 100 10" stroke="#006ee6" fill="none" marker-end="url(#arrow)" />
          <line id="line_w" x1="10" y1="30" x2="100" y2="30" stroke="#009646" />
        </svg>""",
        encoding="utf-8",
    )

    parsed = parse_svg(svg)

    bins = {
        line["source_svg_element_id"]: line["colour_bin"] for line in parsed["lines"]
    }
    assert bins["line_a"] == "blue_A"
    assert bins["line_w"] == "green_W_coupler"
    assert parsed["arrows"][0]["inferred_direction"] == "start-to-end"
    assert parsed["arrows"][0]["arrow_tip_coordinate"] == [100.0, 10.0]
    assert parsed["tags"][0]["matches"]


def test_build_models_marks_missing_expected_inputs_unresolved() -> None:
    models = build_models(svg_paths=[Path("does-not-exist.svg")])

    assert models["line_model"]["lines"] == []
    assert models["arrow_direction_model"]["counts"] == {
        "total": 0,
        "resolved": 0,
        "unresolved": 0,
    }
    assert models["unresolved_items"][0]["type"] == "input"
