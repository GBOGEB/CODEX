"""Render the GISTAU book navigator and the Chapter 3 page from committed sources.

Sources (no hand-typed figures):
  GISTAU/sources/master/source_manifest.yaml       original book identity, page offsets, chapters
  docs/gistau-ch3/data/claude_cycle_benchmarks.json Ch3 Claude-cycle benchmarks and open items
  docs/gistau-ch15/data/l1_validation_results.json  Ch15 L1 record (CI)
  governance/physics/CH15_CANONICAL_VALIDATION.yaml Ch15 gate (checked / excluded / errata)
  docs/gistau-ch15/index.html                       Ch15 portal page list (link labels)
Outputs:
  docs/gistau/index.html       book navigator (canonical entry for Ch3 and Ch15)
  docs/gistau-ch3/index.html   Chapter 3 Claude-cycle benchmarks

Deterministic; tests fail if the committed pages are stale. Regenerate with:
  python tools/render_gistau_book.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "GISTAU" / "sources" / "master" / "source_manifest.yaml"
CH3_DATA = REPO_ROOT / "docs" / "gistau-ch3" / "data" / "claude_cycle_benchmarks.json"
L1_RECORD = REPO_ROOT / "docs" / "gistau-ch15" / "data" / "l1_validation_results.json"
GATE = REPO_ROOT / "governance" / "physics" / "CH15_CANONICAL_VALIDATION.yaml"
CH15_PORTAL = REPO_ROOT / "docs" / "gistau-ch15" / "index.html"
OUT_BOOK = REPO_ROOT / "docs" / "gistau" / "index.html"
OUT_CH3 = REPO_ROOT / "docs" / "gistau-ch3" / "index.html"

UNITS = (
    ("_g_s", "g/s"), ("_kw", "kW"), ("_w_k", "W/K"), ("_w", "W"), ("_k", "K"), ("_bar", "bar"),
    ("_pct", "%"), ("_pct_carnot", "% Carnot"),
)
CHAPTER_TITLES = {
    "ch3_basic_thermodynamic_cycles": "Chapter 3 · Basic Thermodynamic Cycles",
    "ch3_5_claude_cycle": "§3.5 · The Claude cycle",
    "ch15_cryo_tool_box": "Chapter 15 · The Cryo Tool Box",
}


def _e(x: Any) -> str:
    return html.escape(str(x), quote=True)


def _unit(key: str) -> str:
    for suffix, unit in sorted(UNITS, key=lambda u: -len(u[0])):
        if key.endswith(suffix):
            return unit
    return ""


def _label(key: str) -> str:
    base = key
    for suffix, _ in sorted(UNITS, key=lambda u: -len(u[0])):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    words = []
    for w in base.split("_"):
        if w == "dt":
            w = "ΔT"
        elif re.fullmatch(r"(hx\d*|jt|lp|hp|lmtd|ua|ln2|t\d*|q|p)", w):
            w = w.upper()
        words.append(w)
    text = " ".join(words).strip()
    return text[:1].upper() + text[1:]


def _flatten(d: dict[str, Any], prefix: str = "") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = []
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            rows.extend(_flatten(v, f"{key}_"))
        else:
            rows.append((key, v))
    return rows


def _fmt(v: Any) -> str:
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


def _pdf_page(book_page: int, offset: int) -> int:
    return book_page + offset


def _table(rows: list[tuple[str, Any]]) -> str:
    trs = "".join(
        f"<tr><td>{_e(_label(k))}</td><td class='num'>{_e(_fmt(v))}</td><td>{_e(_unit(k))}</td></tr>"
        if not isinstance(v, str) else f"<tr><td>{_e(_label(k))}</td><td colspan='2'>{_e(v)}</td></tr>"
        for k, v in rows
    )
    return f"<div class='wrap'><table><thead><tr><th>Quantity</th><th>Book value</th><th>Unit</th></tr></thead><tbody>{trs}</tbody></table></div>"


CSS = """
:root {
  --bg: #ffffff; --panel: #ffffff; --fg: #111111; --muted: #5a5a5a; --line: #562873; --soft: #d9d9d9;
  --accent: #984A9C; --ok: #007a33; --open: #8a5a00; --open-bg: #fff4e5; --th-fg: #ffffff;
  --font: Arial, "Helvetica Neue", Helvetica, sans-serif; --mono: Consolas, "Liberation Mono", monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #181421; --panel: #241d33; --fg: #f5f2ff; --muted: #cfc2ef; --line: #b79ae0; --soft: #3a3150;
  --accent: #e0a6e4; --ok: #9cf2be; --open: #ffd27a; --open-bg: #3b2a00; --th-fg: #181421; color-scheme: dark;
} }
:root[data-theme="dark"] {
  --bg: #181421; --panel: #241d33; --fg: #f5f2ff; --muted: #cfc2ef; --line: #b79ae0; --soft: #3a3150;
  --accent: #e0a6e4; --ok: #9cf2be; --open: #ffd27a; --open-bg: #3b2a00; --th-fg: #181421; color-scheme: dark;
}
body { background: var(--bg); color: var(--fg); font-family: var(--font); margin: 0; line-height: 1.45; }
.page { padding-inline: 16px; padding-block: 0 24px; max-width: 1100px; margin-inline: auto; }
.topbar { padding-block: 16px; border-bottom: 4px solid var(--line); }
.crumbs { font-size: .85rem; color: var(--muted); margin: 0 0 6px; }
.topbar h1 { margin: 0 0 6px; font-size: 1.5rem; text-wrap: balance; }
.topbar p { margin: 0; color: var(--muted); max-width: 75ch; }
h2 { font-size: 1.15rem; margin: 22px 0 8px; }
.grid { display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr)); }
.card { border: 3px solid var(--line); border-radius: 12px; padding: 14px 16px; background: var(--panel); min-width: 0; }
.card h3 { margin: 0 0 4px; font-size: 1.05rem; }
.card.open { border-color: var(--open); background: var(--open-bg); }
.ref { color: var(--muted); font-size: .85rem; margin: 0 0 6px; }
.pill { display: inline-block; border: 2px solid var(--accent); border-radius: 999px; padding: 1px 9px; font-size: .8rem; font-weight: bold; margin: 2px 4px 2px 0; }
.pill.ok { border-color: var(--ok); color: var(--ok); }
ul.links { margin: 8px 0 0; padding-left: 18px; } ul.links li { margin: 3px 0; }
.wrap { overflow-x: auto; margin-top: 10px; }
table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; font-size: .88rem; }
th, td { border: 1px solid var(--soft); padding: 5px 8px; text-align: left; }
th { background: var(--line); color: var(--th-fg); border-color: var(--line); white-space: nowrap; } td.num { text-align: right; white-space: nowrap; }
.note { margin: 8px 0 0; max-width: 80ch; }
.conv { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center; margin-top: 8px; }
.conv input { font: inherit; width: 7em; padding: 4px 6px; border: 2px solid var(--line); border-radius: 6px; background: var(--bg); color: var(--fg); }
.conv output { font-weight: bold; }
.foot { margin-top: 22px; color: var(--muted); font-size: .88rem; max-width: 80ch; }
code { font-family: var(--mono); font-size: .9em; overflow-wrap: anywhere; } a { color: var(--fg); }
a:focus-visible, input:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
"""


def _shell(title: str, crumbs: str, h1: str, lead: str, body: str, foot: str, script: str = "") -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{_e(title)}</title>
<style>{CSS}</style></head>
<body><main class="page">
<header class="topbar"><p class="crumbs">{crumbs}</p><h1>{_e(h1)}</h1><p>{lead}</p></header>
{body}
<p class="foot">{foot}</p>
</main>{script}</body></html>
"""


