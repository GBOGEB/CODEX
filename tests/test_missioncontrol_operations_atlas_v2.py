"""CI source contracts for the CODEX Mission Control V2 read-only atlas."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data/missioncontrol_operations_atlas_v2.json"
HTML = ROOT / "docs/missioncontrol_operations_atlas.html"
MERMAID = ROOT / "docs/missioncontrol_operations_atlas_v2.mmd"


def source():
    return json.loads(DATA.read_text(encoding="utf-8"))


def test_source_populations_and_cardinalities():
    d=source()
    assert d["schema"] == "missioncontrol.federated.operations_atlas.v2"
    assert len(d["sources"])==4 and len(d["nodes"])==32 and len(d["edges"])==43
    assert d["snapshot"]["repo_count"]==5 and d["snapshot"]["verified_graph_families"]==8
    assert len({n["id"] for n in d["nodes"]})==32


def test_registry_is_source_owned_and_sha_pinned():
    d=source(); ids={n["id"] for n in d["nodes"]}
    families=[]
    for s in d["sources"]:
        assert re.fullmatch(r"[0-9a-f]{40}",s["sha"])
        assert re.fullmatch(r"[0-9a-f]{40}",s["blob"])
        assert s["sha"] in s["url"] and s["path"] in s["url"]
        families.extend(s["families"])
    assert len(families)==8
    assert {"reg_"+f for f in families}.issubset(ids)


def test_endpoints_and_dependency_dag_have_no_cycle():
    d=source(); nodes={n["id"] for n in d["nodes"]}
    graph={n:[] for n in nodes}
    for e in d["edges"]:
        assert e["source"] in nodes and e["target"] in nodes
        if e["kind"]=="dependency":graph[e["source"]].append(e["target"])
    active=set();done=set()
    def visit(n):
        assert n not in active, "same-pulse cycle"
        if n in done:return
        active.add(n)
        for v in graph[n]:visit(v)
        active.remove(n);done.add(n)
    for n in nodes:visit(n)


def test_proposed_cross_repository_links_do_not_claim_receipts():
    d=source();links=[e for e in d["edges"] if e["kind"]=="federation"]
    assert len(links)==3
    assert all(e["binding"]=="DECLARED_EDGE_NO_RECEIPT" and e["executable"] is False for e in links)
    assert all(e["executable"] is False for e in d["edges"])


def test_default_deny_authority_barrier():
    d=source();s=d["snapshot"]
    assert s["merge_admission"]=="HOLD" and s["mutation_enabled"] is False
    assert s["authority_transfer"] is False and s["security_waiver"] is False
    assert s["authenticated_worker_launches"] is None
    assert s["canonical_master_dags_path"] is None and s["matched_coverage_delta"] is None
    assert all(not w["approved"] and w["principal"] is None and w["run_id"] is None for w in d["workers"])


def test_embedded_projection_equal_to_versioned_json():
    page=HTML.read_text(encoding="utf-8")
    match=re.search(r'<script id="atlas-data" type="application/json">([\s\S]*?)</script>',page)
    assert match and json.loads(match.group(1))==source()
    canonical=json.dumps(source(),sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() in page


def test_html_control_surfaces_accessible_and_read_only():
    page=HTML.read_text(encoding="utf-8")
    for word in ['MISSION CONTROL','Scheduler / Workers','SIPOC & Processes','Telemetry & Lineage',
                 'No live refresh','No workers launched by this HTML','QUALIFICATION: DENY']:
        assert word in page
    for element in ['dag','filter','repo','edges','clear','workerChoice','evaluate',
                    'launchSearch','launchRepo','launchList','sipocBody']:
        assert f'id="{element}"' in page
    assert 'role="button"' in page and 'keydown' in page
    assert 'fetch(' not in page and 'github_token' not in page.lower()


def test_mermaid_is_the_same_directed_graph():
    d=source();t=MERMAID.read_text(encoding="utf-8")
    assert t.startswith('flowchart LR\n')
    for e in d["edges"]:
        assert f'{e["source"]} ' in t and f'|{e["kind"]}| {e["target"]}' in t
    assert t.count('-.->|federation|')==3


def test_launches_are_explicit_source_or_owner_links():
    d=source()
    assert len(d["launches"])>=20
    assert all(x["url"].startswith('https://github.com/GBOGEB/') for x in d["launches"])
    assert any(x["title"].startswith('CODEX federated launchpad') for x in d["launches"])
