"""
Wave 18 — AI Semantic Reasoning & Engineering Intent Runtime.

This module introduces engineering semantic reasoning primitives for the
Engineering Semantic Runtime Platform.

Purpose:
- infer engineering intent from topology
- detect semantic anomalies
- reason about subsystem dependencies
- support engineering Q&A runtime contexts
- prepare graph-assisted engineering intelligence
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List
import json


@dataclass
class EngineeringIntent:
    intent_id: str
    category: str
    confidence: float
    reasoning: List[str] = field(default_factory=list)


@dataclass
class SemanticAnomaly:
    anomaly_id: str
    severity: str
    description: str
    affected_nodes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DependencyInference:
    source: str
    target: str
    dependency_type: str
    confidence: float
    explanation: str


class EngineeringSemanticReasoningRuntime:
    """
    Graph-assisted engineering semantic reasoning runtime.

    Capabilities:
    - infer subsystem operational intent
    - identify missing engineering relationships
    - detect topology anomalies
    - support engineering semantic Q&A
    - enrich runtime graph intelligence
    """

    UTILITY_KEYWORDS = {
        "PCW": "cooling_supply",
        "RCW": "recovery_cooling",
        "HVAC": "environmental_control",
        "MIT": "signal_exchange",
        "MIS": "safety_interlock",
        "MCS": "supervisory_control",
    }

    def infer_intent(self, node_payload: Dict) -> EngineeringIntent:
        reasoning: List[str] = []
        category = "general_system"
        confidence = 0.65

        text = json.dumps(node_payload).upper()

        for keyword, inferred in self.UTILITY_KEYWORDS.items():
            if keyword in text:
                category = inferred
                confidence += 0.05
                reasoning.append(f"Detected keyword: {keyword}")

        if "HVAC" in text and "PCW" in text:
            reasoning.append("Combined HVAC and PCW suggest thermal-management intent")
            confidence += 0.08

        return EngineeringIntent(
            intent_id=node_payload.get("label", "unknown"),
            category=category,
            confidence=min(confidence, 0.99),
            reasoning=reasoning,
        )

    def detect_anomalies(self, graph_nodes: List[Dict]) -> List[SemanticAnomaly]:
        anomalies: List[SemanticAnomaly] = []

        for node in graph_nodes:
            text = json.dumps(node).upper()

            if "MIS" in text and "MIT" not in text:
                anomalies.append(
                    SemanticAnomaly(
                        anomaly_id=f"anomaly::{node.get('label','unknown')}",
                        severity="medium",
                        description="MIS interface detected without MIT companion interface.",
                        affected_nodes=[node.get("label", "unknown")],
                        recommendations=[
                            "Verify control-system interface completeness",
                            "Review MIT/MIS interface mapping",
                        ],
                    )
                )

        return anomalies

    def infer_dependencies(self, source: Dict, target: Dict) -> DependencyInference:
        src_text = json.dumps(source).upper()
        tgt_text = json.dumps(target).upper()

        dependency_type = "topology"
        confidence = 0.72
        explanation = "Generic topology dependency inferred."

        if "PCW" in src_text and "HVAC" in tgt_text:
            dependency_type = "thermal_support"
            confidence = 0.91
            explanation = "PCW cooling dependency inferred for HVAC-linked subsystem."

        if "MCS" in src_text and "MIT" in tgt_text:
            dependency_type = "control_signal"
            confidence = 0.89
            explanation = "MCS supervisory dependency inferred through MIT interface."

        return DependencyInference(
            source=source.get("label", "unknown"),
            target=target.get("label", "unknown"),
            dependency_type=dependency_type,
            confidence=confidence,
            explanation=explanation,
        )

    @staticmethod
    def export_json(payload) -> str:
        return json.dumps(asdict(payload), indent=2)


if __name__ == "__main__":
    runtime = EngineeringSemanticReasoningRuntime()

    qplant = {
        "label": "QPLANT",
        "interfaces": ["PCW", "MCS", "MIT"],
    }

    wcs = {
        "label": "WCS.HCC",
        "interfaces": ["HVAC", "MIS"],
    }

    intent = runtime.infer_intent(qplant)
    dependency = runtime.infer_dependencies(qplant, wcs)
    anomalies = runtime.detect_anomalies([qplant, wcs])

    print(runtime.export_json(intent))
    print(runtime.export_json(dependency))
    print([runtime.export_json(a) for a in anomalies])
