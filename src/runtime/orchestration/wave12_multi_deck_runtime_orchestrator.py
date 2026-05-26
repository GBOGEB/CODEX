from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DeckManifest:
    deck_id: str
    domain: str
    source_type: str
    slide_count: int
    renderer_profile: str


@dataclass
class RuntimeTemplate:
    template_id: str
    supported_domains: List[str]
    card_types: List[str]
    evidence_policy: str


class MultiDeckRuntimeOrchestrator:
    """
    Wave 12 Runtime Generalization + Multi-Deck Architecture.

    Purpose:
    - orchestrate multiple engineering decks
    - support reusable renderer templates
    - normalize convergence across domains
    - enable generalized engineering runtime workflows

    Platform:
    Engineering Deck Convergence Platform (EDCP)
    """

    def __init__(self):
        self.decks: Dict[str, DeckManifest] = {}
        self.templates: Dict[str, RuntimeTemplate] = {}

    def register_deck(self, manifest: DeckManifest):
        self.decks[manifest.deck_id] = manifest

    def register_template(self, template: RuntimeTemplate):
        self.templates[template.template_id] = template

    def resolve_template(self, domain: str) -> List[RuntimeTemplate]:
        compatible_templates = []

        for template in self.templates.values():
            if domain in template.supported_domains:
                compatible_templates.append(template)

        return compatible_templates

    def build_runtime_summary(self) -> Dict:
        return {
            "registered_decks": len(self.decks),
            "registered_templates": len(self.templates),
            "domains": list({deck.domain for deck in self.decks.values()}),
            "deck_ids": list(self.decks.keys()),
        }


if __name__ == "__main__":
    orchestrator = MultiDeckRuntimeOrchestrator()

    orchestrator.register_deck(
        DeckManifest(
            deck_id="thermal_shields_001",
            domain="cryogenic",
            source_type="pptx",
            slide_count=27,
            renderer_profile="evidence-first",
        )
    )

    orchestrator.register_template(
        RuntimeTemplate(
            template_id="engineering_dual_column_v1",
            supported_domains=["cryogenic", "manufacturing", "p&id"],
            card_types=["EvidenceCard", "TableCard", "SVGCard"],
            evidence_policy="IMAGE_GT_OCR",
        )
    )

    summary = orchestrator.build_runtime_summary()

    print(summary)