def _load() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], list[tuple[str, str]]]:
    book = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["original_book"]
    ch3 = json.loads(CH3_DATA.read_text(encoding="utf-8"))
    rec = json.loads(L1_RECORD.read_text(encoding="utf-8"))
    gate = yaml.safe_load(GATE.read_text(encoding="utf-8"))
    portal = [
        (h, html.unescape(text))
        for h, text in re.findall(r"<a [^>]*href='([^'#:]+\.html)'[^>]*>([^<]+)</a>", CH15_PORTAL.read_text(encoding="utf-8"))
        if not h.startswith("..")
    ]
    return book, ch3, rec, gate, portal


def render_ch3() -> str:
    book, ch3, _, _, _ = _load()
    off = book["pdf_page_offset"]["ch3"]
    benches = ch3["benchmarks"]
    by_id = {b["benchmark_id"]: b for b in benches}
    cards = []
    for b in benches:
        pages = b.get("page") or b.get("pages", "")
        figs = b.get("figure") or ", ".join(b.get("figures", []))
        if isinstance(pages, int):
            pdf = f"PDF {_pdf_page(pages, off)}"
        else:
            lo, _, hi = str(pages).partition("-")
            pdf = f"PDF {_pdf_page(int(lo), off)}–{_pdf_page(int(hi or lo), off)}" if lo.isdigit() else ""
        ref = " · ".join(x for x in (f"§{b['section']}", figs, f"p. {pages}" if pages else "", pdf) if x)
        body = f"<p class='ref'>{_e(ref)}</p>"
        if b.get("problem"):
            body += f"<p class='note'>{_e(b['problem'])}</p>"
        if b.get("headline"):
            body += f"<p class='note'><strong>{_e(b['headline'])}</strong></p>"
        inputs = b.get("inputs")
        if isinstance(inputs, dict):
            body += "<h4>Inputs</h4>" + _table(_flatten(inputs))
        elif isinstance(inputs, str):
            body += f"<p class='note'>Inputs: {_e(inputs)}</p>"
        outs = b.get("expected_outputs", {})
        if set(outs) == {"parallel", "series"}:
            p, s = dict(_flatten(outs["parallel"])), dict(_flatten(outs["series"]))
            trs = "".join(
                f"<tr><td>{_e(_label(k))}</td><td class='num'>{_e(_fmt(p[k]))}</td><td class='num'>{_e(_fmt(s.get(k, '—')))}</td><td>{_e(_unit(k))}</td></tr>"
                for k in p
            )
            body += ("<h4>Parallel vs series</h4><div class='wrap'><table><thead><tr><th>Quantity</th><th>Parallel</th>"
                     f"<th>Series</th><th>Unit</th></tr></thead><tbody>{trs}</tbody></table></div>")
        elif outs:
            body += "<h4>Book results</h4>" + _table(_flatten(outs))
        if b.get("note"):
            body += f"<p class='note'>Note: {_e(b['note'])}</p>"
        cards.append(f"<article class='card' id='{_e(b['benchmark_id'])}'><h3>{_e(b['benchmark_id'])}</h3>{body}</article>")

    # Initial vs optimised one-turbine comparison, computed from the two benchmark records.
    a, o = by_id.get("G3-3.5.3.1-ONE-TURBINE-INITIAL"), by_id.get("G3-3.5.3.1-ONE-TURBINE-OPTIMISED")
    compare = ""
    if a and o:
        av = dict(_flatten(a["expected_outputs"]))
        av["turbine_discharge_t_k"] = a["inputs"]["turbine_discharge_t_k"]
        ov = dict(_flatten(o["expected_outputs"]))
        trs = ""
        for k, new in ov.items():
            old = av.get(k)
            if isinstance(old, (int, float)) and isinstance(new, (int, float)) and old:
                d = (new - old) / abs(old) * 100
                trs += (f"<tr><td>{_e(_label(k))}</td><td class='num'>{_e(_fmt(old))}</td><td class='num'>{_e(_fmt(new))}</td>"
                        f"<td class='num'>{d:+.1f} %</td><td>{_e(_unit(k))}</td></tr>")
        compare = ("<h2>One turbine: initial vs optimised turbine discharge temperature</h2>"
                   "<p class='note'>Change computed from the two transcribed cases (§3.5.3.1.1 → §3.5.3.1.2).</p>"
                   "<div class='wrap'><table><thead><tr><th>Quantity</th><th>Initial</th><th>Optimised</th><th>Change</th>"
                   f"<th>Unit</th></tr></thead><tbody>{trs}</tbody></table></div>")

    opens = "".join(
        f"<article class='card open'><h3>{_e(i['id'])}</h3><p class='ref'>due {_e(i['due'])}</p><p class='note'>{_e(i['item'])}</p></article>"
        for i in ch3.get("open_items", [])
    )
    src = ch3["source"]
    body = (
        compare
        + "<h2>Benchmarks</h2><section class='grid'>" + "".join(cards) + "</section>"
        + (f"<h2>Open items</h2><section class='grid'>{opens}</section>" if opens else "")
    )
    lead = (f"{_e(src['scope_note'])} Extracted {_e(src['extracted_on'])} by {_e(src['method'])}. "
            f"PDF page = printed page + {off} in this chapter.")
    foot = (f"Source: {_e(book['author'])}, <em>{_e(book['title'])}</em>, {_e(book['publisher'])} {_e(book['year'])}; "
            f"original PDF sha256 <code>{_e(book['sha256'])}</code> (not committed). Data: "
            "<code>docs/gistau-ch3/data/claude_cycle_benchmarks.json</code>. Generated by <code>tools/render_gistau_book.py</code>.")
    crumbs = "<a href='../gistau/index.html'>GISTAU book</a> › Chapter 3"
    return _shell("GISTAU Chapter 3", crumbs, "Chapter 3 · The Claude cycle", lead, body, foot)


