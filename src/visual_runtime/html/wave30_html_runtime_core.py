from dataclasses import dataclass, field
from html import escape
from typing import Dict, List


@dataclass
class RuntimeCard:
    card_id: str
    title: str
    card_type: str
    body: str
    tags: List[str] = field(default_factory=list)


@dataclass
class RuntimeSlide:
    slide_id: str
    title: str
    subtitle: str
    cards: List[RuntimeCard] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class HTMLRuntimeCore:
    """
    Wave 30 pivot runtime.

    Converts normalized engineering slide content into browser-ready HTML.
    This is the visual execution layer after the semantic architecture pivot.
    """

    def render_card(self, card: RuntimeCard) -> str:
        tags = "".join(f'<span class="tag">{escape(tag)}</span>' for tag in card.tags)
        return f'''
        <article class="runtime-card {escape(card.card_type)}" data-card-id="{escape(card.card_id)}">
          <header class="card-title">{escape(card.title)}</header>
          <div class="card-tags">{tags}</div>
          <section class="card-body">{escape(card.body)}</section>
        </article>
        '''

    def render_slide(self, slide: RuntimeSlide) -> str:
        cards = "\n".join(self.render_card(card) for card in slide.cards)
        return f'''
        <section class="runtime-slide" data-slide-id="{escape(slide.slide_id)}">
          <header class="slide-header">
            <h1>{escape(slide.title)}</h1>
            <p>{escape(slide.subtitle)}</p>
          </header>
          <main class="card-grid">{cards}</main>
        </section>
        '''

    def render_document(self, slides: List[RuntimeSlide]) -> str:
        body = "\n".join(self.render_slide(slide) for slide in slides)
        return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Engineering Deck Runtime</title>
  <link rel="stylesheet" href="runtime.css">
</head>
<body>
{body}
</body>
</html>
'''


if __name__ == "__main__":
    runtime = HTMLRuntimeCore()
    html = runtime.render_document([
        RuntimeSlide(
            slide_id="QRB_AUB_001",
            title="QRB move-in ROOF (AUB) Constraints",
            subtitle="QPLANT + Storages | QPS / ACR:NFS Buildings interface",
            cards=[
                RuntimeCard("decision", "Decision", "decision", "13.5 m maximum approved roof-opening length.", ["DECISION"]),
                RuntimeCard("constraint", "Constraint", "constraint", "Do not answer as full room availability.", ["CONSTRAINT"]),
            ],
        )
    ])
    print(html)
