from __future__ import annotations

from typing import Any


def line_trace(name: str, x: list[float], y: list[float]) -> dict[str, Any]:
    return {"type": "scatter", "mode": "lines+markers", "name": name, "x": x, "y": y}


def bar_trace(name: str, x: list[str], y: list[float]) -> dict[str, Any]:
    return {"type": "bar", "name": name, "x": x, "y": y}


def heatmap_trace(name: str, x: list[str], y: list[str], z: list[list[float]]) -> dict[str, Any]:
    return {"type": "heatmap", "name": name, "x": x, "y": y, "z": z}


class PlotlyTraceBuilder:
    """Build JSON-compatible Plotly trace dictionaries.

    The dashboard stays static and GitHub Pages compatible; generated traces
    can be written to JSON and rendered without a Python runtime in the browser.
    """

    def saturation_traces(self, saturation: dict[str, list[float]]) -> list[dict[str, Any]]:
        return [
            line_trace("liquid branch", saturation["entropy_liquid"], saturation["temperature_liquid"]),
            line_trace("vapor branch", saturation["entropy_vapor"], saturation["temperature_vapor"]),
        ]

    def agreement_trace(self, x: list[str], y: list[str], z: list[list[float]]) -> dict[str, Any]:
        return heatmap_trace("backend agreement", x, y, z)
