"""Global mesh semantic-book projection runtime.

Consumes a mesh node JSON document plus a view manifest and emits synchronized
Markdown, HTML book/flow, graph JSON and a deterministic receipt. The runtime is
presentation-only: it never changes source authority or evidence classification.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

RENDERER_VERSION = "global-mesh-book-runtime/1.0.0"
BOUNDARY_ORDER = ["GLOBAL_HIVE", "DOMAIN", "PROJECT", "REPO", "ARTEFACT", "SECTION", "ATOM"]
DEPTH_LABELS = {0: "ATOM", 1: "EXECUTIVE", 2: "SUMMARY", 3: "ENGINEERING", 4: "EVIDENCE", 5: "TRACE"}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


@dataclass(frozen=True)
class View:
    mode: str
    boundary: str
    lens: str
    depth: int
    status: tuple[str, ...]
    evidence_class: tuple[str, ...]
    render: Dict[str, Any]

    @classmethod
    def from_manifest(cls, manifest: Dict[str, Any]) -> "View":
        if manifest.get("schema_version") != "global-mesh-view-manifest/1.0.0":
            raise ValueError("unsupported view manifest schema")
        boundary = manifest["boundary"]
        if boundary not in BOUNDARY_ORDER:
            raise ValueError(f"unknown boundary: {boundary}")
        depth = int(manifest["depth"])
        if not 0 <= depth <= 5:
            raise ValueError("depth must be 0..5")
        filters = manifest.get("filters", {})
        return cls(
            mode=manifest["mode"],
            boundary=boundary,
            lens=manifest["lens"],
            depth=depth,
            status=tuple(filters.get("status", [])),
            evidence_class=tuple(filters.get("evidence_class", [])),
            render=manifest.get("render", {}),
        )


class GlobalMeshBookRuntime:
    def __init__(self, nodes: Iterable[Dict[str, Any]], manifest: Dict[str, Any]):
        self.nodes = list(nodes)
        self.manifest = manifest
        self.view = View.from_manifest(manifest)
        self._validate_nodes()

    def _validate_nodes(self) -> None:
        ids = set()
        for node in self.nodes:
            for key in ("id", "title", "depth", "boundary", "lens", "content"):
                if key not in node:
                    raise ValueError(f"node missing required field {key}: {node}")
            if node["id"] in ids:
                raise ValueError(f"duplicate node id: {node['id']}")
            ids.add(node["id"])
            if node["boundary"] not in BOUNDARY_ORDER:
                raise ValueError(f"unknown node boundary: {node['boundary']}")
            if not 0 <= int(node["depth"]) <= 5:
                raise ValueError(f"invalid node depth: {node['id']}")

    def project(self) -> List[Dict[str, Any]]:
        boundary_limit = BOUNDARY_ORDER.index(self.view.boundary)
        visible: List[Dict[str, Any]] = []
        for node in self.nodes:
            if int(node["depth"]) > self.view.depth:
                continue
            if BOUNDARY_ORDER.index(node["boundary"]) > boundary_limit:
                continue
            if node["lens"] not in (self.view.lens, "NARRATIVE") and self.view.lens != "NARRATIVE":
                continue
            if self.view.status and node.get("status", "UNKNOWN") not in self.view.status:
                continue
            if self.view.evidence_class and node.get("evidence_class", "UNKNOWN") not in self.view.evidence_class:
                continue
            visible.append(node)
        return visible

    def to_markdown(self, nodes: List[Dict[str, Any]]) -> str:
        lines = [f"# Global Mesh Book — {self.view.boundary} / {self.view.lens} / L{self.view.depth}", ""]
        for node in nodes:
            heading = min(6, int(node["depth"]) + 1)
            lines += [f"{'#' * heading} {node['title']}", "", node["content"].rstrip(), ""]
            meta = []
            for k in ("status", "evidence_class", "source_sha", "freshness_timestamp", "next_action", "blocking_atom"):
                if node.get(k) not in (None, ""):
                    meta.append(f"{k}={node[k]}")
            if meta:
                lines += [f"> mesh: {' | '.join(meta)}", ""]
        return "\n".join(lines).rstrip() + "\n"

    def to_graph(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        visible_ids = {n["id"] for n in nodes}
        return {
            "schema_version": "global-mesh-graph-projection/1.0.0",
            "view": {"mode": self.view.mode, "boundary": self.view.boundary, "lens": self.view.lens, "depth": self.view.depth},
            "nodes": [{k: n.get(k) for k in ("id", "title", "depth", "boundary", "lens", "status", "evidence_class", "source_sha")} for n in nodes],
            "edges": [{"from": n["parent_id"], "to": n["id"], "kind": "EXPANDS_TO"} for n in nodes if n.get("parent_id") in visible_ids],
        }

    def to_html(self, nodes: List[Dict[str, Any]]) -> str:
        blocks = []
        for n in nodes:
            meta = " ".join(
                f'<span><b>{html.escape(k)}</b> {html.escape(str(n[k]))}</span>'
                for k in ("status", "evidence_class", "source_sha") if n.get(k)
            )
            blocks.append(
                f'<section class="node d{int(n["depth"])}" data-depth="{int(n["depth"])}" '
                f'data-boundary="{html.escape(n["boundary"])}" data-lens="{html.escape(n["lens"])}">'
                f'<h2>{html.escape(n["title"])}</h2><div class="content"><pre>{html.escape(n["content"].rstrip())}</pre></div>'
                f'<footer>{meta}</footer></section>'
            )
        mode_class = self.view.mode.lower()
        return f'''<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Global Mesh Book</title>
<style>
:root{{--page-width:210mm;--paper:#fff;--ink:#171717;--muted:#666;--line:#ddd}}
*{{box-sizing:border-box}} body{{margin:0;background:#ececec;color:var(--ink);font:15px/1.55 system-ui,sans-serif}}
.toolbar{{position:sticky;top:0;z-index:5;padding:10px 16px;background:#111;color:#fff;display:flex;gap:14px;align-items:center}}
.toolbar input{{width:180px}} main.book{{width:var(--page-width);max-width:calc(100vw - 24px);margin:24px auto;background:var(--paper);padding:20mm;box-shadow:0 2px 18px #0002}}
main.flow{{max-width:1100px;margin:24px auto;background:var(--paper);padding:36px}} .node{{border-top:1px solid var(--line);padding:18px 0}}
.node h2{{margin:0 0 8px;font-size:1.15rem}} .node pre{{white-space:pre-wrap;font:inherit;margin:0}} .node footer{{margin-top:8px;color:var(--muted);display:flex;gap:12px;flex-wrap:wrap;font-size:.78rem}}
.d0 h2{{font-size:1.5rem}} .d1 h2{{font-size:1.35rem}} .d4,.d5{{margin-left:18px}}
@media print{{body{{background:#fff}} .toolbar{{display:none}} main.book,main.flow{{width:auto;max-width:none;margin:0;box-shadow:none;padding:14mm}} .node{{break-inside:avoid}}}}
</style></head><body>
<div class="toolbar"><strong>Gloob / Global Mesh</strong><label>Depth <input id="depth" type="range" min="0" max="5" value="{self.view.depth}"></label><span id="label">L{self.view.depth} {DEPTH_LABELS[self.view.depth]}</span><button onclick="window.print()">Print / PDF</button></div>
<main class="{mode_class if mode_class in ('book','flow') else 'book'}">{''.join(blocks)}</main>
<script>const r=document.getElementById('depth'),l=document.getElementById('label');const labels={json.dumps(DEPTH_LABELS)};r.oninput=()=>{{const d=+r.value;l.textContent=`L${{d}} ${{labels[d]}}`;document.querySelectorAll('.node').forEach(n=>n.hidden=+n.dataset.depth>d)}};</script>
</body></html>'''

    def execute(self, out_dir: Path) -> Dict[str, Any]:
        out_dir.mkdir(parents=True, exist_ok=True)
        projected = self.project()
        markdown = self.to_markdown(projected)
        graph = self.to_graph(projected)
        html_text = self.to_html(projected)
        source_digest = _sha256_bytes(_canonical_json(self.nodes))
        manifest_digest = _sha256_bytes(_canonical_json(self.manifest))
        identity = _sha256_bytes(f"{source_digest}:{manifest_digest}:{RENDERER_VERSION}".encode())
        receipt = {
            "schema_version": "global-mesh-render-receipt/1.0.0",
            "renderer_version": RENDERER_VERSION,
            "source_sha256": source_digest,
            "manifest_sha256": manifest_digest,
            "artifact_identity_sha256": identity,
            "visible_nodes": len(projected),
            "view": {"mode": self.view.mode, "boundary": self.view.boundary, "lens": self.view.lens, "depth": self.view.depth},
        }
        (out_dir / "book.md").write_text(markdown, encoding="utf-8")
        (out_dir / "book.html").write_text(html_text, encoding="utf-8")
        (out_dir / "graph.json").write_text(json.dumps(graph, indent=2), encoding="utf-8")
        (out_dir / "render_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return receipt


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--nodes", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    nodes_doc = json.loads(args.nodes.read_text(encoding="utf-8"))
    nodes = nodes_doc["nodes"] if isinstance(nodes_doc, dict) else nodes_doc
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    receipt = GlobalMeshBookRuntime(nodes, manifest).execute(args.out)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
