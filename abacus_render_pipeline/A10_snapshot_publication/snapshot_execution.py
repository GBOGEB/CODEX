from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
A9 = ROOT / "abacus_render_pipeline" / "A9_multiformat_publication"
A7 = ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime"
sys.path.insert(0, str(A9))
sys.path.insert(0, str(A7))
sys.path.insert(0, str(ROOT))

from multiformat_execution import execute as execute_a9
from semantic_delta_replay import run as run_semantic_replay

OUTPUT_DIR = HERE / "outputs"
RECEIPT_DIR = HERE / "receipts"
A9_RECEIPT = A9 / "receipts" / "multiformat_execution_receipt.json"
VIEWPORT = {"width": 1440, "height": 1200}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot_dom(page: Any) -> dict[str, Any]:
    return page.evaluate(
        """() => {
          const els = [...document.querySelectorAll('h1,h2,p,strong,th,td')];
          const doc = document.documentElement;
          const body = document.body;
          function rgb(v) {
            const m = v && v.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
            return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : null;
          }
          function lum(c) {
            const f = c.map(v => { v /= 255; return v <= 0.04045 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); });
            return 0.2126*f[0] + 0.7152*f[1] + 0.0722*f[2];
          }
          function contrast(fg, bg) {
            const a=lum(fg), b=lum(bg), hi=Math.max(a,b), lo=Math.min(a,b);
            return (hi+0.05)/(lo+0.05);
          }
          function bgFor(el) {
            let n = el;
            while (n) {
              const c = getComputedStyle(n).backgroundColor;
              if (c && !c.endsWith(', 0)') && c !== 'rgba(0, 0, 0, 0)') return rgb(c);
              n = n.parentElement;
            }
            return [255,255,255];
          }
          let hidden=0, clipped=0, visible=0, contrastFailures=0, minContrast=999;
          const docW=Math.max(doc.scrollWidth, body.scrollWidth, doc.clientWidth);
          const docH=Math.max(doc.scrollHeight, body.scrollHeight, doc.clientHeight);
          for (const el of els) {
            if (!el.innerText.trim()) continue;
            const s=getComputedStyle(el), r=el.getBoundingClientRect();
            const isVisible=s.display!=='none' && s.visibility!=='hidden' && Number(s.opacity)>0 && r.width>0 && r.height>0;
            if (!isVisible) { hidden++; continue; }
            visible++;
            if (r.left < -0.5 || r.top < -0.5 || r.right > docW + 0.5 || r.bottom > docH + 0.5) clipped++;
            const fg=rgb(s.color), bg=bgFor(el);
            if (fg && bg) {
              const ratio=contrast(fg,bg); minContrast=Math.min(minContrast,ratio);
              if (ratio < 4.5) contrastFailures++;
            }
          }
          return {
            viewport_width: window.innerWidth,
            viewport_height: window.innerHeight,
            document_width: docW,
            document_height: docH,
            scroll_width: doc.scrollWidth,
            scroll_height: doc.scrollHeight,
            horizontal_overflow: doc.scrollWidth > window.innerWidth + 1,
            visible_text_elements: visible,
            hidden_text_elements: hidden,
            clipped_elements: clipped,
            contrast_failures: contrastFailures,
            min_contrast_ratio: minContrast === 999 ? null : Math.round(minContrast*1000)/1000,
            element_coverage: visible + hidden === 0 ? 0 : visible/(visible+hidden),
            body_text: body.innerText
          };
        }"""
    )


def execute() -> dict[str, Any]:
    a9 = execute_a9()
    if a9.get("decision") != "accept":
        raise RuntimeError("A9 multi-format carrier must accept before snapshot execution")

    html_rel = a9["formats"]["html"]["artifact_relpath"]
    html_path = A9 / html_rel
    if not html_path.exists():
        raise FileNotFoundError(html_path)

    expected_tokens = [a9["publication_id"], a9["canonical_content_sha256"]]
    for token in ("Requirements", "Traceability Matrix", "REQ-W000-001", "REQ-W001-001"):
        expected_tokens.append(token)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    png_path = OUTPUT_DIR / "governance_snapshot.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
        page = context.new_page()
        page.goto(html_path.resolve().as_uri(), wait_until="load")
        page.emulate_media(media="screen")
        telemetry = _snapshot_dom(page)
        page.screenshot(path=str(png_path), full_page=True, animations="disabled")
        browser_version = browser.version
        browser.close()

    with Image.open(png_path) as image:
        width, height = image.size
        image_format = image.format

    body_text = telemetry.pop("body_text")
    missing_tokens = [token for token in expected_tokens if token not in body_text]
    screenshot_covers_document = width >= telemetry["document_width"] and height >= telemetry["document_height"]
    checks = {
        "dimensions": {"pass": width > 0 and height > 0, "width_px": width, "height_px": height, "format": image_format},
        "clipping": {"pass": telemetry["clipped_elements"] == 0, "clipped_elements": telemetry["clipped_elements"]},
        "viewport_overflow": {"pass": not telemetry["horizontal_overflow"], "horizontal_overflow": telemetry["horizontal_overflow"]},
        "text_visibility": {"pass": telemetry["hidden_text_elements"] == 0 and telemetry["visible_text_elements"] > 0, "visible_text_elements": telemetry["visible_text_elements"], "hidden_text_elements": telemetry["hidden_text_elements"]},
        "contrast": {"pass": telemetry["contrast_failures"] == 0 and (telemetry["min_contrast_ratio"] or 0) >= 4.5, "min_ratio": telemetry["min_contrast_ratio"], "failures": telemetry["contrast_failures"], "threshold": 4.5},
        "element_coverage": {"pass": screenshot_covers_document and telemetry["element_coverage"] == 1.0, "coverage": telemetry["element_coverage"], "screenshot_covers_document": screenshot_covers_document},
        "semantic_parity": {"pass": not missing_tokens, "expected_token_count": len(expected_tokens), "missing_tokens": missing_tokens},
        "semantic_replay": {"pass": run_semantic_replay().get("status") == "PASS"},
        "a9_carrier": {"pass": a9.get("decision") == "accept"},
    }
    decision = "accept" if all(item["pass"] for item in checks.values()) else "reject"
    receipt = {
        "receipt_version": "A10.0",
        "publication_id": a9["publication_id"],
        "source_commit": os.environ.get("ABACUS_SOURCE_SHA") or os.environ.get("GITHUB_SHA") or "local",
        "snapshot_sha256": sha256_path(png_path),
        "snapshot_relpath": png_path.relative_to(HERE).as_posix(),
        "snapshot_bytes": png_path.stat().st_size,
        "source_html_sha256": sha256_path(html_path),
        "a9_receipt_sha256": sha256_path(A9_RECEIPT),
        "tuple_ledger_sha256": a9["tuple_ledger_sha256"],
        "renderer": {"name": "playwright-chromium", "browser_version": browser_version, "viewport": VIEWPORT, "full_page": True},
        "telemetry": telemetry,
        "checks": checks,
        "decision": decision,
    }
    (RECEIPT_DIR / "snapshot_execution_receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    result = execute()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"] == "accept" else 1)
