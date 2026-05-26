from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SemanticRegion:
    region_id: str
    region_type: str
    confidence: float
    bounds: Dict[str, int]


@dataclass
class SlideSemanticModel:
    slide_id: str
    slide_type: str
    semantic_regions: List[SemanticRegion] = field(default_factory=list)


class SVGAbstractionEngine:
    """
    Wave 10 prototype runtime.

    Purpose:
    - convert engineering slide semantics into lightweight SVG abstractions
    - preserve engineering topology and visual hierarchy
    - separate evidence imagery from conceptual SVG overlays

    Platform:
    Engineering Deck Convergence Platform (EDCP)
    """

    def __init__(self):
        self.supported_slide_types = {
            "CAD",
            "PHOTO",
            "FEA",
            "PID",
            "TABLE",
            "MIXED",
        }

    def build_svg_canvas(self, width: int = 1200, height: int = 800) -> str:
        return (
            f'<svg width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" '
            'xmlns="http://www.w3.org/2000/svg">'
        )

    def render_heading_band(self, title: str) -> str:
        return f'''
        <g class="heading-band">
            <rect x="0" y="0" width="1200" height="64" fill="#F6F0FA"/>
            <text x="32" y="40"
                  font-size="28"
                  font-family="Aptos, Arial"
                  fill="#5A237A"
                  font-weight="700">{title}</text>
        </g>
        '''

    def render_semantic_region(self, region: SemanticRegion) -> str:
        x = region.bounds.get("x", 0)
        y = region.bounds.get("y", 0)
        w = region.bounds.get("width", 100)
        h = region.bounds.get("height", 100)

        return f'''
        <g class="semantic-region" data-type="{region.region_type}">
            <rect x="{x}" y="{y}"
                  width="{w}" height="{h}"
                  rx="8"
                  fill="#FAFAFA"
                  stroke="#D9D9D9"
                  stroke-width="1"/>
            <text x="{x + 12}" y="{y + 24}"
                  font-size="14"
                  fill="#1F2933"
                  font-family="Aptos, Arial">
                  {region.region_type}
            </text>
        </g>
        '''

    def generate_slide_svg(self, model: SlideSemanticModel, title: str) -> str:
        if model.slide_type not in self.supported_slide_types:
            raise ValueError(f"Unsupported slide type: {model.slide_type}")

        svg = [self.build_svg_canvas()]
        svg.append(self.render_heading_band(title))

        for region in model.semantic_regions:
            svg.append(self.render_semantic_region(region))

        svg.append('</svg>')

        return "\n".join(svg)


if __name__ == "__main__":
    engine = SVGAbstractionEngine()

    model = SlideSemanticModel(
        slide_id="thermal_shields_001",
        slide_type="MIXED",
        semantic_regions=[
            SemanticRegion(
                region_id="r1",
                region_type="EvidenceCard",
                confidence=0.96,
                bounds={"x": 40, "y": 100, "width": 520, "height": 520},
            ),
            SemanticRegion(
                region_id="r2",
                region_type="TableCard",
                confidence=0.92,
                bounds={"x": 620, "y": 100, "width": 520, "height": 520},
            ),
        ],
    )

    svg_output = engine.generate_slide_svg(
        model=model,
        title="Thermal Shields — Semantic SVG Runtime"
    )

    print(svg_output)
