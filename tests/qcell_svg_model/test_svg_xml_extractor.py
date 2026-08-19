from pathlib import Path

from qcell_svg_model.tools.svg_xml_extractor import extract_svg_xml


def test_preserves_inkscape_layers_labels_text_ids_colours_and_hierarchy(
    tmp_path: Path,
) -> None:
    source = tmp_path / "inkscape_layers.svg"
    source.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
  <g id="layer_thermal" inkscape:groupmode="layer" inkscape:label="Thermal Architecture">
    <g id="group_2k" inkscape:label="2 K group" style="fill:#dae8fc;stroke:#6c8ebf">
      <text id="text_mass" fill="#111827"><tspan id="tspan_mass">2 K Superfluid Mass</tspan></text>
    </g>
  </g>
  <g id="layer_pressure" inkscape:groupmode="layer" inkscape:label="Pressure Diagnostics">
    <rect id="p1" style="fill:#d5e8d4;stroke:#82b366" />
  </g>
</svg>
""",
        encoding="utf-8",
    )

    manifest = extract_svg_xml(source)

    assert manifest["source_kind"] == "inkscape_svg"
    assert manifest["extraction_policy"] == {
        "primary_source": "svg_xml",
        "ocr": False,
        "rasterize": False,
        "parse_pdf_first": False,
        "preserve_text_nodes": True,
        "preserve_layer_labels": True,
        "preserve_object_ids": True,
        "preserve_color_metadata": True,
        "preserve_group_hierarchy": True,
    }
    assert [layer["label"] for layer in manifest["layers"]] == [
        "Thermal Architecture",
        "Pressure Diagnostics",
    ]

    objects_by_id = {obj["id"]: obj for obj in manifest["objects"]}
    assert objects_by_id["text_mass"]["text"] == "2 K Superfluid Mass"
    assert objects_by_id["text_mass"]["layer_path"] == ["Thermal Architecture"]
    assert objects_by_id["group_2k"]["inkscape_label"] == "2 K group"
    assert objects_by_id["group_2k"]["colors"] == {
        "fill": "#dae8fc",
        "stroke": "#6c8ebf",
    }
    assert {
        tuple(edge.values()) for edge in manifest["group_hierarchy"] if len(edge) == 2
    } >= {
        ("layer_thermal", "group_2k"),
        ("group_2k", "text_mass"),
        ("text_mass", "tspan_mass"),
    }


def test_extracts_drawio_sheet_layers_and_cell_semantics() -> None:
    source = Path("qcell_svg_model/v0_8_1/drawio/QCELL_PARASITIC.drawio.svg")
    manifest = extract_svg_xml(source)

    assert manifest["source_kind"] == "drawio_mxfile_svg_xml"
    assert len(manifest["diagrams"]) == 4
    layer_labels = [layer["label"] for layer in manifest["layers"]]
    assert "Copy of Copy of Copy of BSLN_0" in layer_labels
    assert "Thermal Layer" in layer_labels
    assert "Pressure Diagnostic Layer" in layer_labels
    assert "Teaching Flow Layer" in layer_labels

    objects_by_text = {
        obj["text"]: obj for obj in manifest["objects"] if obj.get("text")
    }
    assert objects_by_text["2 K Superfluid Mass"]["colors"] == {
        "fill": "#dae8fc",
        "stroke": "#6c8ebf",
    }
    assert objects_by_text["P1 - Supply Pressure"]["layer_path"] == [
        "Copy of Copy of Copy of BSLN_0",
        "Pressure Diagnostic Layer",
    ]
    assert objects_by_text["Coolant In"]["layer_path"] == [
        "Copy of Copy of Copy of BSLN_0",
        "Teaching Flow Layer",
    ]
