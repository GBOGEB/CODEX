from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SemanticInference:
    inference_id: str
    inference_type: str
    confidence: float
    source_nodes: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class SemanticDriftSignal:
    signal_id: str
    drift_score: float
    affected_regions: List[str] = field(default_factory=list)


class AISemanticInferenceLayer:
    """
    Wave 18 AI-Assisted Semantic Inference Layer.

    Purpose:
    - provide AI-assisted topology inference
    - detect semantic drift
    - establish semantic confidence scoring
    - support autonomous engineering interpretation

    Platform:
    Engineering Deck Convergence Platform (EDCP)
    """

    def __init__(self):
        self.inferences: List[SemanticInference] = []
        self.drift_signals: List[SemanticDriftSignal] = []

    def register_inference(self, inference: SemanticInference):
        self.inferences.append(inference)

    def register_drift_signal(self, signal: SemanticDriftSignal):
        self.drift_signals.append(signal)

    def calculate_semantic_confidence(self) -> float:
        if not self.inferences:
            return 0.0

        total_confidence = sum(i.confidence for i in self.inferences)
        return round(total_confidence / len(self.inferences), 2)

    def detect_high_drift_regions(self) -> List[str]:
        regions = []

        for signal in self.drift_signals:
            if signal.drift_score > 0.65:
                regions.extend(signal.affected_regions)

        return sorted(set(regions))

    def build_inference_summary(self) -> Dict:
        return {
            "semantic_confidence": self.calculate_semantic_confidence(),
            "high_drift_regions": self.detect_high_drift_regions(),
            "inference_count": len(self.inferences),
            "drift_signal_count": len(self.drift_signals),
        }


if __name__ == "__main__":
    layer = AISemanticInferenceLayer()

    layer.register_inference(
        SemanticInference(
            inference_id="inf_001",
            inference_type="topology_prediction",
            confidence=0.91,
            source_nodes=["slide_01", "slide_08"],
        )
    )

    layer.register_drift_signal(
        SemanticDriftSignal(
            signal_id="drift_001",
            drift_score=0.72,
            affected_regions=["region_04", "region_09"],
        )
    )

    summary = layer.build_inference_summary()

    print(summary)
