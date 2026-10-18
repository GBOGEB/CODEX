"""Responsive deterministic browser QA for the CODE PURPLE read-only control tower.

Native test mocks PUBLIC GET response payloads and never generates a worker
launch, credential, merge, security clearance or coverage acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LEDGER = json.loads((DOCS / "data/code_purple_convergence_control_w32.json").read_text())


def fixture(url):
    a = "0" * 40
    b = LEDGER["source_heads_observed"]["ABACUS"]
    if url.endswith("/GBOGEB/ABACUS/commits/main"):
        return {"sha": b}
    if url.endswith("/GBOGEB/CODEX/commits/main"):
        return {"sha": LEDGER["source_heads_observed"]["CODEX"]}
    if url.endswith("/GBOGEB/cryoplant-project/commits/main"):
        return {"sha": a}
    if url.endswith("/GBOGEB/ABACUS/issues/1860"):
        return {"body": "- [x] milestone one\n" + "- [ ] outstanding\n" * 11}
    if url.endswith("/GBOGEB/CODEX/issues/977"):
        return {"body": "- [ ] outstanding\n" * 7}
    if url.endswith("/GBOGEB/ABACUS/pulls/2274"):
        return {"state": "open", "draft": True, "merged_at": None,
                "head": {"sha": LEDGER["candidate"]["head"]}}
    if "/actions/workflows/mip-coverage-evidence.yml/runs?" in url:
        return {"workflow_runs": [{"id": 39156907500, "status": "completed",
                "conclusion": "failure", "run_attempt": 1,
                "head_sha": "0dd018768f46dbfecf8aad872776d4ba3f6d4fc8",
                "html_url": "https://github.com/GBOGEB/ABACUS/actions/runs/39156907500"}]}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--head", required=True)
    args = ap.parse_args()
    if len(args.head) != 40 or any(x not in "0123456789abcdef" for x in args.head):
        raise SystemExit("invalid exact head")
    args.out.mkdir(parents=True, exist_ok=True)
    handler = lambda *a, **k: SimpleHTTPRequestHandler(*a, directory=str(DOCS), **k)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    page_url = "http://127.0.0.1:%s/code_purple_convergence.html" % server.server_port
    checks = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for width, height in ((1440, 1000), (1280, 800), (390, 844)):
                page = browser.new_page(viewport={"width": width, "height": height})
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.on("console", lambda m: errors.append("console: "+m.text) if m.type == "error" else None)
                def intercept(route):
                    body = fixture(route.request.url)
                    if body is None:
                        route.fulfill(status=404, body="{}", content_type="application/json")
                    else:
                        route.fulfill(status=200, body=json.dumps(body), content_type="application/json")
                page.route("https://api.github.com/repos/**", intercept)
                page.goto(page_url, wait_until="domcontentloaded")
                page.locator("#githubState").get_by_text("7/7 metadata sources loaded", exact=False).wait_for(timeout=12000)
                assert page.locator("#abacusTodo").inner_text().startswith("1/12")
                assert page.locator("#codexTodo").inner_text().startswith("0/7")
                assert page.locator("#currentCoverage").inner_text() == "UNKNOWN"
                assert "DIFFERENT SHA" in page.locator("#b0Status").inner_text()
                assert page.locator("#controlLanes tr").count() == 6
                assert page.locator("#controlLinks a").count() >= 11
                page.locator("#githubReload").click()
                page.locator("#githubState").get_by_text("7/7 metadata sources loaded", exact=False).wait_for(timeout=12000)
                values = page.evaluate("""() => ({
                  scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth,
                  broken:[...document.images].filter(i=>!i.complete || i.naturalWidth===0).length})""")
                assert values["scroll"] <= values["client"] + 1, values
                assert values["broken"] == 0, values
                assert not errors, errors
                shot=args.out / ("control-%sx%s.png" % (width,height))
                page.screenshot(path=str(shot), full_page=True)
                checks.append({"viewport": [width,height],"errors":errors,
                               "overflow": False,"broken_images":0,
                               "screenshot":shot.name})
                page.close()
            # A failed public issue read must yield UNKNOWN, never a false zero.
            page=browser.new_page()
            page.route("https://api.github.com/repos/**", lambda route:
                       route.fulfill(status=503,body="{}",content_type="application/json")
                       if route.request.url.endswith("/GBOGEB/ABACUS/issues/1860")
                       else route.fulfill(status=200,body=json.dumps(fixture(route.request.url) or {}),
                                         content_type="application/json"))
            page.goto(page_url, wait_until="domcontentloaded")
            page.locator("#githubState").get_by_text("6/7 metadata sources loaded", exact=False).wait_for(timeout=12000)
            assert page.locator("#abacusTodo").inner_text().startswith("UNKNOWN")
            assert page.locator("#currentCoverage").inner_text() == "UNKNOWN"
            page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    receipts = {"schema":"codepurple.w32.browser-qa.v1","head":args.head,
                "browser_case": "SUCCESS_AND_DEGRADED_PUBLIC_GET",
                "checks":checks,"security_waiver":False,"authority_transfer":False,
                "merge_admission":"HOLD","coverage_current_main":None,
                "html_sha256":hashlib.sha256((DOCS/"code_purple_convergence.html").read_bytes()).hexdigest(),
                "ledger_sha256":hashlib.sha256((DOCS/"data/code_purple_convergence_control_w32.json").read_bytes()).hexdigest(),
                "evidence_level":"EXACT_SHA_TESTFLIGHT_NOT_MERGE_ADMISSION"}
    (args.out/"W32_BROWSER_QA_RECEIPT.json").write_text(json.dumps(receipts,indent=2)+"\n")
    print(json.dumps({"head":args.head,"responsive":len(checks),"result":"PASS"}))


if __name__ == "__main__":
    main()
