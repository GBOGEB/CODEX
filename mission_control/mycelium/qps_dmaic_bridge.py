#!/usr/bin/env python3
"""Non-admitting QPS review-DMAIC -> CODEX MYCELIUM observation bridge.

The producing QPS head and consuming CODEX head are caller-supplied reference
identities, not authenticated GitHub facts. Raw QPS review data are never fetched
or published by this module. Generated files are local scratch projections only.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

INPUT_SCHEMA = "qps.review-dmaic-score/1.0"
OUTPUT_SCHEMA = "codepurple.qps.review-dmaic-bridge.v1"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
MAX_INPUT = 2 * 1024 * 1024
FAMILIES = ("SLD", "PID", "TS")
CLASSES = {"BASELINE", "NON_COMPARABLE_WITHHELD", "IDENTICAL_REPLAY_NOT_PROGRESS",
           "COMPARABLE_REVIEW_ANALYSIS"}


class SourceWithheld(ValueError):
    """Missing, ambiguous or inadmissible source evidence."""


def need(ok, reason):
    if not ok:
        raise SourceWithheld(reason)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def unique_object(pairs):
    result = {}
    for k, v in pairs:
        need(k not in result, "duplicated JSON member")
        result[k] = v
    return result


def refuse_constant(value):
    raise SourceWithheld("non-finite JSON number")


def parse(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_INPUT, "invalid or oversized source")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=refuse_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise SourceWithheld("invalid JSON source") from exc


def load_pinned(path, expected_sha256):
    need(type(expected_sha256) is str and SHA64.fullmatch(expected_sha256),
         "independent payload SHA-256 pin required")
    need(path.is_file() and not path.is_symlink() and path.stat().st_size <= MAX_INPUT,
         "source file absent, linked or oversized")
    data = path.read_bytes()
    need(sha256(data) == expected_sha256, "payload pin mismatch")
    return parse(data)


def _nonnegative_int(value):
    return type(value) is int and 0 <= value <= 1000000


def validate_source(report):
    need(type(report) is dict and report.get("schema") == INPUT_SCHEMA,
         "unsupported producing schema")
    need(report.get("mode") == "OBSERVE" and report.get("admission") == "OBSERVATION_ONLY"
         and report.get("evidence_class") in ("SYNTHETIC_FIXTURE", "OBSERVED_UNVERIFIED")
         and report.get("dispatched_workflows") == 0 and report.get("github_mutations") == 0,
         "producer claimed execution or authority")
    need(type(report.get("input_manifest_sha256")) is str and
         SHA64.fullmatch(report["input_manifest_sha256"]), "unbound input manifest")
    # Do not accidentally publish reviewer, vendor or bidder content.
    def walk(value):
        if type(value) is dict:
            need(not ({"comments", "body_verbatim", "candidate_answer", "author", "source_locator"}
                      & set(value)), "source carries private review content")
            for item in value.values():
                walk(item)
        elif type(value) is list:
            for item in value:
                walk(item)
    walk(report)

    s = report.get("score")
    need(type(s) is dict and s.get("authority_transfer") is False
         and s.get("formal_credit_delta") == 0 and s.get("engineering_admission") == "HOLD"
         and s.get("publication_admission") == "HOLD", "QPS authority escalation")
    for key, expected in (("native_office_qa", "NOT_EXECUTED"),
                          ("exact_head_ci", "NOT_VERIFIED"),
                          ("receipt_pin_integrity", "PASS"),
                          ("dag_cycle_guard", "PASS"),
                          ("handoff_direction_guard", "PASS")):
        need(s.get(key) == expected, "unsupported producer control state: " + key)
    for key in ("first_red_causal_recurrence", "consumer_adoption", "queue_p50_p95", "pca_bt"):
        need(type(s.get(key)) is str and s[key].startswith("WITHHELD"),
             "unsupported metric promotion: " + key)
    for key in ("comment_identity_duplicates", "unique_comment_keys",
                "comment_observations", "repeat_observations"):
        need(_nonnegative_int(s.get(key)), "invalid comment counter: " + key)
    need(s["comment_identity_duplicates"] == 0, "duplicate identities not admitted")
    pulses = report.get("pulses")
    need(type(pulses) is list and 0 < len(pulses) <= 64
         and type(report.get("pulse_count")) is int and len(pulses) == report["pulse_count"],
         "pulse denominator mismatch")
    seen, ords, counts, comments, comparable = set(), set(), 0, set(), 0
    last_ordinal = -1
    for p in pulses:
        need(type(p) is dict, "invalid pulse row")
        pid, ordinal = p.get("pulse_id"), p.get("ordinal")
        need(type(pid) is str and re.fullmatch(r"[a-zA-Z0-9._:-]{1,96}", pid)
             and pid not in seen and type(ordinal) is int and ordinal > last_ordinal
             and ordinal not in ords, "duplicate or out-of-order pulse")
        seen.add(pid); ords.add(ordinal); last_ordinal = ordinal
        for key in ("source_sha256", "workitems_receipt_sha256", "producer_receipt_sha256"):
            need(type(p.get(key)) is str and SHA64.fullmatch(p[key]),
                 "malformed source/receipt SHA: " + key)
        for key in ("entry_count", "thread_count", "candidate_answers", "declared_evidence_links"):
            need(_nonnegative_int(p.get(key)), "missing/invalid count: " + key)
        need(p["entry_count"] > 0 and p["thread_count"] > 0
             and p["thread_count"] <= p["entry_count"]
             and 0 <= p["candidate_answers"] <= p["entry_count"]
             and p["declared_evidence_links"] <= p["entry_count"],
             "invalid population bounds")
        for key, observed in (("expected_entries", "entry_count"),
                              ("expected_threads", "thread_count")):
            if p.get(key) is not None:
                need(type(p[key]) is int and p[key] == p[observed],
                     "frozen source count mismatch")
        counts += p["entry_count"]
        comments.add(p.get("source_document_id"))  # Count only; never publish identities.
    need(s["comment_observations"] == counts
         and s["unique_comment_keys"] <= counts
         and s["repeat_observations"] == counts - s["unique_comment_keys"],
         "counter consistency failed")
    if s.get("source_population_reconciliation") == "PASS":
        need(all(p.get("expected_entries") is not None and
                 p.get("expected_threads") is not None for p in pulses),
             "unfrozen population declared PASS")
    else:
        need(s.get("source_population_reconciliation") == "WITHHELD",
             "invalid population proof state")
    trends = report.get("trend")
    need(type(trends) is list and len(trends) == len(pulses), "temporal trend denominator mismatch")
    for i, (t, p) in enumerate(zip(trends, pulses)):
        need(type(t) is dict and t.get("pulse_id") == p["pulse_id"]
             and t.get("class") in CLASSES, "unbound temporal comparison")
        if i == 0:
            need(t["class"] == "BASELINE" and t.get("candidate_answer_delta") is None,
                 "first pulse cannot claim improvement")
        else:
            need(t["class"] != "BASELINE", "duplicate baseline")
            delta = t.get("candidate_answer_delta")
            if t["class"] == "NON_COMPARABLE_WITHHELD":
                need(delta is None, "non-comparable delta cannot be measured")
            else:
                need(type(delta) is int and abs(delta) <= max(p["entry_count"], pulses[i-1]["entry_count"]),
                     "invalid candidate delta")
                if t["class"] == "IDENTICAL_REPLAY_NOT_PROGRESS":
                    need(delta == 0, "replay cannot be progress")
                else:
                    comparable += 1
    order = report.get("dag_order")
    need(type(order) is list and 0 < len(order) <= 64
         and all(type(x) is str and x for x in order)
         and len(set(order)) == len(order), "invalid producer DAG ordering claim")
    for key in ("dag_edge_count", "candidate_handoff_count"):
        need(_nonnegative_int(report.get(key)), "invalid graph counter")
    return {"pulse_count":len(pulses),"unique_comments":s["unique_comment_keys"],
            "comment_observations":counts,"repeat_observations":s["repeat_observations"],
            "comparable_candidate_transitions":comparable,
            "distinct_review_documents":len(comments),
            "source_population_claim":s["source_population_reconciliation"],
            "evidence_class":report["evidence_class"]}


def bridge(raw, *, expected_payload_sha256, expected_qps_head, expected_codex_head):
    for label, value in (("payload", expected_payload_sha256),):
        need(type(value) is str and SHA64.fullmatch(value), "invalid externally bound " + label)
    for label, value in (("QPS", expected_qps_head), ("CODEX", expected_codex_head)):
        need(type(value) is str and SHA40.fullmatch(value), "invalid " + label + " head pin")
    need(sha256(raw) == expected_payload_sha256, "payload pin mismatch")
    obj = parse(raw)
    measured = validate_source(obj)
    out = {
        "schema":OUTPUT_SCHEMA,"mode":"OBSERVE_ONLY","admission":"DEFER",
        "source":{"repository":"GBOGEB/cryoplant-project",
                  "source_head_reference":expected_qps_head,
                  "source_payload_sha256":expected_payload_sha256,
                  "source_manifest_sha256":obj["input_manifest_sha256"],
                  "head_binding":"CALLER_DECLARED_NOT_GITHUB_AUTHENTICATED"},
        "consumer":{"repository":"GBOGEB/CODEX", "head_reference":expected_codex_head,
                    "head_binding":"CALLER_DECLARED_NOT_GITHUB_AUTHENTICATED"},
        "metrics":{**measured, "operational_throughput":"WITHHELD_NO_NATIVE_EXECUTION_COHORT",
                    "engineering_closure":"WITHHELD_NO_OWNER_DECISION",
                    "consumer_adoption":"WITHHELD_NO_INDEPENDENT_RECEIPT",
                    "native_scaling":"WITHHELD_NO_DIVERSE_BINARY_QA",
                    "p50_p95":"WITHHELD_NO_NATIVE_CLOCKS"},
        "handoff":{"edge_type":"PAY_IT_FORWARD","admission":"DEFER",
                   "independent_consumer_proof":False,"dispatch_authorized":False},
        "provenance":{"payload_hash_verified":True,"manifest_bytes_verified":False,
                      "producer_git_origin_authenticated":False,
                      "native_source_bytes_verified":False,
                      "consumer_independent_acceptance_verified":False},
        "controls":{"native_office":"WITHHELD","exact_head_ci":"NOT_VERIFIED_BY_BRIDGE",
                    "engineering_admission":"HOLD","publication_admission":"HOLD",
                    "merge_admission":"HOLD","source_private_bytes_published":False},
        "authority_transfer":False,"formal_credit_delta":0,
        "github_mutations":0,"dispatched_workflows":0,
    }
    out["receipt_sha256"] = sha256(canonical(out))
    return out


def render_html(report):
    e = lambda x: html.escape(str(x), quote=True)
    metrics = report["metrics"]
    tiles = [("PULSES",metrics["pulse_count"]),("UNIQUE KEYS",metrics["unique_comments"]),
             ("OCCURRENCES",metrics["comment_observations"]),
             ("REPLAY OBSERVATIONS",metrics["repeat_observations"]),
             ("NATIVE SCALE", "WITHHELD"),("ADMISSION", "DEFER")]
    cards = "".join('<article class="tile"><small>%s</small><strong>%s</strong></article>' % (e(a),e(b)) for a,b in tiles)
    panels = [
        ("01 / Define", "QPS review-DMAIC aggregate. External SHA-256 payload pin verified; origin authentication withheld."),
        ("02 / Measure", "%s pulses / %s distinct review documents, as claimed by the producer." % (e(metrics["pulse_count"]),e(metrics["distinct_review_documents"]))),
        ("03 / Analyse", "%s comparable candidate-answer transitions. These are not root closures or effectiveness measurements." % e(metrics["comparable_candidate_transitions"])),
        ("04 / Improve", "Existing QPS source, W383, R07 and MINERVA_PID generators retain their own authority. This bridge does not launch them."),
        ("05 / Control", "Native Office, engineering acceptance and exact-head CI are withheld in the bridge. Publication HOLD."),
        ("06 / Federation", "PAY_IT_FORWARD / DEFER. No automatic adoption; CODEX owns presentation only, QPS owns engineering truth."),
    ]
    grid = "".join('<section><h2>%s</h2><p>%s</p></section>' % (e(a), b) for a,b in panels)
    return """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MYCELIUM · QPS DMAIC intake</title><style>
