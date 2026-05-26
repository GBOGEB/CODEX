"""
Wave 16 — Engineering Topology Graph Runtime.

This module establishes the first executable engineering graph runtime for the
Engineering Semantic Runtime Platform.

Purpose:
- model engineering systems as traversable graphs
- normalize subsystem interfaces
- represent TP/MIT/MIS semantic edges
- support topology-aware runtime navigation
- prepare interactive engineering semantic runtimes
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import json


class NodeType(str, Enum):
    SYSTEM = "system"
    SUBSYSTEM = "subsystem"
    INTERFACE = "interface"
    EQUIPMENT = "equipment"
    ROOM = "room"
    UTILITY = "utility"
    CONTROL = "control"


class EdgeType(str, Enum):
    FLOW = "flow"
    SIGNAL = "signal"
    INTERLOCK = "interlock"
    THERMAL = "thermal"
    ELECTRICAL = "electrical"
    NETWORK = "network"
    TOPOLOGY = "topology"


@dataclass
class SemanticNode:
    node_id: str
    label: str
    node_type: NodeType
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class SemanticEdge:
    source: str
    target: str
    edge_type: EdgeType
    label: str
    confidence: float = 1.0
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class EngineeringGraph:
    graph_id: str
    title: str
    nodes: List[SemanticNode] = field(default_factory=list)
    edges: List[SemanticEdge] = field(default_factory=list)


class EngineeringTopologyRuntime:
    """
    Executable engineering graph runtime.

    Supports:
    - subsystem dependency traversal
    - utility-flow graph extraction
    - MIT/MIS/MCS interface mapping
    - HVAC/PCW/RCW engineering topology
    - graph-aware semantic navigation
    """

    def __init__(self):
        self.graphs: Dict[str, EngineeringGraph] = {}

    def register_graph(self, graph: EngineeringGraph):
        self.graphs[graph.graph_id] = graph

    def add_node(self, graph_id: str, node: SemanticNode):
        self.graphs[graph_id].nodes.append(node)

    def add_edge(self, graph_id: str, edge: SemanticEdge):
        self.graphs[graph_id].edges.append(edge)

    def neighbors(self, graph_id: str, node_id: str) -> List[SemanticNode]:
        graph = self.graphs[graph_id]
        targets = {
            edge.target
            for edge in graph.edges
            if edge.source == node_id
        }
        return [node for node in graph.nodes if node.node_id in targets]

    def classify_interface(self, label: str) -> EdgeType:
        upper = label.upper()

        if "MIT" in upper:
            return EdgeType.SIGNAL

        if "MIS" in upper:
            return EdgeType.INTERLOCK

        if "MCS" in upper or "OPC" in upper:
            return EdgeType.NETWORK

        if any(token in upper for token in ["PCW", "RCW", "HVAC"]):
            return EdgeType.FLOW

        return EdgeType.TOPOLOGY

    def export_graph_json(self, graph_id: str) -> str:
        graph = self.graphs[graph_id]
        return json.dumps(asdict(graph), indent=2)


if __name__ == "__main__":
    runtime = EngineeringTopologyRuntime()

    graph = EngineeringGraph(
        graph_id="qplant_wcs_runtime",
        title="QPLANT WCS Semantic Runtime",
    )

    runtime.register_graph(graph)

    runtime.add_node(
        graph.graph_id,
        SemanticNode(
            node_id="QPLANT",
            label="QPLANT",
            node_type=NodeType.SYSTEM,
        ),
    )

    runtime.add_node(
        graph.graph_id,
        SemanticNode(
            node_id="WCS.HCC",
            label="WCS.HCC",
            node_type=NodeType.SUBSYSTEM,
        ),
    )

    runtime.add_edge(
        graph.graph_id,
        SemanticEdge(
            source="QPLANT",
            target="WCS.HCC",
            edge_type=runtime.classify_interface("PCW Interface"),
            label="PCW Interface",
            confidence=0.94,
        ),
    )

    print(runtime.export_graph_json(graph.graph_id))
