"""Responsive browser QA for the read-only MissionControl V2 operations atlas."""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

VIEWPORTS = (("wide", 1920, 1050), ("desktop", 1440, 1000),
             ("laptop", 1280, 800), ("mobile", 390, 844))


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run(docs: Path, output: Path) -> dict:
    from playwright.sync_api import Error, sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    html = docs / "missioncontrol_operations_atlas.html"
    graph = docs / "data" / "missioncontrol_operations_atlas_v2.json"
    source = json.loads(graph.read_text(encoding="utf-8"))
    server = ThreadingHTTPServer(("127.0.0.1", 0),
             functools.partial(Quiet, directory=str(docs)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    observations = []
    try:
        with sync_playwright() as p:
            executable = os.getenv("CHROMIUM_EXECUTABLE")
            kwargs = {"headless": True, "args": ["--no-sandbox"]}
            if executable:
                kwargs["executable_path"] = executable
            browser = p.chromium.launch(**kwargs)
            try:
                for label, width, height in VIEWPORTS:
                    page = browser.new_page(viewport={"width": width, "height": height})
                    errors = []
                    page.on("pageerror", lambda e, dst=errors: dst.append(str(e)))
                    page.on("console", lambda e, dst=errors: dst.append(e.text) if e.type == "error" else None)
                    mode = "HTTP"
                    try:
                        response = page.goto(
                            "http://127.0.0.1:%s/missioncontrol_operations_atlas.html" % server.server_port,
                            wait_until="networkidle", timeout=15000,
                        )
                        assert response is not None and response.ok
                    except (Error, AssertionError):
                        # Managed browsers may block localhost. Content is self-contained.
                        page.set_content(html.read_text(encoding="utf-8"), wait_until="load")
                        mode = "IN_MEMORY_STATIC_EQUIVALENCE"
                    checks = {}
                    def verify(name: str, result: bool) -> None:
                        checks[name] = bool(result)
                    verify("document", page.locator("h1").count() == 1)
                    verify("five_tiles", page.locator("#metrics .metric").count() == 5)
                    verify("no_horizontal_overflow", page.evaluate(
                        "document.documentElement.scrollWidth<=document.documentElement.clientWidth && document.body.scrollWidth<=document.body.clientWidth"))
                    page.get_by_role("button", name="Graph & DAG").click()
                    verify("source_nodes", page.locator("#dag .graph-node").count() == len(source["nodes"]))
                    verify("source_edges", page.locator("#dag .graph-edge").count() == len(source["edges"]))
                    page.locator("#filter").fill("CODEX")
                    filtered = page.locator("#dag .graph-node").count()
                    verify("search", 0 < filtered < len(source["nodes"]))
                    page.locator("#clear").click()
                    verify("reset", page.locator("#dag .graph-node").count() == len(source["nodes"]))
                    page.locator("#edges").select_option("federation")
                    verify("three_federation_candidates", page.locator("#dag .graph-edge").count() == 3)
                    page.locator("#edges").select_option("all")
                    node = page.locator("#dag .graph-node").first
                    node.focus()
                    node.press("Enter")
                    verify("keyboard_node_inspection", "Incoming:" in page.locator("#inspect").inner_text())
                    page.get_by_role("button", name="Scheduler / Workers").click()
                    verify("workers", page.locator("#workerGrid .worker-card").count() == 5)
                    page.locator("#evaluate").click()
                    verify("dispatch_fails_closed", "QUALIFICATION: DENY" in page.locator("#qualification").inner_text()
                           and "No API call" in page.locator("#qualification").inner_text())
                    page.get_by_role("button", name="Repository Launch").click()
                    verify("multiple_repo_links", page.locator("#launchList .launch").count() >= 20)
                    page.locator("#launchSearch").fill("ABACUS")
                    verify("launch_filter", 0 < page.locator("#launchList .launch").count() < 20)
                    page.get_by_role("button", name="SIPOC & Processes").click()
                    verify("seven_sipoc_rows", page.locator("#sipocBody tr").count() == 7)
                    page.get_by_role("button", name="Telemetry & Lineage").click()
                    verify("four_registry_rows", page.locator("#sourceLedger tr").count() == 4)
                    page.get_by_role("button", name="Overview").click()
                    verify("no_page_errors", not errors)
                    verify("no_broken_images", page.evaluate(
                        "[...document.images].filter(x=>!x.complete||x.naturalWidth===0).length") == 0)
                    screenshot = output / (label + ".png")
                    page.screenshot(path=str(screenshot), full_page=True)
                    observations.append({
                        "viewport": label, "width": width, "height": height,
                        "qa_mode": mode, "checks": checks,
                        "passed": sum(checks.values()), "total": len(checks),
                        "errors": errors, "screenshot": screenshot.name,
                    })
                    page.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    receipt = {
        "schema": "missioncontrol.operations_atlas.browser_qa.v2",
        "source_json_sha256": hashlib.sha256(graph.read_bytes()).hexdigest(),
        "html_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
        "observations": observations,
        "passed": sum(x["passed"] for x in observations),
        "total": sum(x["total"] for x in observations),
        "failure_count": sum(x["total"] - x["passed"] for x in observations),
        "dispatch_enabled": False, "security_waiver": False,
        "native_worker_receipt": None, "main_admission": "HOLD",
    }
    (output / "qa-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--docs-dir", type=Path, default=Path("docs"))
    cli.add_argument("--output-dir", type=Path, default=Path("artifacts/missioncontrol-operations-atlas-v2"))
    a = cli.parse_args()
    result = run(a.docs_dir.resolve(), a.output_dir.resolve())
    print(json.dumps({"passed": result["passed"], "total": result["total"], "failed": result["failure_count"]}))
    if result["failure_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
