from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LayoutCard:
    card_id: str
    card_type: str
    priority: int
    width: int
    height: int


@dataclass
class LayoutZone:
    zone_id: str
    cards: List[LayoutCard] = field(default_factory=list)


class AdaptiveSemanticLayoutEngine:
    """
    Wave 14 Adaptive Semantic Layout Engine.

    Purpose:
    - dynamically optimize engineering semantic layouts
    - normalize spacing and hierarchy
    - stabilize responsive runtime behavior
    - reduce layout drift across convergence workflows

    Platform:
    Engineering Deck Convergence Platform (EDCP)
    """

    def __init__(self):
        self.zones: Dict[str, LayoutZone] = {}

    def register_zone(self, zone: LayoutZone):
        self.zones[zone.zone_id] = zone

    def calculate_zone_density(self, zone_id: str) -> float:
        zone = self.zones[zone_id]

        total_area = 0
        for card in zone.cards:
            total_area += card.width * card.height

        return round(total_area / 1000000, 2)

    def optimize_card_order(self, zone_id: str) -> List[LayoutCard]:
        zone = self.zones[zone_id]

        return sorted(
            zone.cards,
            key=lambda card: (
                -card.priority,
                card.card_type,
            ),
        )

    def build_layout_manifest(self) -> Dict:
        manifest = {}

        for zone_id, zone in self.zones.items():
            manifest[zone_id] = {
                "card_count": len(zone.cards),
                "density": self.calculate_zone_density(zone_id),
                "optimized_order": [
                    card.card_id
                    for card in self.optimize_card_order(zone_id)
                ],
            }

        return manifest


if __name__ == "__main__":
    engine = AdaptiveSemanticLayoutEngine()

    zone = LayoutZone(
        zone_id="main_layout",
        cards=[
            LayoutCard(
                card_id="evidence_001",
                card_type="EvidenceCard",
                priority=10,
                width=600,
                height=600,
            ),
            LayoutCard(
                card_id="table_001",
                card_type="TableCard",
                priority=7,
                width=500,
                height=500,
            ),
            LayoutCard(
                card_id="svg_001",
                card_type="SVGCard",
                priority=8,
                width=520,
                height=520,
            ),
        ],
    )

    engine.register_zone(zone)

    manifest = engine.build_layout_manifest()

    print(manifest)
