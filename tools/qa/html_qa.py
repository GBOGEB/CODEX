"""Site-wide Playwright QA for every published CODEX page (MANIFEST.json published_pages).

Serves docs/ over HTTP (as GitHub Pages does), loads each page in Chromium at a
desktop (1280x900) and a phone (390x844) viewport, and records:

  ERROR  page_error         uncaught JavaScript exception
  ERROR  local_http_error   same-origin request answered >= 400 or failed
  ERROR  broken_link        <a href> to a relative target that does not exist
  ERROR  no_title           missing or empty <title>
  WARN   console_error      console.error output
  WARN   external_failed    third-party request failed (CDN, API); network-dependent
  WARN   phone_overflow     horizontal page scroll at 390 px
  WARN   no_viewport_meta   no <meta name="viewport">
  WARN   no_lang            no <html lang>
  WARN   deploy_generated   same-origin file the Pages build generates (DEPLOY_GENERATED)
  WARN   page_error_after_external_failure
                            uncaught exception on a page whose third-party script failed to load

The committed baseline (reports/html_qa/baseline.json) lists known ERROR
findings per page. The gate fails only on ERROR findings that are not in the
baseline (no new debt); fixed findings are reported so the baseline can shrink.

Usage:
    python tools/qa/html_qa.py --report reports/html_qa/latest.json [--check] [--write-baseline]
"""
from __future__ import annotations

import argparse
import contextlib
import fnmatch
import functools
import glob
import http.server
import json
import socketserver
import sys
import threading
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPO_ROOT / "docs"
MANIFEST = REPO_ROOT / "MANIFEST.json"
BASELINE = REPO_ROOT / "reports" / "html_qa" / "baseline.json"
VIEWPORTS = {"desktop": (1280, 900), "phone": (390, 844)}
ERROR_KINDS = {"page_error", "local_http_error", "broken_link", "no_title"}

# Files the Pages build (.github/workflows/pages.yml) generates before upload; they are
# absent from a plain checkout, so a request for them is a WARN here, not an ERROR.
# tests/test_html_qa.py checks each producer is still invoked by pages.yml.
DEPLOY_GENERATED = {
    "data/code_purple_current_observation.json": "scripts/code_purple_current_observation.py",
    "data/code_purple_rex_rollup.json": "scripts/code_purple_rex_rollup.py",
    "assets/missioncontrol/missioncontrol_degree_distribution.png": "scripts/render_missioncontrol_graph_matplotlib.py",
}


def published_pages() -> list[str]:
    patterns = json.loads(MANIFEST.read_text(encoding="utf-8"))["published_pages"]
    found: set[str] = set()
    for pat in patterns:
        found.update(glob.glob(str(REPO_ROOT / pat)))
    return sorted(str(Path(p).relative_to(DOCS)).replace("\\", "/") for p in found if p.endswith(".html"))


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args: Any) -> None:  # silence per-request logging
        pass


@contextlib.contextmanager
def serve_docs():
    handler = functools.partial(_Quiet, directory=str(DOCS))
    with socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler) as httpd:
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{httpd.server_address[1]}/"
        finally:
            httpd.shutdown()


def _link_target_exists(page: str, href: str) -> bool:
    url = urlparse(href)
    if url.scheme or url.netloc or href.startswith(("#", "mailto:", "javascript:", "data:")) or not url.path:
        return True
    target = (DOCS / Path(page).parent / unquote(url.path)).resolve() if not url.path.startswith("/") else None
    if target is None:
        return True  # site-absolute paths depend on the Pages base URL; not checked
    if target.is_dir():
        return (target / "index.html").exists()
    return target.exists()


