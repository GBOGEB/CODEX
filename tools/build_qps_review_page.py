"""Build the QPS side-by-side lineage review page from the review YAML records.

Sources:
  docs/qps-slide-system/review/lineage/*.review.yaml   one record per review (schema: yaml/schema.review.yaml)
  docs/qps-slide-system/yaml/nodes/*.yaml              node records, to link slides and extracted objects
  docs/qps-slide-system/styles/tokens.yaml             colors and typography (via build_qps_node_graph)
Output:
  docs/qps-slide-system/html/review.html               source vs curated, comments, extracted objects

Each review shows the source slide (left) beside the curated slide (right), the
lineage of the source, the reviewer comments and the extracted semantic objects.
A slide id is matched to the node whose `slides` list holds its base id
(`SBSBW.01.original` -> `SBSBW.01`); an extracted object whose id is a node id
links to that node page.

Deterministic; a test fails if the committed page is stale. Regenerate with:
  python tools/build_qps_review_page.py           (write)
  python tools/build_qps_review_page.py --check   (exit 1 when stale)
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from html import escape
from pathlib import Path
from typing import Any

import yaml


def _load_graph_module():
    """Reuse the node-graph builder (records, page shell, tokens) instead of copying it."""
    path = Path(__file__).resolve().with_name("build_qps_node_graph.py")
    spec = importlib.util.spec_from_file_location("build_qps_node_graph", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


graph = _load_graph_module()

SYSTEM = graph.SYSTEM
REVIEWS_DIR = SYSTEM / "review" / "lineage"
SCHEMA = SYSTEM / "yaml" / "schema.review.yaml"
REVIEW_PATH = "html/review.html"
SUFFIX = ".review.yaml"


class ReviewError(ValueError):
    """A review record breaks the schema."""


def load_reviews(reviews_dir: Path = REVIEWS_DIR, schema_path: Path = SCHEMA) -> list[dict[str, Any]]:
    """Load and validate every review record, sorted by file name; each carries its file stem."""
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))["review"]
    reviews: list[dict[str, Any]] = []
    for path in sorted(reviews_dir.glob(f"*{SUFFIX}")):
        record = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("review")
        if not isinstance(record, dict):
            raise ReviewError(f"{path.name}: missing top-level 'review' mapping")
        missing = [k for k in schema if k not in record]
        if missing:
            raise ReviewError(f"{path.name}: missing keys {missing}")
        for key, kind in schema.items():
            if isinstance(kind, list) and not isinstance(record[key], list):
                raise ReviewError(f"{path.name}: '{key}' must be a list")
            if not isinstance(kind, list) and not (isinstance(record[key], str) and record[key].strip()):
                raise ReviewError(f"{path.name}: '{key}' must be a non-empty string")
        for obj in record["extracted_objects"]:
            if not (isinstance(obj, dict) and len(obj) == 1):
                raise ReviewError(f"{path.name}: extracted object {obj!r} must be a one-key mapping (kind: id)")
            ((kind, value),) = obj.items()
            if not all(isinstance(v, str) and v.strip() for v in (kind, value)):
                raise ReviewError(f"{path.name}: extracted object {obj!r} needs a non-empty kind and id")
        reviews.append({**record, "stem": path.name[: -len(SUFFIX)], "file": path.name})
    if not reviews:
        raise ReviewError(f"no review records in {reviews_dir}")
    return reviews


def slide_node(nodes: dict[str, dict[str, Any]], slide: str) -> str | None:
    """The node whose `slides` list holds this slide id or its base (prefix up to a dot)."""
    for node_id in sorted(nodes):
        for base in nodes[node_id]["slides"]:
            if slide == base or slide.startswith(f"{base}."):
                return node_id
    return None


def _node_ref(nodes: dict[str, dict[str, Any]], node_id: str | None) -> str:
    if node_id is None:
        return "— (no node record lists this slide)"
    return f'<a href="node/{nodes[node_id]["stem"]}.html">{escape(node_id)}</a>'


def _items(values: list[Any]) -> str:
    if not values:
        return "<p>—</p>"
    return "<ul>" + "".join(f"<li>{escape(str(v))}</li>" for v in values) + "</ul>"


def render_review(nodes: dict[str, dict[str, Any]], review: dict[str, Any]) -> list[str]:
    source, curated = str(review["source_slide"]), str(review["curated_slide"])
    objects = []
    for obj in review["extracted_objects"]:
        ((kind, value),) = obj.items()
        value = str(value)
        target = _node_ref(nodes, value) if value in nodes else f"{escape(value)} <em>(not a node record)</em>"
        objects.append(f"<tr><td>{escape(str(kind))}</td><td>{target}</td></tr>")
    return [
        f'<section class="review" id="{escape(review["stem"])}">',
        f"<h2>{escape(source)} &rarr; {escape(curated)}</h2>",
        (
            f'<p>Status: <strong class="status">{escape(str(review["status"]))}</strong> · '
            f'Reviewer: {escape(str(review["reviewer"]))} · '
            f'Record: <a href="../review/lineage/{escape(review["file"])}"><code>review/lineage/{escape(review["file"])}</code></a></p>'
        ),
        '<div class="grid">',
        '<div class="panel"><h3>Source slide</h3>',
        f"<p><code>{escape(source)}</code></p>",
        f"<p>Node: {_node_ref(nodes, slide_node(nodes, source))}</p>",
        "<h4>Lineage</h4>",
        _items(review["lineage"]),
        "</div>",
        '<div class="panel"><h3>Curated slide</h3>',
        f"<p><code>{escape(curated)}</code></p>",
        f"<p>Node: {_node_ref(nodes, slide_node(nodes, curated))}</p>",
        "</div>",
        "</div>",
        "<h3>Review comments</h3>",
        _items(review["comments"]),
        "<h3>Extracted semantic objects</h3>",
        "<table><thead><tr><th>Kind</th><th>Object</th></tr></thead><tbody>",
        *objects,
        "</tbody></table>",
        "</section>",
    ]


def render_page(nodes: dict[str, dict[str, Any]] | None = None, reviews: list[dict[str, Any]] | None = None) -> str:
    nodes = graph.load_nodes() if nodes is None else nodes
    reviews = load_reviews() if reviews is None else reviews
    body = [
        (
            "<style>.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}"
            ".panel{border:1px solid #334155;padding:10px}.review{border-top:1px solid #334155;margin-top:16px}</style>"
        ),
        "<h1>QPS Side-by-side Lineage Review</h1>",
        (
            "<p>Generated from <code>review/lineage/*.review.yaml</code>. Each review shows the source slide beside the "
            'curated slide, the source lineage, reviewer comments and extracted semantic objects. '
            '<a href="graph/index.html">Navigation graph</a> · <a href="../index.html">Deck navigator</a></p>'
        ),
        "<h2>Reviews</h2>",
        "<ul>",
        *(
            f'  <li><a href="#{escape(r["stem"])}">{escape(str(r["source_slide"]))} &rarr; '
            f'{escape(str(r["curated_slide"]))}</a> ({escape(str(r["status"]))})</li>'
            for r in reviews
        ),
        "</ul>",
    ]
    for review in reviews:
        body += render_review(nodes, review)
    return graph._page("QPS Lineage Review", body).replace(
        "generated by tools/build_qps_node_graph.py", "generated by tools/build_qps_review_page.py"
    )


def render_all() -> dict[str, str]:
    """All outputs, keyed by path relative to docs/qps-slide-system."""
    return {REVIEW_PATH: render_page()}


def stale_outputs(outputs: dict[str, str]) -> list[str]:
    stale = []
    for rel, text in outputs.items():
        path = SYSTEM / rel
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            stale.append(rel)
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if the committed page is stale")
    args = parser.parse_args(argv)
    outputs = render_all()
    if args.check:
        stale = stale_outputs(outputs)
        for rel in stale:
            print(f"stale: {rel}", file=sys.stderr)
        return 1 if stale else 0
    for rel, text in outputs.items():
        path = SYSTEM / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(outputs)} file(s) under {SYSTEM}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
