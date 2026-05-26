"""
Wave 17 — Interactive Engineering Knowledge Runtime.

This module introduces the first interactive engineering-runtime layer.

Purpose:
- traverse engineering semantic graphs
- connect evidence assets to topology nodes
- support semantic engineering search
- enable subsystem dependency exploration
- prepare browser/runtime UX integration
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional
import json


@dataclass
class EvidenceReference:
    evidence_id: str
    title: str
    path: str
    renderer_type: str
    confidence: float


@dataclass
class RuntimeView:
    view_id: str
    title: str
    active_node: str
    visible_nodes: List[str] = field(default_factory=list)
    visible_edges: List[str] = field(default_factory=list)
    evidence_refs: List[EvidenceReference] = field(default_factory=list)


@dataclass
class SemanticSearchResult:
    node_id: str
    label: str
    score: float
    matched_terms: List[str] = field(default_factory=list)


class InteractiveKnowledgeRuntime:
    """
    Interactive engineering-runtime orchestration.

    Provides:
    - semantic engineering navigation
    - graph-aware search
    - evidence-linked topology traversal
    - subsystem dependency exploration
    - runtime-view generation
    """

    def __init__(self):
        self.node_index: Dict[str, Dict] = {}
        self.edge_index: Dict[str, List[str]] = {}
        self.evidence_links: Dict[str, List[EvidenceReference]] = {}

    def register_node(self, node_id: str, payload: Dict):
        self.node_index[node_id] = payload

    def register_edge(self, source: str, target: str):
        self.edge_index.setdefault(source, []).append(target)

    def link_evidence(self, node_id: str, evidence: EvidenceReference):
        self.evidence_links.setdefault(node_id, []).append(evidence)

    def semantic_search(self, query: str) -> List[SemanticSearchResult]:
        terms = query.lower().split()
        results: List[SemanticSearchResult] = []

        for node_id, payload in self.node_index.items():
            text = json.dumps(payload).lower()
            matched = [term for term in terms if term in text]

            if matched:
                score = round(len(matched) / len(terms), 2)
                results.append(
                    SemanticSearchResult(
                        node_id=node_id,
                        label=payload.get("label", node_id),
                        score=score,
                        matched_terms=matched,
                    )
                )

        return sorted(results, key=lambda item: item.score, reverse=True)

    def generate_runtime_view(self, node_id: str) -> RuntimeView:
        neighbors = self.edge_index.get(node_id, [])

        visible_edges = [
            f"{node_id}->{target}"
            for target in neighbors
        ]

        return RuntimeView(
            view_id=f"runtime::{node_id}",
            title=f"Interactive Runtime — {node_id}",
            active_node=node_id,
            visible_nodes=[node_id] + neighbors,
            visible_edges=visible_edges,
            evidence_refs=self.evidence_links.get(node_id, []),
        )

    def export_runtime_view(self, node_id: str) -> str:
        view = self.generate_runtime_view(node_id)
        return json.dumps(asdict(view), indent=2)


if __name__ == "__main__":
    runtime = InteractiveKnowledgeRuntime()

    runtime.register_node(
        "QPLANT",
        {
            "label": "QPLANT",
            "category": "system",
            "interfaces": ["PCW", "MIT", "MCS"],
        },
    )

    runtime.register_node(
        "WCS.HCC",
        {
            "label": "WCS.HCC",
            "category": "subsystem",
            "interfaces": ["RCW", "HVAC"],
        },
    )

    runtime.register_edge("QPLANT", "WCS.HCC")

    runtime.link_evidence(
        "WCS.HCC",
        EvidenceReference(
            evidence_id="ev-001",
            title="WCS.HCC Skid Overview",
            path="evidence/wcs_hcc_skid.png",
            renderer_type="EvidenceCard",
            confidence=0.96,
        ),
    )

    print(runtime.export_runtime_view("QPLANT"))
