"""Render the public SPINE-core / COV-01 status page (ADR-0002).

Reads the committed receipts/spine/SPINE_GATE_RECEIPT.json and
spine/SPINE_MANIFEST.yaml and writes docs/spine/index.html, which GitHub
Pages publishes with the rest of docs/. Output is a pure function of those
two inputs (no clock, no network), so CI can regenerate and diff it.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
GH = "https://github.com/GBOGEB/CODEX"

STYLE = """
:root{color-scheme:light;--bg:#f6f8fb;--panel:#fff;--ink:#132033;--muted:#56657a;--brand:#2756d8;--ok:#0f7b45;--warn:#a05a00;--bad:#b3261e;--line:#d9e1ef;--soft:#eef3ff;--okbg:#e8f7ef;--warnbg:#fff4df;--badbg:#fde8e6}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--bg:#0e1522;--panel:#151f31;--ink:#e3e9f3;--muted:#9aa8bd;--brand:#8aa8ff;--ok:#6fd3a0;--warn:#f0c068;--bad:#ff8f86;--line:#2a3750;--soft:#1c2945;--okbg:#123326;--warnbg:#3a2c0f;--badbg:#3d1714}}
*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5}
header{background:linear-gradient(135deg,#12264d,#2756d8);color:#fff;padding:2rem 1rem}
main{max-width:1120px;margin:0 auto;padding:1.25rem}header main{padding-block:0}
header p{max-width:65ch;margin:.4rem 0 0}nav{display:flex;gap:.75rem;flex-wrap:wrap;margin-top:1rem}
nav a{color:#fff;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.35);padding:.55rem .8rem;border-radius:.75rem;text-decoration:none}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:1rem}
.card{grid-column:span 3;background:var(--panel);border:1px solid var(--line);border-radius:1rem;padding:1rem;min-width:0}
.wide{grid-column:span 12}.half{grid-column:span 6}
.metric{font-size:1.9rem;font-weight:700;color:var(--brand);font-variant-numeric:tabular-nums}.label{color:var(--muted);font-size:.9rem}
.status{display:inline-block;border-radius:999px;padding:.15rem .6rem;font-weight:700;font-size:.78rem;white-space:nowrap}
.ready{background:var(--okbg);color:var(--ok)}.partial{background:var(--warnbg);color:var(--warn)}.blocked{background:var(--badbg);color:var(--bad)}
h2{font-size:1.15rem;margin:0 0 .6rem}a{color:var(--brand)}
.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:.9rem}
th,td{padding:.5rem .6rem;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{background:var(--soft)}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.85em;overflow-wrap:anywhere}
.note{border-left:4px solid var(--brand);padding:.7rem .9rem;background:var(--soft);border-radius:.5rem;max-width:80ch}
ol,ul{margin:.2rem 0;padding-left:1.3rem}li{margin:.25rem 0}
details summary{cursor:pointer;font-weight:700}
@media(max-width:760px){.card,.half{grid-column:span 6}}@media(max-width:480px){.card,.half{grid-column:span 12}}
"""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render(receipt: dict, manifest: dict) -> str:
    counts = receipt["counts"]
    verdict = receipt["verdict"]
    vclass = "ready" if verdict == "PASS" else "blocked"
    by_area: dict[str, list[dict]] = defaultdict(list)
    for f in receipt["files"]:
        by_area[f["path"].split("/")[0]].append(f)

    area_rows = "".join(
        f"<tr><td><code>{esc(area)}/</code></td><td>{len(files)}</td>"
        f"<td>{sum(1 for x in files if x['status'] == 'CLEAN')}</td>"
        f"<td>{sum(x['bytes'] for x in files):,}</td></tr>"
        for area, files in sorted(by_area.items())
    )
    file_rows = "".join(
        f"<tr><td><code>{esc(f['path'])}</code>"
        + (f" <span class=\"label\">overlay</span>" if f.get("overlay_source") else "")
        + f"</td><td><code>{esc(f['sha256'][:16])}</code></td>"
        f"<td><span class=\"status {'ready' if f['status'] == 'CLEAN' else 'blocked'}\">{esc(f['status'])}</span></td></tr>"
        for f in receipt["files"]
    )
    smoke_rows = "".join(
        f"<tr><td><code>{esc(c['name'])}</code></td><td><code>{esc(c['cwd'])}</code></td>"
        f"<td>{esc(c.get('expect', 'pass'))}</td></tr>"
        for c in manifest.get("smoke") or []
    )
    held = [e for e in manifest.get("exclude", []) if e in HELD_BACK]
    held_items = "".join(f"<li><code>{esc(h)}</code></li>" for h in held)
    missing = receipt.get("missing_include_patterns") or []
    missing_html = (
        "<p class=\"note\">Include patterns that matched nothing: "
        + ", ".join(f"<code>{esc(m)}</code>" for m in missing) + "</p>"
        if missing else ""
    )

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SPINE-core Gate</title><style>{STYLE}</style></head><body>
<header><main><h1>SPINE-core Gate</h1>
<p>The public backbone extracted from CODEX (ADR-0002) and the COV-01 Coverity fix. Every file below passed a scan for private terms and secrets, an import-closure check, and an isolated smoke run before admission.</p>
<nav><a href="../index.html">Runtime Portal</a><a href="{GH}/actions/workflows/spine-gate.yml">Latest gate runs</a><a href="{GH}/blob/main/governance/adr/ADR-0002-spine-core-public-backbone.md">ADR-0002</a><a href="{GH}/blob/main/receipts/spine/SPINE_GATE_RECEIPT.json">Receipt JSON</a></nav></main></header>
<main>
<section class="grid">
<article class="card"><div class="label">Gate verdict</div><div class="metric">{esc(verdict)}</div><span class="status {vclass}">receipt {esc(receipt['generated_utc'])}</span></article>
<article class="card"><div class="label">Files admitted</div><div class="metric">{counts['admitted']}</div><span class="status ready">{counts['clean']} clean</span></article>
<article class="card"><div class="label">Blocked</div><div class="metric">{counts['blocked']}</div><span class="status {'ready' if counts['blocked'] == 0 else 'blocked'}">term / secret / import</span></article>
<article class="card"><div class="label">Smoke cases</div><div class="metric">{len(manifest.get('smoke') or [])}</div><span class="status ready">run in CI on every change</span></article>
<article class="card wide"><h2>Admitted tree</h2><p><code>{esc(receipt['admitted_tree_sha256'])}</code></p><p class="label">SHA-256 over every admitted path and file hash. The <a href="{GH}/actions/workflows/spine-gate.yml">spine-gate</a> workflow fails if this page, the receipt, or the tree drift apart.</p>{missing_html}</article>
<article class="card half"><h2>COV-01 Coverity Scan</h2>
<p><span class="status partial">DoV withheld</span> The scan failed with HTTP 401 because no token was configured. No analysis ran. A missing token now reports <strong>WITHHELD</strong>, never PASS.</p>
<ol><li>Name the GBOGEB repo the failing run came from.</li><li>Register it on scan.coverity.com under the exact repository name.</li><li>Set <code>COVERITY_SCAN_TOKEN</code> and call <code>coverity-scan-reusable.yml</code>.</li></ol>
<p><a href="{GH}/blob/main/.github/workflows/coverity-scan-reusable.yml">Reusable workflow</a> · <a href="{GH}/blob/main/triage/COV-01_COVERITY_CREDENTIAL_PREANALYSIS.yaml">Triage record</a></p></article>
<article class="card half"><h2>Held back for redaction</h2><p class="label">Blocked on the first gate run because they name the private project or a corporate system.</p><ul>{held_items}</ul><p class="label">Contract ingestion, corporate integrations, project-authority schemas and handover state are never admitted.</p></article>
<article class="card wide"><h2>By area</h2><div class="scroll"><table><thead><tr><th>Area</th><th>Files</th><th>Clean</th><th>Bytes</th></tr></thead><tbody>{area_rows}</tbody></table></div></article>
<article class="card wide"><h2>Smoke cases</h2><p class="label">Executed in a staged tree containing only the admitted files. Results are in the latest spine-gate run.</p><div class="scroll"><table><thead><tr><th>Case</th><th>Directory</th><th>Expect</th></tr></thead><tbody>{smoke_rows}</tbody></table></div></article>
<article class="card wide"><details><summary>All {counts['admitted']} admitted files</summary><div class="scroll"><table><thead><tr><th>Path</th><th>SHA-256 (prefix)</th><th>Status</th></tr></thead><tbody>{file_rows}</tbody></table></div></details></article>
<article class="card wide"><p class="note">Non-compensating: gate, smoke and scan status never compensates, reorders or substitutes W248, GT_BDQ_0..9, the v6 release train, or any QPS first-red. A WITHHELD scan is not a green signal.</p></article>
</section></main></body></html>
"""


HELD_BACK = {
    "federation_runtime/engines/phase0_orchestration.py",
    "pca_engine/README.md",
    "pca_engine/docs/EMPIRICAL_CONTROL_PROVIDER.md",
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=REPO_ROOT)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    root = a.root.resolve()
    receipt = json.loads((root / "receipts" / "spine" / "SPINE_GATE_RECEIPT.json").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((root / "spine" / "SPINE_MANIFEST.yaml").read_text(encoding="utf-8"))
    out = a.out or root / "docs" / "spine" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(receipt, manifest), encoding="utf-8")
    print(f"wrote {out.relative_to(root) if out.is_relative_to(root) else out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