def check_page(browser: Any, base: str, page: str) -> dict[str, Any]:
    from playwright.sync_api import Error as PlaywrightError

    findings: list[dict[str, str]] = []

    def add(kind: str, detail: str, viewport: str = "") -> None:
        item = {"kind": kind, "detail": detail[:300]}
        if viewport:
            item["viewport"] = viewport
        if item not in findings:
            findings.append(item)

    origin = urlparse(base).netloc
    for vp, (w, h) in VIEWPORTS.items():
        ctx = browser.new_context(viewport={"width": w, "height": h})
        pg = ctx.new_page()
        pg.on("pageerror", lambda exc: add("page_error", str(exc).splitlines()[0] if str(exc) else "error"))
        pg.on("console", lambda msg: add("console_error", msg.text) if msg.type == "error" else None)

        def _kind(url: str) -> str:
            if urlparse(url).netloc != origin:
                return "external_failed"
            return "deploy_generated" if urlparse(url).path.lstrip("/") in DEPLOY_GENERATED else "local_http_error"

        def on_response(resp: Any) -> None:
            if resp.status >= 400:
                add(_kind(resp.url), f"{resp.status} {resp.url.replace(base, '/')}")

        def on_failed(req: Any) -> None:
            if urlparse(req.url).netloc == origin and any(f["detail"].endswith(req.url.replace(base, "/")) for f in findings):
                return  # the 404 response is already recorded
            add(_kind(req.url), f"failed {req.url.replace(base, '/')} ({req.failure})")

        pg.on("response", on_response)
        pg.on("requestfailed", on_failed)
        try:
            pg.goto(urljoin(base, page), wait_until="load", timeout=30000)
            pg.wait_for_timeout(400)
        except PlaywrightError as exc:  # navigation timeout or crash
            add("page_error", f"navigation: {exc}".splitlines()[0])
        if vp == "desktop":
            meta = pg.evaluate(
                """() => ({title: (document.title || '').trim(),
                         lang: document.documentElement.getAttribute('lang') || '',
                         viewport: !!document.querySelector('meta[name=viewport]'),
                         links: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))})"""
            )
            if not meta["title"]:
                add("no_title", "empty <title>")
            if not meta["lang"]:
                add("no_lang", "<html> has no lang")
            if not meta["viewport"]:
                add("no_viewport_meta", "no viewport meta")
            for href in sorted(set(meta["links"])):
                if not _link_target_exists(page, href):
                    add("broken_link", href)
        else:
            over = pg.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
            if over > 1:
                add("phone_overflow", f"{over}px horizontal scroll", vp)
        ctx.close()
    if any(f["kind"] == "external_failed" for f in findings):
        for f in findings:
            if f["kind"] == "page_error":
                f["kind"] = "page_error_after_external_failure"
    return {"page": page, "findings": findings}


def run(pages: list[str]) -> list[dict[str, Any]]:
    from playwright.sync_api import sync_playwright

    with serve_docs() as base, sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            return [check_page(browser, base, page) for page in pages]
        finally:
            browser.close()


def _error_keys(results: list[dict[str, Any]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for r in results:
        keys = sorted({f"{f['kind']}: {f['detail']}" for f in r["findings"] if f["kind"] in ERROR_KINDS})
        if keys:
            out[r["page"]] = keys
    return out


def compare(results: list[dict[str, Any]], baseline: dict[str, list[str]]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """(new errors not in baseline, baseline errors no longer present)."""
    now = _error_keys(results)
    new = {p: [k for k in ks if k not in baseline.get(p, [])] for p, ks in now.items()}
    fixed = {p: [k for k in ks if k not in now.get(p, [])] for p, ks in baseline.items()}
    return {p: v for p, v in new.items() if v}, {p: v for p, v in fixed.items() if v}


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for r in results:
        for f in r["findings"]:
            counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    clean = sum(1 for r in results if not any(f["kind"] in ERROR_KINDS for f in r["findings"]))
    return {"pages": len(results), "pages_without_errors": clean, "finding_counts": dict(sorted(counts.items()))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", type=Path, help="write the full JSON report here")
    ap.add_argument("--check", action="store_true", help="exit 1 on ERROR findings not in the baseline")
    ap.add_argument("--write-baseline", action="store_true", help="replace the baseline with the current ERROR findings")
    ap.add_argument("--only", default="", help="fnmatch pattern to limit pages (debugging)")
    args = ap.parse_args(argv)

    pages = [p for p in published_pages() if not args.only or fnmatch.fnmatch(p, args.only)]
    results = run(pages)
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))["errors"] if BASELINE.exists() else {}
    new, fixed = compare(results, baseline)
    report = {"summary": summarize(results), "new_errors": new, "fixed_since_baseline": fixed, "results": results}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if args.write_baseline:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps({"note": "Known ERROR findings per published page; the gate fails only on new ones.",
                                        "errors": _error_keys(results)}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    s = report["summary"]
    print(f"::notice title=HTML QA::{s['pages']} pages, {s['pages_without_errors']} without errors; {s['finding_counts']}")
    for page, keys in new.items():
        for k in keys:
            print(f"::error file=docs/{page},title=HTML QA new error::{k}")
    for page, keys in fixed.items():
        print(f"::notice file=docs/{page},title=HTML QA fixed::{len(keys)} baseline error(s) no longer present; shrink the baseline")
    return 1 if args.check and new else 0


if __name__ == "__main__":
    sys.exit(main())
