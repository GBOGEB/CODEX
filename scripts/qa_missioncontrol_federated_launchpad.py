"""Browser acceptance for the source-bound MissionControl federated launchpad.

Run from a checkout with Playwright/Chromium installed:
python scripts/qa_missioncontrol_federated_launchpad.py --docs-dir docs --output-dir artifacts/mc-federated-qa

This never authenticates workers or promotes engineering/admission evidence.
"""
from __future__ import annotations
import argparse
import functools
import hashlib
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

VIEWPORTS = (("desktop", 1440, 1000), ("laptop", 1280, 800), ("mobile", 390, 844))


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        pass


def run(docs: Path, output: Path) -> dict:
    from playwright.sync_api import sync_playwright

    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(docs)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    observations: list[dict] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                for label, width, height in VIEWPORTS:
                    page = browser.new_page(viewport={"width": width, "height": height})
                    console: list[str] = []
                    errors: list[str] = []
                    page.on("pageerror", lambda e, dst=errors: dst.append(str(e)))
                    page.on("console", lambda m, dst=console: dst.append(m.text) if m.type == "error" else None)
                    page.on("response", lambda r, dst=console: dst.append("HTTP %s %s" % (r.status, r.url)) if r.status >= 400 else None)
                    url = "http://127.0.0.1:%s/missioncontrol_federated_launchpad.html" % server.server_port
                    response = page.goto(url, wait_until="networkidle", timeout=20000)
                    page.wait_for_selector("#dag .node", timeout=10000)
                    before = page.locator("#dag .node").count()
                    first = page.locator("#dag .node").first
                    first.focus()
                    first.press("Enter")
                    selected = page.locator("#dag .node.selected").count() == 1
                    filter_box = page.locator("#filter")
                    filter_box.fill("CODEX")
                    filtered = page.locator("#dag .node").count()
                    filter_box.fill("")
                    page.locator("#edges").select_option("dependency")
                    dep = page.locator("#dag .edge").count()
                    page.locator("#edges").select_option("reference")
                    refs = page.locator("#dag .edge").count()
                    page.locator("#clear").click()
                    reset = page.locator("#dag .node").count() == before
                    overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth || document.body.scrollWidth > document.body.clientWidth")
                    broken = page.evaluate("[...document.images].filter(x => !x.complete || x.naturalWidth === 0).length")
                    screenshot = output / ("%s.png" % label)
                    page.screenshot(path=str(screenshot), full_page=True)
                    passed = all((response is not None and response.ok, before == 18, selected,
                                  0 < filtered < before, dep > 0, refs > 0, reset,
                                  not overflow, broken == 0, not errors, not console))
                    observations.append({"viewport": label, "width": width, "height": height,
                        "http": response.status if response else None, "source_nodes": before,
                        "filtered_nodes": filtered, "dependency_edges": dep, "reference_edges": refs,
                        "keyboard_inspection": selected, "reset": reset, "horizontal_overflow": overflow,
                        "broken_images": broken, "page_errors": errors, "console_errors": console,
                        "screenshot": screenshot.name, "pass": passed})
                    page.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    graph = docs / "data" / "missioncontrol_federated_dag_v1.json"
    html = docs / "missioncontrol_federated_launchpad.html"
    receipt = {
        "schema": "missioncontrol.launchpad.browser-qa.v1",
        "evidence": "LOCAL_OR_NATIVE_BROWSER_ONLY_NOT_GOVERNED_ADMISSION",
        "html_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
        "source_json_sha256": hashlib.sha256(graph.read_bytes()).hexdigest(),
        "viewport_count": len(VIEWPORTS),
        "passed": sum(bool(x["pass"]) for x in observations),
        "failed": sum(not x["pass"] for x in observations),
        "observations": observations,
        "formal_credit_delta": 0,
        "security_waiver": False,
        "worker_launch_id": None,
    }
    (output / "qa-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--docs-dir", type=Path, default=Path("docs"))
    cli.add_argument("--output-dir", type=Path, default=Path("artifacts/mc-federated-qa"))
    args = cli.parse_args()
    receipt = run(args.docs_dir.resolve(), args.output_dir.resolve())
    print(json.dumps({"passed": receipt["passed"], "failed": receipt["failed"]}))
    if receipt["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
