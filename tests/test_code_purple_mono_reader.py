"""Static acceptance controls for the read-only monochrome process reader.

These tests deliberately do not claim executed browser/runner/worker proof.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "federation" / "mesh"
HTML = ROOT / "CODE_PURPLE_EVERRED_MONOCHROME_READER_v0.2.html"
DAG = ROOT / "CODE_PURPLE_EVERRED_MONOCHROME_FLOW_v0.2.mmd"
CONTRACT = ROOT / "CODE_PURPLE_EVERRED_GRAPH_REVIEW_v0.2.md"


def _receipt_core(html: str) -> str:
    """Return the DOM-free receipt validation block embedded in the reader."""
    begin = html.index("/* receipt-core:begin")
    end = html.index("/* receipt-core:end */")
    return html[html.index("*/", begin) + 2:end]


class MonochromeReaderContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.diagram = DAG.read_text(encoding="utf-8")
        cls.contract = CONTRACT.read_text(encoding="utf-8")

    def test_eight_stages_present_in_html_and_mermaid(self):
        for n in range(1, 9):
            stage = f"S{n:02d}"
            with self.subTest(stage=stage):
                self.assertIn(stage, self.html)
                self.assertIn(stage, self.diagram)

    def test_no_semantic_colour_palette(self):
        # Only grayscale hex colours may be used in HTML.
        for hexval in re.findall(r"#[0-9a-fA-F]{3,8}\b", self.html):
            h = hexval[1:]
            if len(h) == 3:
                rgb = [int(d, 16) for d in h]
            elif len(h) in (6, 8):
                rgb = [int(h[i:i+2], 16) for i in (0, 2, 4)]
            else:
                continue
            self.assertEqual(len(set(rgb)), 1, hexval)

    def test_reading_legend_is_explicit(self):
        for label in (
            "Basic reading legend", "ordinary advancement",
            "first-red repair", ".self re-entry",
            "pay_it_forward proposal", "HOLD / watch",
            "Rectangle: stage", "Diamond: decision",
            "admission gate", "No observation",
        ):
            with self.subTest(label=label):
                self.assertIn(label, self.html)

    def test_disclosure_and_keyboard_friendly_contract(self):
        for marker in (
            'id="details"', "<summary>", "aria-pressed",
            "focus-visible", "id=\"expand\"", "id=\"collapse\"",
        ):
            self.assertIn(marker, self.html)

    def test_n_minus_ten_is_not_synthetic_green(self):
        for value in ("N−10", "N−9", "N−8", "N−7", "N−6",
                      "N−5", "N−4", "N−3", "N−2", "N−1"):
            self.assertIn(value, self.html)
        self.assertIn("NOT_TRIGGERED", self.html)
        self.assertIn("QUEUED AT SNAPSHOT", self.html)

    def test_recensus_needs_identity_and_rejects_conflict(self):
        for marker in (
            "code-purple.observation.v1", "run_attempt", "job_id",
            "source_sha", "observed_at", "Contradictory",
            "Number.isSafeInteger", "receipts", "UNVERIFIED",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.html)
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("https://cdn.", self.html)

    # --- #1036 review reconciliation (CODEX #1037 C3) -----------------------

    def test_pinned_census_stores_full_shas(self):
        block = self.html.split("const runs=[", 1)[1].split("];", 1)[0]
        rows = re.findall(r"\['(N(?:−\d+)?)','([^']*)'", block)
        self.assertEqual(len(rows), 11, rows)
        for slot, sha in rows:
            with self.subTest(slot=slot):
                self.assertRegex(sha, r"^[0-9a-f]{40}$")

    def test_recensus_requires_receipt_provenance(self):
        core = _receipt_core(self.html)
        for marker in ("receipt_digest", "scanner_identity",
                       "config_identity", "sha256:"):
            with self.subTest(marker=marker):
                self.assertIn(marker, core)

    def test_duplicate_comparison_is_key_order_independent(self):
        self.assertIn("sameReceipt(", self.html)
        self.assertNotIn("JSON.stringify(staged.get(key))", self.html)

    def test_self_and_pay_it_forward_have_distinct_strokes(self):
        links = [ln for ln in self.diagram.splitlines()
                 if re.search(r"\s(-->|==>|-\.->)", ln)
                 and not ln.strip().startswith("%%")]
        idx = {lbl: i for i, ln in enumerate(links)
               for lbl in ("SELF_REENTRY", "PAY_IT_FORWARD") if lbl in ln}
        self.assertEqual(set(idx), {"SELF_REENTRY", "PAY_IT_FORWARD"})
        styles = dict(re.findall(r"linkStyle (\d+) ([^;\n]+)", self.diagram))
        self_style = styles.get(str(idx["SELF_REENTRY"]))
        fwd_style = styles.get(str(idx["PAY_IT_FORWARD"]))
        self.assertIsNotNone(self_style)
        self.assertIsNotNone(fwd_style)
        self.assertIn("stroke-dasharray", self_style)
        self.assertIn("stroke-dasharray", fwd_style)
        self.assertNotEqual(self_style.strip(), fwd_style.strip())
        # Monochrome: link styles must not introduce colour.
        self.assertNotRegex(self_style + fwd_style, r"#|stroke:")

    @unittest.skipUnless(shutil.which("node"), "node not on PATH")
    def test_receipt_core_behaviour_in_node(self):
        harness = _receipt_core(self.html) + r"""
