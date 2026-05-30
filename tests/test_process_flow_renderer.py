"""Tests for renderers/process_flow_renderer.py (W003.2)."""
from __future__ import annotations

import pytest

from renderers.process_flow_renderer import (
    render_process_flow,
    lineage_metadata,
    LINEAGE,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

VALID_SCHEMA = {
    "type": "process_flow",
    "title": "Example Process",
    "nodes": [
        {"id": "A", "label": "Compressor"},
        {"id": "B", "label": "Heat Exchanger"},
        {"id": "C", "label": "Cold Box"},
    ],
    "edges": [
        {"from": "A", "to": "B"},
        {"from": "B", "to": "C"},
    ],
}


# ---------------------------------------------------------------------------
# SVG generation
# ---------------------------------------------------------------------------

class TestSVGGeneration:
    def test_returns_string(self):
        result = render_process_flow(VALID_SCHEMA)
        assert isinstance(result, str)

    def test_output_starts_with_svg_tag(self):
        result = render_process_flow(VALID_SCHEMA)
        assert result.strip().startswith("<svg")

    def test_output_closes_svg_tag(self):
        result = render_process_flow(VALID_SCHEMA)
        assert "</svg>" in result

    def test_xmlns_present(self):
        result = render_process_flow(VALID_SCHEMA)
        assert "http://www.w3.org/2000/svg" in result


# ---------------------------------------------------------------------------
# Node and edge rendering
# ---------------------------------------------------------------------------

class TestNodeAndEdgeRendering:
    def test_node_labels_in_output(self):
        result = render_process_flow(VALID_SCHEMA)
        assert "Compressor" in result
        assert "Heat Exchanger" in result
        assert "Cold Box" in result

    def test_rect_elements_for_nodes(self):
        result = render_process_flow(VALID_SCHEMA)
        assert result.count("<rect") == 3

    def test_edges_produce_line_elements(self):
        result = render_process_flow(VALID_SCHEMA)
        assert result.count("<line") == 2

    def test_title_in_output(self):
        result = render_process_flow(VALID_SCHEMA)
        assert "Example Process" in result

    def test_no_edges_schema(self):
        schema = {
            "type": "process_flow",
            "title": "Solo",
            "nodes": [{"id": "X", "label": "Only Node"}],
            "edges": [],
        }
        result = render_process_flow(schema)
        assert "Only Node" in result
        assert "<line" not in result


# ---------------------------------------------------------------------------
# Empty graph handling
# ---------------------------------------------------------------------------

class TestEmptyGraphHandling:
    def test_empty_nodes_returns_svg(self):
        schema = {
            "type": "process_flow",
            "title": "",
            "nodes": [],
            "edges": [],
        }
        result = render_process_flow(schema)
        assert result.startswith("<svg")
        assert "</svg>" in result

    def test_empty_graph_contains_placeholder(self):
        schema = {
            "type": "process_flow",
            "title": "",
            "nodes": [],
            "edges": [],
        }
        result = render_process_flow(schema)
        assert "empty graph" in result


# ---------------------------------------------------------------------------
# Invalid schema rejection
# ---------------------------------------------------------------------------

class TestInvalidSchemaRejection:
    def test_wrong_type_raises(self):
        with pytest.raises(ValueError, match="process_flow"):
            render_process_flow({"type": "sankey", "nodes": [], "edges": []})

    def test_missing_type_raises(self):
        with pytest.raises(ValueError):
            render_process_flow({"nodes": [], "edges": []})

    def test_non_dict_raises(self):
        with pytest.raises(ValueError):
            render_process_flow("not a dict")  # type: ignore[arg-type]

    def test_missing_nodes_key_raises(self):
        with pytest.raises(ValueError, match="nodes"):
            render_process_flow({"type": "process_flow"})

    def test_node_missing_id_raises(self):
        with pytest.raises(ValueError):
            render_process_flow(
                {
                    "type": "process_flow",
                    "nodes": [{"label": "No ID"}],
                    "edges": [],
                }
            )

    def test_node_missing_label_raises(self):
        with pytest.raises(ValueError):
            render_process_flow(
                {
                    "type": "process_flow",
                    "nodes": [{"id": "A"}],
                    "edges": [],
                }
            )

    def test_edge_referencing_unknown_node_raises(self):
        with pytest.raises(ValueError, match="unknown node"):
            render_process_flow(
                {
                    "type": "process_flow",
                    "nodes": [{"id": "A", "label": "A"}],
                    "edges": [{"from": "A", "to": "NONEXISTENT"}],
                }
            )

    def test_edge_missing_from_raises(self):
        with pytest.raises(ValueError):
            render_process_flow(
                {
                    "type": "process_flow",
                    "nodes": [{"id": "A", "label": "A"}],
                    "edges": [{"to": "A"}],
                }
            )


# ---------------------------------------------------------------------------
# Scaling support
# ---------------------------------------------------------------------------

class TestScaling:
    def test_scale_affects_dimensions(self):
        result_1x = render_process_flow(VALID_SCHEMA, scale=1.0)
        result_2x = render_process_flow(VALID_SCHEMA, scale=2.0)
        # Extract width from SVG tag – 2x should be larger
        import re
        w1 = int(re.search(r'width="(\d+)"', result_1x).group(1))
        w2 = int(re.search(r'width="(\d+)"', result_2x).group(1))
        assert w2 > w1


# ---------------------------------------------------------------------------
# SVG root validation (via render_process_flow)
# ---------------------------------------------------------------------------

class TestSVGRootValidation:
    def test_wave_lineage_attribute(self):
        result = render_process_flow(VALID_SCHEMA)
        assert 'data-wave="W003"' in result

    def test_renderer_lineage_attribute(self):
        result = render_process_flow(VALID_SCHEMA)
        assert 'data-renderer="process_flow"' in result


# ---------------------------------------------------------------------------
# Lineage metadata
# ---------------------------------------------------------------------------

class TestLineageMetadata:
    def test_lineage_wave(self):
        assert LINEAGE["wave"] == "W003"

    def test_lineage_renderer(self):
        assert LINEAGE["renderer"] == "process_flow"

    def test_lineage_runtime_evidence(self):
        assert LINEAGE["runtime_evidence"] is True

    def test_lineage_metadata_function_returns_copy(self):
        meta = lineage_metadata()
        meta["wave"] = "TAMPERED"
        assert lineage_metadata()["wave"] == "W003"
