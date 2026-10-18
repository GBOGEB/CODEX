"""W37 exact-head DoV browser QA: three viewports, normal, reset and fail-closed GET.

This is presentation assurance only: no remote workers, approvals, coverage
promotion, QPS-private transport or admission mutations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LEDGER = json.loads((DOCS / "data/code-purple-dov-w36.json").read_text())
AB = next(x["sha"] for x in LEDGER["repos"] if x["repo"] == "GBOGEB/ABACUS")
CODEX = next(x["sha"] for x in LEDGER["repos"] if x["repo"] == "GBOGEB/CODEX")
FROZEN = next(x["runs"]["total"] for x in LEDGER["repos"] if x["repo"] == "GBOGEB/ABACUS")


def native_rows(repo, sha):
    rows = [
        {"id": 8001, "head_sha": sha, "status": "queued", "conclusion": None,
         "name": "PR Feedback Gate Evaluator"},
        {"id": 8002, "head_sha": sha, "status": "completed",
         "conclusion": "success", "name": "CI"},
    ]
    if repo == "ABACUS":
        rows += [
            {"id": 8003, "head_sha": sha, "status": "in_progress",
             "conclusion": None, "name": "Security Scan"},
            {"id": 8004, "head_sha": sha, "status": "completed",
             "conclusion": "failure", "name": "B0"}
        ]
    return rows


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS), **kwargs)

    def log_message(self, *_):
        pass


def intercept(route, calls, scenario):
    url = route.request.url
    calls.append({"method": route.request.method, "url": url})
    assert route.request.method == "GET", "UNEXPECTED_BROWSER_MUTATION"
    assert "cryoplant" not in url, "PRIVATE_QPS_API_BOUNDARY"
    path = urlparse(url).path
    if scenario == "offline_AB" and "/GBOGEB/ABACUS/" in path:
        return route.fulfill(status=503, body='{"error":"offline"}',
                             content_type="application/json")
    if path.endswith("/GBOGEB/ABACUS/branches/main"):
        return route.fulfill(status=200, body=json.dumps({"commit":{"sha":AB}}),
                             content_type="application/json")
    if path.endswith("/GBOGEB/CODEX/branches/main"):
        return route.fulfill(status=200, body=json.dumps({"commit":{"sha":CODEX}}),
                             content_type="application/json")
    for name, sha in (("ABACUS", AB), ("CODEX", CODEX)):
        if "/GBOGEB/" + name + "/actions/runs" in path:
            rows = native_rows(name,sha)
            if scenario == "invalid_AB" and name == "ABACUS":
                rows[0] = dict(rows[0],head_sha="f"*40)
            if scenario == "duplicate_AB" and name == "ABACUS":
                rows[1] = dict(rows[0])
            return route.fulfill(status=200,
                                 body=json.dumps({"total_count":len(rows),
                                                  "workflow_runs":rows}),
                                 content_type="application/json")
    raise AssertionError("unexpected GitHub GET: "+url)


def check_viewport(page, checks, width, height, artifact_dir):
    violations = page.evaluate("""() => ({
      documentWidth:document.documentElement.scrollWidth,
      clientWidth:document.documentElement.clientWidth,
      brokenImages:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).length,
      title:document.title
    })""")
    assert violations["documentWidth"] <= violations["clientWidth"]+1, violations
    assert violations["brokenImages"] == 0, violations
    assert "DoV" in violations["title"], violations
    shot = artifact_dir / ("w37-"+str(width)+"x"+str(height)+".png")
    page.screenshot(path=str(shot), full_page=True)
    checks.append({"viewport":[width,height],
                   "overflow":False,"broken_images":0,
                   "screenshot":shot.name,
                   "sha256":hashlib.sha256(shot.read_bytes()).hexdigest()})


def new_page(browser, scenario, viewport=(1280,800)):
    page = browser.new_page(viewport={"width":viewport[0],"height":viewport[1]})
    errors, calls = [], []
    page.on("pageerror",lambda e:errors.append("page:"+str(e)))
    page.on("console",lambda e:errors.append("console:"+e.text) if e.type=="error" else None)
    page.route("https://api.github.com/**",
               lambda route:intercept(route,calls,scenario))
    return page,errors,calls


def run(out, head):
    assert len(head)==40 and set(head)<=set("0123456789abcdef"), "INVALID_HEAD"
    out.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(("127.0.0.1",0), QuietHandler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    page_url="http://127.0.0.1:%s/code-purple-dov.html"%server.server_port
    checks=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            for width,height in ((1440,1000),(1280,800),(390,844)):
                page,errors,calls=new_page(browser,"valid",(width,height))
                try:
                    page.goto(page_url,wait_until="domcontentloaded")
                    page.wait_for_function("""() => document.querySelectorAll('#axes .axis').length===5""")
                    assert page.locator("#total").inner_text()==str(FROZEN)
                    assert page.locator("#repos tr").count()==3
                    assert page.locator("#coverage").count()==0  # DOM deliberately has no promoted coverage KPI
                    assert "UNKNOWN" in page.locator("main").inner_text()
                    page.locator("#family").select_option("B0")
                    assert page.locator("#clusters .axis").count()==1
                    page.locator("#refresh").click()
                    page.wait_for_function("""() => document.getElementById('status').textContent.includes('Public readback')""")
                    assert page.locator("#total").inner_text()=="4"
                    assert "4/4 observed" in page.locator("#observed").inner_text()
                    assert "Private QPS DEFER" in page.locator("#status").inner_text()
                    assert all("cryoplant" not in c["url"] for c in calls)
                    assert len(calls)==4, calls
                    page.locator("#reset").click()
                    assert page.locator("#total").inner_text()==str(FROZEN)
                    assert page.locator("#family").input_value()=="all"
                    assert "Restored frozen" in page.locator("#status").inner_text()
                    assert not errors, errors
                    check_viewport(page,checks,width,height,out)
                finally:
                    page.close()

            for scenario in ("offline_AB","invalid_AB","duplicate_AB"):
                page,errors,calls=new_page(browser,scenario)
                try:
                    page.goto(page_url,wait_until="domcontentloaded")
                    page.wait_for_function("""() => document.querySelectorAll('#axes .axis').length===5""")
                    page.locator("#refresh").click()
                    page.wait_for_function("""() => document.getElementById('status').textContent.includes('Public readback')""")
                    assert "Partial:" in page.locator("#status").inner_text(),scenario
                    assert page.locator("#total").inner_text()=="UNKNOWN",scenario
                    assert "No native-run census" in page.locator("#observed").inner_text()
                    assert "UNKNOWN" in page.locator("#repos").inner_text()
                    assert all("cryoplant" not in c["url"] for c in calls)
                    expected_fault_console=[e for e in errors if
                        scenario=="offline_AB" and
                        "Failed to load resource" in e and
                        "503" in e]
                    unexpected=[e for e in errors if e not in expected_fault_console]
                    assert not unexpected,unexpected
                    # An intentionally injected HTTP 503 may generate a
                    # Chromium console resource error. Record it as expected
                    # fault evidence, never as an unexplained QA error.
                    shot=out/("w37-negative-"+scenario+".png")
                    page.screenshot(path=str(shot),full_page=True)
                    checks.append({"negative_scenario":scenario,"status":"PASS",
                                   "expected_fault_console_count":len(expected_fault_console),
                                   "unexpected_console_errors":len(unexpected),
                                   "screenshot":shot.name,
                                   "sha256":hashlib.sha256(shot.read_bytes()).hexdigest()})
                finally:
                    page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    receipt={
        "schema":"codepurple.w37.browser-qa.v1",
        "source_head":head,
        "source_html_sha256":hashlib.sha256((DOCS/"code-purple-dov.html").read_bytes()).hexdigest(),
        "source_ledger_sha256":hashlib.sha256((DOCS/"data/code-purple-dov-w36.json").read_bytes()).hexdigest(),
        "checks":checks,"native_browser_case_count":len(checks),
        "evidence_class":"BROWSER_PRESENTATION_QA_NOT_ENGINEERING_ACCEPTANCE",
        "qps_private_probed":False,"remote_dispatch":False,
        "authority_transfer":False,"security_waiver":False,
        "merge_admission":"HOLD"
    }
    (out/"W37_BROWSER_QA_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"result":"PASS","head":head,"cases":len(checks),
                      "viewports":3,"negative_cases":3}))
    return receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--head",required=True)
    args=p.parse_args()
    run(args.out,args.head)
