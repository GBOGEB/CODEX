from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class EngineeringNode:
    node_id: str
    node_type: str
    label: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class EngineeringEdge:
    source: str
    target: str
    relation: str


class EngineeringSemanticGraph:
    """
    Wave 15 Engineering Graph Intelligence Layer.

    Purpose:
    - establish semantic engineering topology graphs
    - support cross-slide engineering continuity
    - enable evidence lineage tracing
    - provide runtime semantic query support

    Platform:
    Engineering Deck Convergence Platform (EDCP)
    """

    def __init__(self):
        self.nodes: Dict[str, EngineeringNode] = {}
        self.edges: List[EngineeringEdge] = []

    def add_node(self, node: EngineeringNode):
        self.nodes[node.node_id] = node

    def add_edge(self, edge: EngineeringEdge):
        self.edges.append(edge)

    def get_neighbors(self, node_id: str) -> Set[str]:
        neighbors = set()

        for edge in self.edges:
            if edge.source == node_id:
                neighbors.add(edge.target)
            elif edge.target == node_id:
                neighbors.add(edge.source)

        return neighbors

    def build_lineage_graph(self) -> Dict:
        lineage = {}

        for node_id in self.nodes:
            lineage[node_id] = {
                "label": self.nodes[node_id].label,
                "neighbors": list(self.get_neighbors(node_id)),
            }

        return lineage

    def semantic_query(self, relation: str) -> List[Dict]:
        results = []

        for edge in self.edges:
            if edge.relation == relation:
                results.append(
                    {
                        "source": edge.source,
                        "target": edge.target,
                        "relation": edge.relation,
                    }
                )

        return results


if __name__ == "__main__":
    graph = EngineeringSemanticGraph()

    graph.add_node(
        EngineeringNode(
            node_id="slide_01",
            node_type="EvidenceCard",
            label="Thermal Shield Evidence",
        )
    )

    graph.add_node(
        EngineeringNode(
            node_id="slide_08",
            node_type="SVGCard",
            label="Flow Topology",
        )
    )

    graph.add_edge(
        EngineeringEdge(
            source="slide_01",
            target="slide_08",
            relation="topology_reference",
        )
    )

    lineage = graph.build_lineage_graph()
    query_results = graph.semantic_query("topology_reference")

    print(lineage)
    print(query_results)
