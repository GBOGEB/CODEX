from __future__ import annotations

import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Any

VIEWPORTS = [
    ("desktop", 1440, 1000),
    ("laptop", 1280, 800),
    ("mobile", 390, 844),
]

PLOTLY_URL = "https://cdn.plot.ly/plotly-2.35.2.min.js"
PLOTLY_STUB = """
window.Plotly = {
  newPlot: function(target) {
    var el = typeof target === 'string' ? document.getElementById(target) : target;
    if (el) {
      el.dataset.plotlyStub = 'active';
      el.textContent = 'deterministic Plotly QA stub';
    }
    return Promise.resolve();
  }
};
"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


def horizontal_overflow(page: Any) -> bool:
    return bool(
        page.evaluate(
            """document.documentElement.scrollWidth >
               document.documentElement.clientWidth ||
               document.body.scrollWidth > document.body.clientWidth"""
        )
    )


def attach_error_capture(page: Any) -> tuple[list[str], list[str]]:
    console_errors: list[str] = []
    page_errors: list[str] = []
    page.on(
        "console",
        lambda msg, dst=console_errors: dst.append(msg.text)
        if msg.type == "error"
        else None,
    )
    page.on("pageerror", lambda exc, dst=page_errors: dst.append(str(exc)))
    return console_errors, page_errors


def qa_explorer_active(page: Any, url: str, out: Path, viewport: str) -> dict[str, Any]:
    page.route(
        PLOTLY_URL,
        lambda route: route.fulfill(
            status=200,
            content_type="application/javascript",
            body=PLOTLY_STUB,
        ),
    )
    response = page.goto(url, wait_until="networkidle")
    page.wait_for_function("document.querySelectorAll('#network .node').length > 0")
    page.wait_for_function(
        "document.querySelector('#plotlyStatus').textContent.includes('active')"
    )
    page.wait_for_function(
        "document.querySelector('#matplotlibPng').getAttribute('href') !== null"
    )

    initial_nodes = page.locator("#network .node").count()
    smart_label_count = int(
        page.evaluate(
            "[...document.querySelectorAll('#network .node text')].filter(x => getComputedStyle(x).display !== 'none').length"
        )
    )
    label_status = page.locator("#labelStatus").text_content() or ""
    accessible_named_nodes = page.locator("#network .node[role='button'][aria-label]").count()
    hidden_label_node_id = str(
        page.evaluate(
            """() => {
              const node = [...document.querySelectorAll('#network .node')]
                .find(n => {
                  const text = n.querySelector('text');
                  return text && getComputedStyle(text).display === 'none';
                });
              return node ? node.dataset.id : '';
            }"""
        )
        or ""
    )
    keyboard_access_pass = False
    if hidden_label_node_id:
        hidden_node = page.locator(
            f'#network .node[data-id="{hidden_label_node_id}"]'
        )
        hidden_aria = hidden_node.get_attribute("aria-label") or ""
        before_keyboard = page.locator("#inspect").text_content() or ""
        hidden_node.focus()
        hidden_node.press("Enter")
        after_keyboard = page.locator("#inspect").text_content() or ""
        keyboard_access_pass = bool(
            hidden_aria
            and after_keyboard != before_keyboard
            and "selected" in (page.locator(
                f'#network .node[data-id="{hidden_label_node_id}"]'
            ).get_attribute("class") or "")
        )
    first = page.locator("#network .node").first
    selected_id = first.get_attribute("data-id") or ""
    before_inspect = page.locator("#inspect").text_content() or ""
    first.click()
    after_inspect = page.locator("#inspect").text_content() or ""
    node_selection_pass = bool(
        selected_id
        and after_inspect != before_inspect
        and "degree" in after_inspect.lower()
    )

    projection_counts: dict[str, int] = {}
    for projection in ("engineering", "control", "observability"):
        page.locator("#view").select_option(projection)
        page.wait_for_timeout(50)
        projection_counts[projection] = page.locator("#network .node").count()
    page.locator("#view").select_option("all")

    plotly_active = (
        page.locator("#degreePlot").get_attribute("data-plotly-stub") == "active"
        and page.locator("#degreeScatter").get_attribute("data-plotly-stub") == "active"
    )
    plotly_status = page.locator("#plotlyStatus").text_content() or ""
    png_href = page.locator("#matplotlibPng").get_attribute("href")
    png_label = page.locator("#matplotlibPng").text_content() or ""
    overflow = horizontal_overflow(page)
    broken_images = int(
        page.evaluate(
            "[...document.images].filter(i => !i.complete || i.naturalWidth === 0).length"
        )
    )

    screenshot = out / f"explorer-{viewport}-plotly-active.png"
    page.screenshot(path=str(screenshot), full_page=True)

    passed = all(
        [
            response is not None and response.ok,
            initial_nodes > 0,
            0 < smart_label_count < initial_nodes,
            "smart labels" in label_status.lower(),
            accessible_named_nodes == initial_nodes,
            bool(hidden_label_node_id),
            keyboard_access_pass,
            node_selection_pass,
            all(count > 0 for count in projection_counts.values()),
            plotly_active,
            "active" in plotly_status.lower(),
            bool(png_href),
            "generated static evidence" in png_label.lower(),
            not overflow,
            broken_images == 0,
        ]
    )
    return {
        "surface": "graph_explorer",
        "mode": "plotly_active",
        "viewport": viewport,
        "http_status": response.status if response else None,
        "initial_node_count": initial_nodes,
        "smart_label_count": smart_label_count,
        "label_status": label_status,
        "accessible_named_nodes": accessible_named_nodes,
        "hidden_label_node_id": hidden_label_node_id,
        "keyboard_access_pass": keyboard_access_pass,
        "selected_node_id": selected_id,
        "node_selection_pass": node_selection_pass,
        "projection_node_counts": projection_counts,
        "plotly_active": plotly_active,
        "plotly_status": plotly_status,
        "matplotlib_href": png_href,
        "matplotlib_label": png_label,
        "horizontal_overflow": overflow,
        "broken_images": broken_images,
        "screenshot": screenshot.name,
        "pass": passed,
    }


def qa_explorer_fallback(page: Any, url: str, out: Path) -> dict[str, Any]:
    page.route(
        PLOTLY_URL,
        lambda route: route.fulfill(
            status=200,
            content_type="application/javascript",
            body="/* intentionally unavailable for fallback QA */",
        ),
    )
    console_errors, page_errors = attach_error_capture(page)
    response = page.goto(url, wait_until="networkidle")
    page.wait_for_function("document.querySelectorAll('#network .node').length > 0")
    page.wait_for_function(
        "document.querySelector('#plotlyStatus').textContent.includes('unavailable')"
    )

    node_count = page.locator("#network .node").count()
    table_count = page.locator("#topRows tr").count()
    status = page.locator("#plotlyStatus").text_content() or ""
    svg_fallback = page.locator(
        'img[src="assets/missioncontrol/missioncontrol_degree_distribution.svg"]'
    ).count() == 1
    overflow = horizontal_overflow(page)

    screenshot = out / "explorer-desktop-plotly-fallback.png"
    page.screenshot(path=str(screenshot), full_page=True)

    passed = all(
        [
            response is not None and response.ok,
            node_count > 0,
            table_count > 0,
            "unavailable" in status.lower(),
            svg_fallback,
            not overflow,
            not console_errors,
            not page_errors,
        ]
    )
    return {
        "surface": "graph_explorer",
        "mode": "plotly_fallback",
        "viewport": "desktop",
        "http_status": response.status if response else None,
        "node_count": node_count,
        "top_degree_rows": table_count,
        "plotly_status": status,
        "svg_fallback_present": svg_fallback,
        "horizontal_overflow": overflow,
        "console_errors": console_errors,
        "page_errors": page_errors,
        "screenshot": screenshot.name,
        "pass": passed,
    }


def qa_mycelium_layouts(page: Any, url: str, out: Path, viewport: str) -> dict[str, Any]:
    console_errors, page_errors = attach_error_capture(page)
    response = page.goto(url, wait_until="networkidle")
    page.wait_for_function("document.querySelector('#stamp').textContent.includes('snapshot')")

    layouts: dict[str, dict[str, Any]] = {}
    for mode in ("grid", "golden-focus", "single-focus"):
        page.locator("#layout").select_option(mode)
        page.locator("#focus").select_option("MYCELIUM_GRAPH")
        page.wait_for_timeout(50)
        grid_class = page.locator("#grid").get_attribute("class") or ""
        focused = page.locator(".panel.focus").count()
        visible_panels = int(
            page.evaluate(
                "[...document.querySelectorAll('.panel')].filter(x => getComputedStyle(x).display !== 'none').length"
            )
        )
        overflow = horizontal_overflow(page)
        screenshot = out / f"mycelium-{viewport}-{mode}.png"
        page.screenshot(path=str(screenshot), full_page=True)

        expected_class = "grid" if mode == "grid" else mode
        class_ok = expected_class in grid_class.split()
        panel_ok = focused == 1 and (
            visible_panels == 1 if mode == "single-focus" else visible_panels == 6
        )
        layouts[mode] = {
            "grid_class": grid_class,
            "focused_panels": focused,
            "visible_panels": visible_panels,
            "horizontal_overflow": overflow,
            "screenshot": screenshot.name,
            "pass": class_ok and panel_ok and not overflow,
        }

    return {
        "surface": "mycelium_layouts",
        "viewport": viewport,
        "http_status": response.status if response else None,
        "layouts": layouts,
        "console_errors": console_errors,
        "page_errors": page_errors,
        "pass": bool(
            response is not None
            and response.ok
            and all(row["pass"] for row in layouts.values())
            and not console_errors
            and not page_errors
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-dir", default="docs")
    ap.add_argument("--output-dir", default="artifacts/missioncontrol-graph-explorer-qa")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(f"BROWSER_GATE_BLOCKED: Playwright unavailable: {exc}")

    docs = Path(args.docs_dir).resolve()
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    graph = json.loads(
        (docs / "data" / "missioncontrol_interaction_graph.json").read_text(
            encoding="utf-8"
        )
    )
    analysis = json.loads(
        (docs / "data" / "missioncontrol_graph_analysis.json").read_text(
            encoding="utf-8"
        )
    )

    handler = partial(QuietHandler, directory=str(docs))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    root = f"http://127.0.0.1:{server.server_port}"
    explorer_url = f"{root}/missioncontrol_graph_explorer.html"
    mycelium_url = f"{root}/missioncontrol_mycelium.html"

    rows: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for name, width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height})
                console_errors, page_errors = attach_error_capture(page)
                row = qa_explorer_active(page, explorer_url, out, name)
                row["console_errors"] = console_errors
                row["page_errors"] = page_errors
                row["pass"] = bool(row["pass"] and not console_errors and not page_errors)
                rows.append(row)
                events.extend(
                    [
                        {
                            "action": "smart_label_density",
                            "viewport": name,
                            "visible_labels": row["smart_label_count"],
                            "visible_nodes": row["initial_node_count"],
                            "result": "PASS"
                            if 0 < row["smart_label_count"] < row["initial_node_count"]
                            else "FAIL",
                        },
                        {
                            "action": "accessible_node_names",
                            "viewport": name,
                            "named_nodes": row["accessible_named_nodes"],
                            "visible_nodes": row["initial_node_count"],
                            "result": "PASS"
                            if row["accessible_named_nodes"] == row["initial_node_count"]
                            else "FAIL",
                        },
                        {
                            "action": "keyboard_node_activation",
                            "viewport": name,
                            "node_id": row["hidden_label_node_id"],
                            "result": "PASS" if row["keyboard_access_pass"] else "FAIL",
                        },
                        {
                            "action": "select_node",
                            "viewport": name,
                            "node_id": row["selected_node_id"],
                            "result": "PASS" if row["node_selection_pass"] else "FAIL",
                        },
                        *[
                            {
                                "action": "switch_projection",
                                "viewport": name,
                                "projection": projection,
                                "visible_nodes": count,
                                "result": "PASS" if count > 0 else "FAIL",
                            }
                            for projection, count in row["projection_node_counts"].items()
                        ],
                        {
                            "action": "activate_matplotlib_link",
                            "viewport": name,
                            "href": row["matplotlib_href"],
                            "result": "PASS" if row["matplotlib_href"] else "FAIL",
                        },
                    ]
                )
                page.close()

                layout_page = browser.new_page(viewport={"width": width, "height": height})
                layout_row = qa_mycelium_layouts(
                    layout_page, mycelium_url, out, name
                )
                rows.append(layout_row)
                for mode, result in layout_row["layouts"].items():
                    events.append(
                        {
                            "action": "switch_layout",
                            "viewport": name,
                            "layout": mode,
                            "visible_panels": result["visible_panels"],
                            "horizontal_overflow": result["horizontal_overflow"],
                            "result": "PASS" if result["pass"] else "FAIL",
                        }
                    )
                layout_page.close()

            fallback = browser.new_page(viewport={"width": 1440, "height": 1000})
            fallback_row = qa_explorer_fallback(fallback, explorer_url, out)
            rows.append(fallback_row)
            events.append(
                {
                    "action": "plotly_fallback",
                    "viewport": "desktop",
                    "svg_fallback_present": fallback_row["svg_fallback_present"],
                    "visible_nodes": fallback_row["node_count"],
                    "result": "PASS" if fallback_row["pass"] else "FAIL",
                }
            )
            fallback.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    report = {
        "schema": "missioncontrol-graph-explorer-browser-qa/1.0",
        "subject": "MISSIONCONTROL_GRAPH_EXPLORER",
        "graph": {
            "nodes": len(graph.get("nodes", [])),
            "edges": len(graph.get("edges", [])),
            "analysis_nodes": analysis.get("graph", {}).get("node_count"),
            "analysis_edges": analysis.get("graph", {}).get("edge_count"),
        },
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
        "boundary": "PRESENTATION_INTERACTION_QA_ONLY",
        "viewports": rows,
        "pass": all(row["pass"] for row in rows),
    }
    receipt = {
        "schema": "missioncontrol-graph-explorer-interaction-receipt/1.0",
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
        "events": events,
        "pass": all(event["result"] == "PASS" for event in events),
    }
    (out / "playwright_qa.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / "interaction_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["pass"] and receipt["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
