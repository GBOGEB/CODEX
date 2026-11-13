"""QPS -> CODEX public-contract adversaries. Synthetic only; no QPS source bytes."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parents[1]
FILE = HERE / "mission_control" / "mycelium" / "qps_dmaic_bridge.py"
SPEC = importlib.util.spec_from_file_location("qps_dmaic_bridge", FILE)
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)
QPS_SHA = "a" * 40
CODEX_SHA = "b" * 40


def score():
    pulse = dict(pulse_id="N0",ordinal=0,source_document_id="SYNTHETIC",
                 source_sha256="a"*64,producer_receipt_sha256="b"*64,
                 workitems_receipt_sha256="c"*64,entry_count=1,thread_count=1,
                 expected_entries=1,expected_threads=1,candidate_answers=0,
                 declared_evidence_links=0)
    newer = {**pulse,"pulse_id":"N1","ordinal":1,"workitems_receipt_sha256":"d"*64,
             "candidate_answers":1}
    return dict(schema="qps.review-dmaic-score/1.0",input_manifest_sha256="e"*64,
                mode="OBSERVE",evidence_class="SYNTHETIC_FIXTURE",admission="OBSERVATION_ONLY",
                dispatched_workflows=0,github_mutations=0,pulse_count=2,pulses=[pulse,newer],
                trend=[{"pulse_id":"N0","class":"BASELINE","candidate_answer_delta":None},
                       {"pulse_id":"N1","class":"COMPARABLE_REVIEW_ANALYSIS","candidate_answer_delta":1}],
                dag_order=["INTAKE","REVIEW"],dag_edge_count=1,candidate_handoff_count=1,
                score=dict(authority_transfer=False,formal_credit_delta=0,
                           engineering_admission="HOLD",publication_admission="HOLD",
                           native_office_qa="NOT_EXECUTED",exact_head_ci="NOT_VERIFIED",
                           receipt_pin_integrity="PASS",dag_cycle_guard="PASS",handoff_direction_guard="PASS",
                           first_red_causal_recurrence="WITHHELD_NO_ROOT_EVENTS",
                           consumer_adoption="WITHHELD_NO_ACCEPTANCE",
                           queue_p50_p95="WITHHELD_NO_CLOCK",pca_bt="WITHHELD_NO_POPULATION",
                           source_population_reconciliation="PASS",comment_identity_duplicates=0,
                           unique_comment_keys=1,comment_observations=2,repeat_observations=1))


def run(record):
    raw=bridge.canonical(record)
    return bridge.bridge(raw,expected_payload_sha256=bridge.sha256(raw),
                         expected_qps_head=QPS_SHA,expected_codex_head=CODEX_SHA)


def test_structured_non_admitting_bridge():
    x=run(score())
    assert x["admission"]=="DEFER"
    assert x["source"]["head_binding"]=="CALLER_DECLARED_NOT_GITHUB_AUTHENTICATED"
    assert x["provenance"]["producer_git_origin_authenticated"] is False
    assert x["controls"]["engineering_admission"]=="HOLD"
    assert x["metrics"]["pulse_count"]==2
    assert x["metrics"]["comparable_candidate_transitions"]==1
    assert x["formal_credit_delta"]==x["github_mutations"]==0


def test_deterministic_replay():
    assert run(score())==run(score())
    assert run(score())["receipt_sha256"]==bridge.sha256(
        bridge.canonical({k:v for k,v in run(score()).items() if k!="receipt_sha256"}))


def test_sanitized_six_view_html():
    body=bridge.render_html(run(score()))
    assert body.count("<section>")==6
    assert "WITHHELD" in body and "NO ENGINEERING CREDIT" in body
    assert "candidate_answer" not in body
    assert "SYNTHETIC" not in body


def test_output_content_addressed_no_clobber(tmp_path):
    x=run(score())
    p=bridge.publish(x,tmp_path)
    assert p==bridge.publish(x,tmp_path)
    assert {f.name for f in p.iterdir()}=={"bridge.json","index.html","SHA256SUMS"}
    assert (p/"SHA256SUMS").read_text().count("\n")==2
    (p/"index.html").write_text("evil")
    with pytest.raises(bridge.SourceWithheld,match="collision"):
        bridge.publish(x,tmp_path)


def test_independent_pin_mismatch():
    raw=bridge.canonical(score())
    with pytest.raises(bridge.SourceWithheld,match="payload pin mismatch"):
        bridge.bridge(raw,expected_payload_sha256="0"*64,
                      expected_qps_head=QPS_SHA,expected_codex_head=CODEX_SHA)

@pytest.mark.parametrize("field,bad",[("expected_qps_head","c"*39),
                                      ("expected_codex_head","d"*41),
                                      ("expected_payload_sha256", "z"*64),
                                      ("expected_qps_head", 7)])
def test_invalid_external_binding(field,bad):
    raw=bridge.canonical(score())
    args=dict(expected_payload_sha256=bridge.sha256(raw),
              expected_qps_head=QPS_SHA,expected_codex_head=CODEX_SHA)
    args[field]=bad
    with pytest.raises(bridge.SourceWithheld):
        bridge.bridge(raw,**args)

@pytest.mark.parametrize("field,value",[
    ("engineering_admission","ACCEPT"),("publication_admission","PASS"),
    ("authority_transfer",True),("formal_credit_delta",1),
    ("native_office_qa","PASS"),("exact_head_ci","PASS"),
    ("consumer_adoption","100%"),("first_red_causal_recurrence",0),
    ("queue_p50_p95",{"p95":0}),("pca_bt","PASS"),
    ("dag_cycle_guard","FAIL"),("comment_identity_duplicates",1)])
def test_privilege_or_metric_escalation(field,value):
    s=score();s["score"][field]=value
    with pytest.raises(bridge.SourceWithheld):
        run(s)

@pytest.mark.parametrize("field,value",[("mode","EXECUTE"),("admission","ACCEPT"),
                                        ("dispatched_workflows",1),("github_mutations",1),
                                        ("evidence_class","ENGINEERING_ACCEPTED")])
def test_producer_runtime_escalation(field,value):
    s=score();s[field]=value
    with pytest.raises(bridge.SourceWithheld):
        run(s)

@pytest.mark.parametrize("field,value",[("entry_count",0),("thread_count",2),
                                         ("candidate_answers",2),("expected_entries",4),
                                         ("source_sha256", "short")])
def test_bad_native_population(field,value):
    s=score();s["pulses"][0][field]=value
    with pytest.raises(bridge.SourceWithheld):
        run(s)

@pytest.mark.parametrize("mutation",[
    lambda d:d["pulses"][1].update(pulse_id="N0"),
    lambda d:d["pulses"][1].update(ordinal=0),
    lambda d:d.update(pulse_count=3),
    lambda d:d["score"].update(comment_observations=999),
    lambda d:d["score"].update(repeat_observations=999),
    lambda d:d["score"].update(source_population_reconciliation="TRUE"),
    lambda d:d["trend"][0].update(candidate_answer_delta=1),
    lambda d:d["trend"][1].update(**{"class":"NON_COMPARABLE_WITHHELD","candidate_answer_delta":1}),
    lambda d:d["trend"][1].update(**{"class":"BASELINE"}),
    lambda d:d.update(dag_order=["A","A"]),
])
def test_forged_temporal_denominators(mutation):
    s=score();mutation(s)
    with pytest.raises(bridge.SourceWithheld):
        run(s)


def test_unfrozen_claim_of_complete_population():
    s=score();s["pulses"][0]["expected_entries"]=None
    with pytest.raises(bridge.SourceWithheld,match="unfrozen population"):
        run(s)

@pytest.mark.parametrize("private_key",["comments","body_verbatim","candidate_answer","author","source_locator"])
def test_private_review_fields_refused(private_key):
    s=score();s[private_key]="Private reviewer text"
    with pytest.raises(bridge.SourceWithheld,match="private review content"):
        run(s)


def test_duplicate_json_members_fail_closed():
    raw=b'{"x":1,"x":2}'
    with pytest.raises(bridge.SourceWithheld,match="duplicated JSON"):
        bridge.parse(raw)


def test_nonfinite_json_number_fails_closed():
    with pytest.raises(bridge.SourceWithheld,match="non-finite"):
        bridge.parse(b'{"x":NaN}')


def test_oversized_and_empty_input_fails_closed():
    with pytest.raises(bridge.SourceWithheld): bridge.parse(b'')
    with pytest.raises(bridge.SourceWithheld): bridge.parse(b'x' * (bridge.MAX_INPUT+1))



def test_cli_fails_closed_for_public_pages_output(tmp_path,monkeypatch,capsys):
    path=tmp_path/"score.json"; raw=bridge.canonical(score());path.write_bytes(raw)
    public=(HERE/"docs"/"data"/"private_metrics").resolve()
    monkeypatch.setattr(sys,"argv",["qps_dmaic_bridge.py","--score",str(path),
      "--expected-payload-sha256",bridge.sha256(raw),"--expected-qps-head",QPS_SHA,
      "--expected-codex-head",CODEX_SHA,"--out-dir",str(public)])
    assert bridge.main()==2
    assert "public CODEX" in capsys.readouterr().out
    assert not public.exists()


def test_cli_permitted_local_output(tmp_path,monkeypatch,capsys):
    path=tmp_path/"score.json";raw=bridge.canonical(score());path.write_bytes(raw)
    monkeypatch.setattr(sys,"argv",["qps_dmaic_bridge.py","--score",str(path),
      "--expected-payload-sha256",bridge.sha256(raw),"--expected-qps-head",QPS_SHA,
      "--expected-codex-head",CODEX_SHA,"--out-dir",str(tmp_path/"out")])
    assert bridge.main()==0
    assert '"admission": "DEFER"' in capsys.readouterr().out

def test_mobile_sha_digest_does_not_force_horizontal_overflow():
    body = bridge.render_html(run(score()))
    assert '.notice code{word-break:break-all}' in body