:root{--purple:#39135f;--violet:#74349c;--ink:#231633;--blush:#f6e1ec}*{box-sizing:border-box}body{margin:0;font:15px Aptos,'Segoe UI',sans-serif;background:#faf8fc;color:var(--ink)}header{background:var(--purple);color:#fff;padding:28px max(20px,5vw)}h1{font-size:clamp(23px,3vw,34px);margin:0 0 8px}.eyebrow{font:12px Consolas,monospace}main{max-width:1380px;margin:auto;padding:18px}.splash,.panels{display:grid;gap:13px}.splash{grid-template-columns:repeat(auto-fit,minmax(160px,1fr));margin-bottom:18px}.panels{grid-template-columns:repeat(2,minmax(0,1fr))}.tile,.panels section{min-width:0;background:#fff;border:1px solid #e5ddee;border-radius:10px;padding:16px}.tile{border-top:4px solid var(--violet)}small{display:block;color:#695c71}.tile strong{display:block;font-size:26px;margin-top:7px;overflow-wrap:anywhere}h2{color:var(--purple);font-size:17px;margin:0}p{line-height:1.5;overflow-wrap:anywhere}.notice{background:var(--blush);padding:12px;border-radius:6px;margin-bottom:15px}footer{text-align:center;padding:22px;color:#73697b}@media(max-width:760px){.panels{grid-template-columns:1fr}}</style></head><body><header><div class="eyebrow">CODEX / MYCELIUM · READ-ONLY BRIDGE · NO ENGINEERING CREDIT</div><h1>QPS DMAIC — SCORE</h1><div>Six-view source-bound observation · admission DEFER</div></header><main><div class="notice">Source score SHA-256: <code>%s</code> · Producer head is a caller-supplied reference, not independently authenticated.</div><div class="splash">%s</div><div class="panels">%s</div></main><footer>Local scratch output only · Do not publish private QPS evidence to public CODEX Pages</footer></body></html>""" % (e(report["source"]["source_payload_sha256"]),cards,grid)


def publish(report, out_dir):
    need(not out_dir.is_symlink(), "linked output root refused")
    base = out_dir / ("qps-dmaic-bridge-" + report["source"]["source_payload_sha256"][:16])
    docs = {"bridge.json":canonical(report), "index.html":(render_html(report)+"\n").encode("utf-8")}
    docs["SHA256SUMS"] = ("".join(sha256(v)+"  "+k+"\n" for k,v in sorted(docs.items()))).encode("ascii")
    if base.exists():
        need(base.is_dir() and not base.is_symlink() and
             {p.name for p in base.iterdir()} == set(docs) and
             all((base/k).is_file() and not (base/k).is_symlink() and (base/k).read_bytes()==v
                 for k,v in docs.items()), "output replay collision or drift")
        return base
    need(not out_dir.exists() or out_dir.is_dir(), "output parent is not a directory")
    out_dir.mkdir(parents=True,exist_ok=True)
    base.mkdir()
    for name,blob in docs.items():
        with (base/name).open("xb") as f:
            f.write(blob)
    return base


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--score",type=Path,required=True)
    p.add_argument("--expected-payload-sha256",required=True)
    p.add_argument("--expected-qps-head",required=True)
    p.add_argument("--expected-codex-head",required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        source=args.score.resolve()
        output=args.out_dir.resolve()
        repo_root=Path(__file__).resolve().parents[2]
        for forbidden in (repo_root/"docs",repo_root/"mission_control"):
            need(not output.is_relative_to(forbidden.resolve()),
                 "private projection cannot be written into public CODEX source tree")
        need(not args.score.is_symlink() and source!=output and not output.is_relative_to(source),
             "aliased source/output")
        need(args.score.is_file() and args.score.stat().st_size<=MAX_INPUT,
             "source missing or oversized")
        data=args.score.read_bytes()
        result=bridge(data,expected_payload_sha256=args.expected_payload_sha256,
                      expected_qps_head=args.expected_qps_head,
                      expected_codex_head=args.expected_codex_head)
        dest=publish(result,args.out_dir)
    except (SourceWithheld,OSError) as exc:
        print(json.dumps({"admission":"HOLD","reason":str(exc)}))
        return 2
    print(json.dumps({"admission":"DEFER","directory":str(dest),
                      "source_payload_sha256":result["source"]["source_payload_sha256"]}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())