const base={schema:'code-purple.observation.v1',repository:'GBOGEB/CODEX',
 source_sha:'a'.repeat(40),observed_at:'2026-10-18T12:00:00Z',producer:'ci',
 disposition:'PASS',run_id:1,run_attempt:1,job_id:2,
 receipt_digest:'sha256:'+'b'.repeat(64),scanner_identity:'osv-scanner@2.3.5',
 config_identity:'osv-scanner.yml@'+'c'.repeat(40)};
const out={};
const rejects=k=>{const v={...base};delete v[k];try{validate(v);return false}catch(e){return true}};
out.valid=(()=>{try{validate({...base});return true}catch(e){return false}})();
out.noDigest=rejects('receipt_digest');
out.noScanner=rejects('scanner_identity');
out.noConfig=rejects('config_identity');
out.badDigest=(()=>{try{validate({...base,receipt_digest:'deadbeef'});return false}catch(e){return true}})();
const reordered=Object.fromEntries(Object.entries(base).reverse());
out.reorderedSame=sameReceipt(base,reordered);
out.nestedReorderedSame=sameReceipt({a:{x:1,y:[1,{p:1,q:2}]}},{a:{y:[1,{q:2,p:1}],x:1}});
out.contradictionDetected=!sameReceipt(base,{...base,disposition:'FAIL'});
out.arrayOrderMatters=!sameReceipt({a:[1,2]},{a:[2,1]});
console.log(JSON.stringify(out));
"""
        res = subprocess.run(["node", "-e", harness], capture_output=True,
                             text=True, timeout=60, check=False)
        self.assertEqual(res.returncode, 0, res.stderr)
        result = json.loads(res.stdout)
        self.assertEqual(len(result), 9)
        for name, ok in result.items():
            with self.subTest(case=name):
                self.assertTrue(ok)

    def test_crews_are_roles_not_launch_claims(self):
        for role in ("Reader", "Deep Reader", "Scout", "Ambulance",
                     "Dispatcher", "Repair Worker", "Runtime/LDAB",
                     "Independent Reviewer", "REX Historian"):
            self.assertIn(role, self.html)
        self.assertIn("UNKNOWN", self.html)

    def test_canonical_methods_and_authority_retained(self):
        for method in ("CODE PURPLE", "EVERRED", "NEVERGREEN", "3PR",
                       "MIP", "3PC", "3P3", "DMAIC", "QPS"):
            self.assertIn(method, self.contract)
        self.assertIn("not an independent scheduler", self.contract.lower())
        self.assertIn("protected main", self.contract)


if __name__ == "__main__":
    unittest.main()
