"""Render the helium-4 physics authority pin as a review page for the GISTAU portal.

Input:  governance/physics/HE4_PROPERTY_AUTHORITY_PIN.yaml
        src/gistau_ch15/properties/qplant_hepak_policy.py (CODEX routing, live)
Output: docs/gistau-ch15/physics_authority.html

The page is a pure function of those inputs (no timestamps), so the committed
HTML can be checked for staleness in CI. Regenerate with:
    PYTHONPATH=src python tools/render_physics_authority_review.py
"""
from __future__ import annotations

import html
import importlib.util
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "gistau-ch15" / "physics_authority.html"


def _load_tool():
    spec = importlib.util.spec_from_file_location(
        "verify_physics_authority_pin", REPO_ROOT / "tools" / "verify_physics_authority_pin.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _codex_router():
    src = str(REPO_ROOT / "src")
    if src not in sys.path:
        sys.path.append(src)
    from gistau_ch15.properties.qplant_hepak_policy import (
        governing_provider_for_temperature,
    )

    return governing_provider_for_temperature


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _band_svg(lo: float, hi: float, lam: float) -> str:
    """Two horizontal bars over 1.5-6 K: CODEX routing vs pinned ABACUS routing."""
    t0, t1 = 1.5, 6.0
    left, right, width = 110, 20, 640

    def x(t: float) -> float:
        return left + (min(max(t, t0), t1) - t0) / (t1 - t0) * (width - left - right)

    def bar(y: int, label: str, hepak_from: float, hepak_to: float) -> str:
        parts = [f'<text x="{left - 8}" y="{y + 15}" text-anchor="end" class="lbl">{_e(label)}</text>']
        parts.append(f'<rect x="{x(t0):.1f}" y="{y}" width="{x(t1) - x(t0):.1f}" height="22" rx="4" class="cp"/>')
        parts.append(
            f'<rect x="{x(hepak_from):.1f}" y="{y}" width="{x(hepak_to) - x(hepak_from):.1f}" height="22" rx="4" class="hp"/>'
        )
        return "".join(parts)

    ticks = []
    for t in (1.5, 2.0, 3.0, 4.0, 4.5, 5.0, 6.0):
        ticks.append(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="98" y2="104" class="ax"/>')
        ticks.append(f'<text x="{x(t):.1f}" y="118" text-anchor="middle" class="tk">{t:g}</text>')
    diverge = (
        f'<rect x="{x(t0):.1f}" y="18" width="{x(lo) - x(t0):.1f}" height="68" class="dv"/>'
        f'<text x="{(x(t0) + x(lo)) / 2:.1f}" y="12" text-anchor="middle" class="dvl">diverges</text>'
        if lo > t0
        else ""
    )
    return (
        f'<svg viewBox="0 0 {width} 150" width="100%" role="img" '
        f'aria-label="HEPAK-governed temperature band, CODEX versus ABACUS">'
        "<style>.lbl,.tk,.dvl,.lg{font:12px Arial,sans-serif;fill:var(--fg)}.tk{fill:var(--muted)}"
        ".cp{fill:var(--cp)}.hp{fill:var(--hp)}.ax{stroke:var(--muted)}"
        ".dv{fill:var(--bad);opacity:.14}.dvl{fill:var(--bad);font-weight:bold}.lam{stroke:var(--bad);stroke-dasharray:4 3}</style>"
        f"{diverge}"
        f"{bar(24, 'CODEX policy', t0, hi)}"
        f"{bar(60, 'ABACUS (pinned)', lo, hi)}"
        f'<line x1="{left}" x2="{width - right}" y1="98" y2="98" class="ax"/>'
        f'{"".join(ticks)}'
        f'<line x1="{x(lam):.1f}" x2="{x(lam):.1f}" y1="18" y2="92" class="lam"/>'
        f'<text x="{x(lam) + 4:.1f}" y="12" class="lg">λ {lam:g} K</text>'
        f'<rect x="{left}" y="130" width="12" height="10" rx="2" class="hp"/><text x="{left + 16}" y="139" class="lg">HEPAK governs</text>'
        f'<rect x="{left + 120}" y="130" width="12" height="10" rx="2" class="cp"/><text x="{left + 136}" y="139" class="lg">CoolProp governs</text>'
        f'<text x="{width - right}" y="139" text-anchor="end" class="lg">T [K]</text>'
        "</svg>"
    )


def _parts(pin: dict[str, Any] | None = None) -> tuple[str, str]:
    tool = _load_tool()
    pin = pin or tool.load_pin()
    tool.check_pin(pin)
    route = _codex_router()

    auth = pin["authority"]
    sha = auth["commit_sha"]
    consts = pin["pinned_constants"]
    lo, hi = consts["qplant_hepak_band_K"]
    parity = pin["policy_parity"]
    status_cls = "ok" if parity["status"] == "PARITY" else "warn"
    probes = ", ".join(f"{x:g}" for x in parity["diverging_probes_K"])
    if parity["status"] == "PARITY":
        # Probe agreement is technical parity, not approval of the pin: the
        # reviewer still accepts the authority commit explicitly.
        decision_cls, decision_title = "active", "Routing in parity; pin awaits your acceptance"
        decision_text = (
            "CODEX and the pinned ABACUS routing agree at every recorded probe: HEPAK governs "
            f"0 &lt; T &le; {hi:g} K, including He-II below the lambda point, and CoolProp governs above. "
            f"Agreement at the probes is not approval: confirm with the checklist that ABACUS "
            f"{_e(sha[:12])} is the provider version CODEX should consume."
        )
    else:
        # Authority-neutral: the remediation comes from the pin, never from a
        # default that tells the governing repository to follow the consumer.
        decision_cls, decision_title = "warning", "Routing diverges; decision needed"
        resolution = parity.get("resolution")
        decision_text = (
            f"CODEX and the pinned ABACUS routing disagree at {probes} K. "
            + (
                f"Recorded resolution: {_e(resolution)}"
                if resolution
                else "No resolution is recorded in the pin. ABACUS governs helium physics, so first decide "
                "whether the CODEX mirror is stale or ABACUS should change, then record that as "
                "policy_parity.resolution."
            )
        )

    file_rows = "".join(
        "<tr>"
        f'<td><a href="https://github.com/{_e(auth["repository"])}/blob/{_e(sha)}/{_e(f["path"])}">{_e(f["path"])}</a></td>'
        f"<td>{_e(f['role'])}</td>"
        f"<td><code>{_e(f['sha256'][:12])}…</code></td>"
        "</tr>"
        for f in pin["pinned_files"]
    )
    probe_rows = []
    for t in parity["probes_K"]:
        codex = route(t)
        abacus = "HEPAK" if lo <= t <= hi else "COOLPROP"
        same = codex == abacus
        probe_rows.append(
            f"<tr><td>{t:g}</td><td>{_e(codex)}</td><td>{_e(abacus)}</td>"
            f'<td class="{"green-text" if same else "red-text"}">{"same" if same else "differs"}</td></tr>'
        )
    role_rows = "".join(
        f"<tr><td><code>{_e(path)}</code></td><td>{_e(role)}</td></tr>" for path, role in pin["local_roles"].items()
    )
    checklist = [
        f"ABACUS commit <code>{_e(sha[:12])}</code> ({_e(auth['commit_date'])}) is the provider version you intend CODEX to consume.",
        f"Pinned constants match ABACUS: λ = {consts['lambda_point_K']:g} K, governed envelope {consts['governed_envelope_K'][0]:g}–{consts['governed_envelope_K'][1]:g} K, QPLANT HEPAK band {lo:g}–{hi:g} K.",
        "Every GISTAU backend is CROSSCHECK_ONLY and the NIST fixture is VALIDATION_REFERENCE_ONLY: nothing in CODEX governs helium physics.",
        f"Policy divergence is acceptable as recorded ({_e(parity['status'])}) until ABACUS adopts the CODEX rule.",
        f"Runtime dependency is <code>{_e(auth['runtime_dependency'])}</code>.",
    ]
    checklist_html = "".join(
        f'<li><label for="chk-{i}"><input type="checkbox" id="chk-{i}"> <span>{item}</span></label></li>'
        for i, item in enumerate(checklist, 1)
    )

    head = """<title>Physics Authority Review</title>
<style>
/* Layout: GISTAU portal cards (black rule header, bordered cards, green/red status) on a two-column grid that stacks on phones. */
:root {
  --bg: #ffffff; --panel: #ffffff; --fg: #111111; --muted: #5a5a5a; --line: #111111;
  --ok: #007a33; --bad: #b00020; --warn-bg: #fff4e5; --warn-line: #b00020;
  --hp: #2e9d55; --cp: #9fbfe3; --font: Arial, "Helvetica Neue", Helvetica, sans-serif; --mono: Consolas, "Liberation Mono", monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #181421; --panel: #241d33; --fg: #f5f2ff; --muted: #cfc2ef; --line: #8f7abd;
  --ok: #9cf2be; --bad: #ffb3b3; --warn-bg: #3b2a00; --warn-line: #c89b00; --hp: #5fd08d; --cp: #3d5f8a; color-scheme: dark;
} }
:root[data-theme="dark"] {
  --bg: #181421; --panel: #241d33; --fg: #f5f2ff; --muted: #cfc2ef; --line: #8f7abd;
  --ok: #9cf2be; --bad: #ffb3b3; --warn-bg: #3b2a00; --warn-line: #c89b00; --hp: #5fd08d; --cp: #3d5f8a; color-scheme: dark;
}
body { background: var(--bg); color: var(--fg); font-family: var(--font); margin: 0; line-height: 1.45; }
.page { padding-inline: 16px; padding-block: 0 24px; max-width: 1100px; margin-inline: auto; }
.topbar { padding-block: 16px; border-bottom: 4px solid var(--line); }
.topbar h1 { margin: 0 0 6px; font-size: 1.5rem; text-wrap: balance; }
.topbar p { margin: 0; color: var(--muted); max-width: 65ch; }
.strip { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.pill { border: 2px solid var(--line); border-radius: 999px; padding: 3px 10px; font-weight: bold; font-size: .85rem; }
.pill.ok { border-color: var(--ok); color: var(--ok); } .pill.warn { border-color: var(--warn-line); color: var(--bad); }
.layout { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap: 16px; padding-block: 16px; }
.card { border: 3px solid var(--line); border-radius: 12px; padding: 16px; background: var(--panel); min-width: 0; }
.card h2 { margin: 0 0 8px; font-size: 1.1rem; } .card p { margin: 0 0 10px; max-width: 70ch; }
.card.active { border-color: var(--ok); } .card.warning { border-color: var(--warn-line); background: var(--warn-bg); }
.full { grid-column: 1 / -1; }
.wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; font-size: .9rem; }
th, td { border: 1px solid var(--line); padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: var(--fg); color: var(--bg); }
td a { color: var(--fg); word-break: break-all; } a:focus-visible, input:focus-visible { outline: 3px solid var(--ok); outline-offset: 2px; }
code { font-family: var(--mono); font-size: .9em; overflow-wrap: anywhere; }
.green-text { color: var(--ok); font-weight: bold; } .red-text { color: var(--bad); font-weight: bold; }
.checklist { list-style: none; padding: 0; margin: 0; display: grid; gap: 6px; }
.checklist li { padding-block: 6px; border-bottom: 1px solid var(--muted); }
.checklist label { display: flex; gap: 8px; align-items: flex-start; }
.checklist input { margin-top: 3px; flex: none; }
small { color: var(--muted); }
</style>"""
    body = f"""<div class="page">
<header class="topbar">
<h1>Helium-4 physics authority — review</h1>
<p>CODEX consumes helium-4 physics from ABACUS by exact commit. GISTAU's local backends cross-check it and never govern.</p>
<div class="strip">
<span class="pill ok">Authority: {_e(auth['repository'])} @ {_e(sha[:12])}</span>
<span class="pill">{_e(auth['runtime_dependency'])}</span>
<span class="pill {status_cls}">Policy parity: {_e(parity['status'])}</span>
<span class="pill">Meta checksum <code>{_e(pin['meta_checksum_sha256'][:16])}…</code></span>
</div>
</header>
<main class="layout">
<section class="card {decision_cls} full" id="decision">
<h2>{decision_title}</h2>
<p>{decision_text}</p>
<div class="wrap">{_band_svg(lo, hi, consts['lambda_point_K'])}</div>
</section>
<section class="card active" id="checklist">
<h2>Reviewer checklist</h2>
<ul class="checklist">{checklist_html}</ul>
<p><small>Ticks are for your own pass through the page and are not saved.</small></p>
</section>
<section class="card" id="roles">
<h2>Who governs what in CODEX</h2>
<div class="wrap"><table><thead><tr><th>Path</th><th>Role</th></tr></thead><tbody>
<tr><td><code>{_e(auth['repository'])}</code> {_e(auth['capability'])}</td><td class="green-text">GOVERNING</td></tr>
{role_rows}
<tr><td><code>nist_gistau_reference</code></td><td>VALIDATION_REFERENCE_ONLY</td></tr>
</tbody></table></div>
</section>
<section class="card" id="probes">
<h2>Routing probes</h2>
<p>Which provider governs at each probe temperature, recomputed from code.</p>
<div class="wrap"><table><thead><tr><th>T [K]</th><th>CODEX</th><th>ABACUS (pinned)</th><th>Result</th></tr></thead>
<tbody>{"".join(probe_rows)}</tbody></table></div>
</section>
<section class="card full" id="files">
<h2>Pinned ABACUS files</h2>
<p>Each file is checked by sha256 against an ABACUS checkout; a different HEAD or content is rejected as stale.</p>
<div class="wrap"><table><thead><tr><th>File at {_e(sha[:12])}</th><th>Role</th><th>sha256</th></tr></thead>
<tbody>{file_rows}</tbody></table></div>
</section>
<section class="card full" id="provenance">
<h2>How this page is made</h2>
<p>Generated from <code>governance/physics/HE4_PROPERTY_AUTHORITY_PIN.yaml</code> and the live CODEX routing by
<code>tools/render_physics_authority_review.py</code>. Verify the pin against ABACUS with
<code>python tools/verify_physics_authority_pin.py --abacus PATH</code>. A test fails if this page is out of date.</p>
<p><a href="index.html">Back to the GISTAU portal</a></p>
</section>
</main>
</div>
"""
    return head, body


def render_fragment(pin: dict[str, Any] | None = None) -> str:
    """Head + body without a document skeleton (for an Artifact preview)."""
    head, body = _parts(pin)
    return head + "\n" + body.replace('<p><a href="index.html">Back to the GISTAU portal</a></p>\n', "")


def render(pin: dict[str, Any] | None = None) -> str:
    head, body = _parts(pin)
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>\n'
        f"{head}\n</head>\n<body>\n{body}</body></html>\n"
    )


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
