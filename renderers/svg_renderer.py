"""svg_renderer.py – Base SVG builder for the QPLANT Presentation Platform.

Wave: W003
Subwave: W003.2
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any


LINEAGE: dict[str, Any] = {
    "wave": "W003",
    "renderer": "svg",
    "runtime_evidence": True,
}


class SVGRenderer:
    """Construct well-formed SVG documents programmatically.

    All public methods return *self* so calls can be chained.  Call
    :meth:`render` to obtain the final SVG string.
    """

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        *,
        style_hook: str = "",
        renderer_name: str = LINEAGE["renderer"],
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive integers")
        self.width = width
        self.height = height
        self.style_hook = style_hook
        self._root = ET.Element(
            "svg",
            attrib={
                "xmlns": "http://www.w3.org/2000/svg",
                "width": str(width),
                "height": str(height),
                "viewBox": f"0 0 {width} {height}",
                "data-wave": LINEAGE["wave"],
                "data-renderer": renderer_name,
            },
        )
        # Always add a canvas group so the root element is never self-closed.
        ET.SubElement(self._root, "g", attrib={"class": "canvas"})
        if style_hook:
            style_el = ET.SubElement(self._root, "style")
            style_el.text = style_hook

    # ------------------------------------------------------------------
    # Primitive drawing helpers
    # ------------------------------------------------------------------

    def add_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        *,
        rx: float = 4,
        fill: str = "#e8f4fd",
        stroke: str = "#2c7bb6",
        stroke_width: float = 2,
        extra: dict[str, str] | None = None,
    ) -> "SVGRenderer":
        attrib: dict[str, str] = {
            "x": str(x),
            "y": str(y),
            "width": str(width),
            "height": str(height),
            "rx": str(rx),
            "fill": fill,
            "stroke": stroke,
            "stroke-width": str(stroke_width),
        }
        if extra:
            attrib.update(extra)
        ET.SubElement(self._root, "rect", attrib=attrib)
        return self

    def add_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        stroke: str = "#555",
        stroke_width: float = 2,
        marker_end: str = "url(#arrow)",
        extra: dict[str, str] | None = None,
    ) -> "SVGRenderer":
        attrib: dict[str, str] = {
            "x1": str(x1),
            "y1": str(y1),
            "x2": str(x2),
            "y2": str(y2),
            "stroke": stroke,
            "stroke-width": str(stroke_width),
        }
        if marker_end:
            attrib["marker-end"] = marker_end
        if extra:
            attrib.update(extra)
        ET.SubElement(self._root, "line", attrib=attrib)
        return self

    def add_text(
        self,
        x: float,
        y: float,
        text: str,
        *,
        font_size: int = 13,
        text_anchor: str = "middle",
        dominant_baseline: str = "central",
        fill: str = "#1a1a2e",
        extra: dict[str, str] | None = None,
    ) -> "SVGRenderer":
        attrib: dict[str, str] = {
            "x": str(x),
            "y": str(y),
            "font-size": str(font_size),
            "text-anchor": text_anchor,
            "dominant-baseline": dominant_baseline,
            "fill": fill,
            "font-family": "sans-serif",
        }
        if extra:
            attrib.update(extra)
        el = ET.SubElement(self._root, "text", attrib=attrib)
        el.text = text
        return self

    def add_defs(self, defs_xml: str) -> "SVGRenderer":
        """Inject raw XML into a *<defs>* element (e.g. marker definitions)."""
        defs = ET.SubElement(self._root, "defs")
        # Parse and append children without wrapping element
        fragment = ET.fromstring(f"<defs>{defs_xml}</defs>")
        for child in fragment:
            defs.append(child)
        return self

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def render(self) -> str:
        """Return a UTF-8 SVG string with an XML declaration."""
        ET.indent(self._root, space="  ")
        return ET.tostring(self._root, encoding="unicode", xml_declaration=False)

    @property
    def lineage(self) -> dict[str, Any]:
        """Return a copy of the lineage metadata block."""
        return dict(LINEAGE)
