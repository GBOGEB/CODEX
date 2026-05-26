"""
Wave 45 — PPTX Topology Reconstruction Runtime.

Purpose:
- reconstruct engineering topology from PPTX geometry telemetry
- infer nodes and edges from shapes/connectors
- generate graph-ready topology telemetry
- bridge geometry semantics into engineering-runtime graphs

Current scope:
- PPTX geometry CSV input
- heuristic connector reconstruction
- adjacency inference
- topology export

Future scope:
- SVG edge parsing
- Visio graph extraction
- DWG topology reconstruction
- semantic graph persistence
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

import pandas as pd


@dataclass
class TopologyNode:
    node_id: str
    slide_number: int
    semantic_role: str
    center_x_mm: float
    center_y_mm: float
    width_mm: float
    height_mm: float
    extracted_text: str


@dataclass
class TopologyEdge:
    edge_id: str
    source_node: str
    target_node: str
    inferred_distance_mm: float
    inference_type: str


class PPTXTopologyReconstructionRuntime:
    """Topology reconstruction from PPTX geometry telemetry."""

    NODE_ROLES = {
        "TITLE",
        "BODY_TEXT",
        "FLOW_OBJECT",
        "TABLE",
        "GROUP",
    }

    def __init__(self, geometry_csv: Path, output_dir: Path):
        self.geometry_csv = geometry_csv
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def center(left: float, top: float, width: float, height: float):
        return left + (width / 2.0), top + (height / 2.0)

    @staticmethod
    def distance(a_x: float, a_y: float, b_x: float, b_y: float) -> float:
        return math.sqrt(((a_x - b_x) ** 2) + ((a_y - b_y) ** 2))

    def build_nodes(self, df: pd.DataFrame) -> List[TopologyNode]:
        nodes: List[TopologyNode] = []

        for _, row in df.iterrows():
            if row["semantic_role"] not in self.NODE_ROLES:
                continue

            cx, cy = self.center(
                row["left_mm"],
                row["top_mm"],
                row["width_mm"],
                row["height_mm"],
            )

            nodes.append(
                TopologyNode(
                    node_id=f"S{row['slide_number']}_N{row['shape_index']}",
                    slide_number=int(row["slide_number"]),
                    semantic_role=row["semantic_role"],
                    center_x_mm=round(cx, 3),
                    center_y_mm=round(cy, 3),
                    width_mm=row["width_mm"],
                    height_mm=row["height_mm"],
                    extracted_text=row["extracted_text"][:500],
                )
            )

        return nodes

    def build_edges(self, nodes: List[TopologyNode]) -> List[TopologyEdge]:
        edges: List[TopologyEdge] = []

        for i, source in enumerate(nodes):
            nearest = None
            nearest_distance = 999999.0

            for j, target in enumerate(nodes):
                if i == j:
                    continue

                if source.slide_number != target.slide_number:
                    continue

                d = self.distance(
                    source.center_x_mm,
                    source.center_y_mm,
                    target.center_x_mm,
                    target.center_y_mm,
                )

                if d < nearest_distance:
                    nearest_distance = d
                    nearest = target

            if nearest and nearest_distance < 120:
                edges.append(
                    TopologyEdge(
                        edge_id=f"E{i}",
                        source_node=source.node_id,
                        target_node=nearest.node_id,
                        inferred_distance_mm=round(nearest_distance, 3),
                        inference_type="nearest_neighbor",
                    )
                )

        return edges

    def execute(self) -> Dict[str, str]:
        df = pd.read_csv(self.geometry_csv)

        nodes = self.build_nodes(df)
        edges = self.build_edges(nodes)

        nodes_df = pd.DataFrame([asdict(n) for n in nodes])
        edges_df = pd.DataFrame([asdict(e) for e in edges])

        nodes_csv = self.output_dir / "topology_nodes.csv"
        edges_csv = self.output_dir / "topology_edges.csv"
        graph_json = self.output_dir / "topology_graph.json"
        summary_json = self.output_dir / "topology_summary.json"

        nodes_df.to_csv(nodes_csv, index=False)
        edges_df.to_csv(edges_csv, index=False)

        graph = {
            "nodes": nodes_df.to_dict(orient="records"),
            "edges": edges_df.to_dict(orient="records"),
        }

        with open(graph_json, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2)

        summary = {
            "nodes": len(nodes),
            "edges": len(edges),
            "slides": int(nodes_df["slide_number"].nunique()) if not nodes_df.empty else 0,
            "inference_method": "nearest_neighbor_geometry",
        }

        with open(summary_json, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return {
            "nodes_csv": str(nodes_csv),
            "edges_csv": str(edges_csv),
            "graph_json": str(graph_json),
            "summary_json": str(summary_json),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Wave 45 topology reconstruction runtime")
    parser.add_argument("geometry_csv", help="Geometry telemetry CSV")
    parser.add_argument("--out", default="runtime_outputs/topology")

    args = parser.parse_args()

    runtime = PPTXTopologyReconstructionRuntime(
        geometry_csv=Path(args.geometry_csv),
        output_dir=Path(args.out),
    )

    outputs = runtime.execute()
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
