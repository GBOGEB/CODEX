from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DependencyNode:
    node_id: str
    node_type: str
    depends_on: list[str] = field(default_factory=list)


class DependencyGraph:
    """Dependency-aware publication graph scaffold.

    Future direction:
    - incremental rebuilds
    - dependency invalidation
    - render caching
    - artifact dependency tracking
    - thermodynamic plot dependency tracking
    """

    def __init__(self) -> None:
        self.nodes: dict[str, DependencyNode] = {}

    def add_node(self, node: DependencyNode) -> None:
        self.nodes[node.node_id] = node

    def affected_by_change(self, node_id: str) -> list[str]:
        affected: list[str] = []

        for candidate in self.nodes.values():
            if node_id in candidate.depends_on:
                affected.append(candidate.node_id)

        return affected


if __name__ == '__main__':
    graph = DependencyGraph()
    graph.add_node(DependencyNode('slide_01', 'slide'))
    graph.add_node(
        DependencyNode(
            'html_01',
            'html_render',
            depends_on=['slide_01'],
        )
    )

    print(graph.affected_by_change('slide_01'))
