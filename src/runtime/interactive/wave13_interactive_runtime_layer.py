from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InteractiveRegion:
    region_id: str
    label: str
    region_type: str
    target_slide: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class InteractiveOverlay:
    overlay_id: str
    title: str
    regions: List[InteractiveRegion] = field(default_factory=list)


class InteractiveEngineeringRuntime:
    """
    Wave 13 Interactive Engineering Runtime Layer.

    Purpose:
    - provide semantic engineering interaction
    - support clickable evidence regions
    - enable topology traversal
    - support runtime engineering overlays

    Platform:
    Engineering Deck Convergence Platform (EDCP)
    """

    def __init__(self):
        self.overlays: Dict[str, InteractiveOverlay] = {}

    def register_overlay(self, overlay: InteractiveOverlay):
        self.overlays[overlay.overlay_id] = overlay

    def build_overlay_manifest(self) -> Dict:
        return {
            overlay_id: {
                "title": overlay.title,
                "region_count": len(overlay.regions),
                "regions": [
                    {
                        "region_id": region.region_id,
                        "label": region.label,
                        "region_type": region.region_type,
                        "target_slide": region.target_slide,
                    }
                    for region in overlay.regions
                ],
            }
            for overlay_id, overlay in self.overlays.items()
        }

    def build_navigation_graph(self) -> Dict[str, List[str]]:
        graph = {}

        for overlay_id, overlay in self.overlays.items():
            graph[overlay_id] = []

            for region in overlay.regions:
                if region.target_slide:
                    graph[overlay_id].append(region.target_slide)

        return graph


if __name__ == "__main__":
    runtime = InteractiveEngineeringRuntime()

    overlay = InteractiveOverlay(
        overlay_id="thermal_overlay_001",
        title="Thermal Shields Interactive Overlay",
        regions=[
            InteractiveRegion(
                region_id="r1",
                label="Evidence Card",
                region_type="evidence",
                target_slide="slide_02",
            ),
            InteractiveRegion(
                region_id="r2",
                label="Flow Path",
                region_type="topology",
                target_slide="slide_08",
            ),
        ],
    )

    runtime.register_overlay(overlay)

    manifest = runtime.build_overlay_manifest()
    navigation_graph = runtime.build_navigation_graph()

    print(manifest)
    print(navigation_graph)
