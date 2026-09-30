#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

VIEWPORTS = [
    ("desktop", 1440, 1000),
    ("laptop", 1280, 800),
    ("mobile", 390, 844),
]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-dir", default="docs")
    ap.add_argument("--output-dir", default="artifacts/missioncontrol-status-snapshot-qa")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise SystemExit(f"BROWSER_GATE_BLOCKED: Playwright unavailable: {exc}")

    docs = Path(args.docs_dir).resolve()
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    snapshot = json.loads(
        (docs / "data" / "missioncontrol_status_snapshot_v01.json").read_text(
            encoding="utf-8"
        )
    )

    handler = partial(QuietHandler, directory=str(docs))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/missioncontrol_status_snapshot.html"

    rows = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for name, width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height})
                console_errors: list[str] = []
                page_errors: list[str] = []
                page.on(
                    "console",
                    lambda msg, dst=console_errors: dst.append(msg.text)
                    if msg.type == "error"
                    else None,
                )
                page.on("pageerror", lambda exc, dst=page_errors: dst.append(str(exc)))
                response = page.goto(url, wait_until="networkidle")
                page.wait_for_function(
                    "document.querySelectorAll('#laneRows tr').length === 3"
                )

                title = page.title().strip()
                h1 = page.locator("h1").first.text_content() or ""
                lane_count = page.locator("#laneRows tr").count()
                evidence_count = page.locator("#evidence .ev").count()
                degraded = "Snapshot renderer degraded" in (
                    page.locator("#subtitle").text_content() or ""
                )
                overflow = page.evaluate(
                    """document.documentElement.scrollWidth >
                       document.documentElement.clientWidth ||
                       document.body.scrollWidth > document.body.clientWidth"""
                )
                broken_images = page.evaluate(
                    "[...document.images].filter(i => !i.complete || i.naturalWidth === 0).length"
                )
                footer = page.locator("#footer").text_content() or ""
                before_theme = page.locator("#theme").text_content() or ""
                page.locator("#theme").click()
                after_theme = page.locator("#theme").text_content() or ""
                theme_changed = before_theme != after_theme

                screenshot = out / f"{name}.png"
                page.screenshot(path=str(screenshot), full_page=True)

                passed = all(
                    [
                        response is not None and response.ok,
                        bool(title),
                        bool(h1.strip()),
                        lane_count == 3,
                        evidence_count >= 4,
                        not degraded,
                        not overflow,
                        broken_images == 0,
                        not console_errors,
                        not page_errors,
                        theme_changed,
                        "MATERIALIZED_VIEW" in footer,
                        "authority_transfer" in footer,
                    ]
                )
                rows.append(
                    {
                        "viewport": name,
                        "width": width,
                        "height": height,
                        "http_status": response.status if response else None,
                        "title": title,
                        "h1": h1,
                        "lane_count": lane_count,
                        "evidence_count": evidence_count,
                        "horizontal_overflow": bool(overflow),
                        "broken_images": broken_images,
                        "console_errors": console_errors,
                        "page_errors": page_errors,
                        "renderer_degraded": degraded,
                        "theme_changed": theme_changed,
                        "screenshot": screenshot.name,
                        "pass": passed,
                    }
                )
                page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    report = {
        "schema": "missioncontrol-html-browser-qa/1.0",
        "subject": "HTML_CONTENT_AS_SLIDE/STATUS_BD_SNAPSHOT",
        "snapshot_sha": snapshot.get("snapshot_sha"),
        "snapshot_state": snapshot.get("snapshot_state"),
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
        "boundary": "PRESENTATION_QA_ONLY",
        "viewports": rows,
        "pass": all(row["pass"] for row in rows),
    }
    (out / "playwright_qa.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