def render_book() -> str:
    book, ch3, rec, gate, portal = _load()
    offs = book["pdf_page_offset"]
    chapters = book["chapters"]
    r = rec["record"]
    n_checked = len(gate["checked"])
    n_pass_ex = sum(1 for eid in gate["checked"] if all(x["verdict"] == "PASS" for x in r["rows"] if x["example_id"] == eid))
    n_q = sum(1 for x in r["rows"] if x["example_id"] in gate["checked"])
    n_q_pass = sum(1 for x in r["rows"] if x["example_id"] in gate["checked"] and x["verdict"] == "PASS")
    n_open = len(gate.get("source_check_required") or {})
    n_err = len(gate.get("book_errata") or {})

    rows = "".join(
        f"<tr><td>{_e(CHAPTER_TITLES.get(k, k))}</td><td class='num'>{_e(v['book_pages'])}</td><td class='num'>{_e(v['pdf_pages'])}</td></tr>"
        for k, v in chapters.items()
    )
    ch3_card = (
        "<article class='card'><h3><a href='../gistau-ch3/index.html'>Chapter 3 · Basic Thermodynamic Cycles</a></h3>"
        f"<p class='ref'>book pp. {_e(chapters['ch3_basic_thermodynamic_cycles']['book_pages'])} · PDF offset +{offs['ch3']}</p>"
        f"<span class='pill'>{len(ch3['benchmarks'])} Claude-cycle benchmarks</span>"
        f"<span class='pill'>{len(ch3.get('open_items', []))} open items</span>"
        "<p class='note'>Textbook reference cases (§3.5 Claude cycle): one turbine, two turbines, parallel vs series, efficiency correlations.</p>"
        "<ul class='links'><li><a href='../gistau-ch3/index.html'>Chapter 3 benchmarks</a></li></ul></article>"
    )
    links = "".join(f"<li><a href='../gistau-ch15/{_e(h)}'>{_e(t.strip())}</a></li>" for h, t in portal)
    ch15_card = (
        "<article class='card'><h3><a href='../gistau-ch15/index.html'>Chapter 15 · The Cryo Tool Box</a></h3>"
        f"<p class='ref'>book pp. {_e(chapters['ch15_cryo_tool_box']['book_pages'])} · PDF offset +{offs['ch15']}</p>"
        f"<span class='pill ok'>L1: {n_pass_ex}/{n_checked} examples · {n_q_pass}/{n_q} values</span>"
        f"<span class='pill'>{n_open} open</span><span class='pill'>{n_err} book erratum</span>"
        f"<span class='pill'>{len(gate['excluded'])} excluded</span>"
        "<p class='note'>Worked examples reproduced by the governing helium-4 provider in CI; engineering toolbox in the browser.</p>"
        f"<ul class='links'><li><a href='../gistau-ch15/index.html'>Chapter 15 portal</a></li>{links}</ul></article>"
    )
    others = "".join(
        f"<article class='card open'><h3>Not this book: {_e(o['name'])}</h3><p class='note'>{_e(o['identity'])}. {_e(o['note'])}</p></article>"
        for o in book.get("not_the_same_source", [])
    )
    ranges = [
        (int(chapters[c]["book_pages"].split("-")[0]), int(chapters[c]["book_pages"].split("-")[1]), offs[key], CHAPTER_TITLES[c])
        for c, key in (("ch3_basic_thermodynamic_cycles", "ch3"), ("ch15_cryo_tool_box", "ch15"))
    ]
    conv = (
        "<h2>Page finder</h2><p class='note'>Printed book page → page in the original PDF. Offsets are verified per chapter; "
        "other chapters are not mapped yet.</p>"
        "<div class='conv'><label for='bp'>Book page</label><input id='bp' type='number' inputmode='numeric' min='1' "
        f"max='{book['pdf_pages']}' placeholder='e.g. 638'/><output id='pdfp' for='bp' aria-live='polite'>—</output></div>"
    )
    script = (
        "<script>(function(){var R=" + json.dumps(ranges) + ";var i=document.getElementById('bp'),o=document.getElementById('pdfp');"
        "i.addEventListener('input',function(){var p=parseInt(i.value,10);if(!p){o.textContent='—';return;}"
        "for(var k=0;k<R.length;k++){if(p>=R[k][0]&&p<=R[k][1]){o.textContent='PDF page '+(p+R[k][2])+' ('+R[k][3]+')';return;}}"
        "o.textContent='Offset not verified for this page';});})();</script>"
    )
    body = (
        "<h2>Chapters</h2><section class='grid'>" + ch3_card + ch15_card + "</section>"
        + conv
        + "<h2>Where each chapter sits</h2><div class='wrap'><table><thead><tr><th>Part</th><th>Book pages</th><th>PDF pages</th></tr></thead>"
        + f"<tbody>{rows}</tbody></table></div>"
        + (f"<h2>Keep apart</h2><section class='grid'>{others}</section>" if others else "")
    )
    lead = (f"{_e(book['author'])}, <em>{_e(book['title'])}</em>, {_e(book['publisher'])} {_e(book['year'])}, "
            f"{_e(book['pdf_pages'])} pages. The canonical entry point for the chapters worked on in CODEX.")
    foot = (f"Original PDF <code>{_e(book['original_name'])}</code>, sha256 <code>{_e(book['sha256'])}</code>, "
            f"{_e(book['size_bytes'])} bytes; not committed, identity pinned in <code>GISTAU/sources/master/source_manifest.yaml</code>. "
            "Generated by <code>tools/render_gistau_book.py</code>. <a href='../index.html'>CODEX portal</a>")
    crumbs = "<a href='../index.html'>CODEX portal</a> › GISTAU book"
    return _shell("GISTAU Book", crumbs, "GISTAU · Cryogenic Helium Refrigeration", lead, body, foot, script)


def main() -> int:
    for path, text in ((OUT_BOOK, render_book()), (OUT_CH3, render_ch3())):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
