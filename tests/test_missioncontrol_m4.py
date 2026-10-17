"""Additive Mission Control M4 contracts: source parity, status semantics and no dispatch."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/data/missioncontrol_m4_status.json'
HTML=ROOT/'docs/missioncontrol_operations_atlas_m4.html'
JS=ROOT/'scripts/missioncontrol_m4_review.js'
CSS=ROOT/'scripts/missioncontrol_m4_review.css'

def _data():return json.loads(DATA.read_text(encoding='utf-8'))

def test_21_statuses_are_source_bound_and_unique():
 d=_data(); p=d['pr_merges']; assert len(p)==21; assert len({(x['repo'],x['number']) for x in p})==21
 assert all(x['state']=='MERGED' and re.fullmatch(r'[0-9a-f]{40}',x['merge_sha']) for x in p)

def test_fanin_depth_not_main_admission():
 d=_data(); f=[x for x in d['pr_merges'] if x['target_kind']=='feature']
 assert {x['number'] for x in f}=={2133,2147,2155}; assert not any(x['target'] in ('main','master') for x in f)

def test_all_current_review_issues_explicitly_open():
 d=_data();assert len(d['issues'])==6 and all(x['state']=='OPEN' for x in d['issues'])

def test_non_atomic_issues_pr_population():
 d=_data();assert sum(x['open_issues'] for x in d['repo_census'])==137
 assert sum(x['open_prs'] for x in d['repo_census'])==39

def test_non_additive_graph_counts():
 x=_data()['topology'];assert (x['source_atlas_graph_nodes'],x['source_atlas_graph_edges'])==(32,43)
 assert (x['top21_model_nodes'],x['top21_model_edges'],x['represented_file_atoms'])==(716,734,26836)

def test_changed_source_denominator_not_uplift():
 a,b=_data()['coverage'];assert (a['covered'],a['eligible'],b['covered'],b['eligible'])==(220,562,217,560)
 assert a['source_sha']!=b['source_sha'] and b['eligible']-a['eligible']==-2 and b['covered']-a['covered']==-3

def test_source_snapshot_cannot_promote_dispatch():
 x=_data()['authority'];assert x['main_admission']=='HOLD' and x['mutation_enabled'] is False
 assert x['authenticated_worker_dispatch'] is None and x['canonical_master_dags_path'] is None

def test_rendered_source_json_parity():
 m=re.search(r'<script id="m4-source" type="application/json">(.*?)</script>',HTML.read_text(encoding='utf-8'))
 assert m and json.loads(m.group(1))==_data()

def test_rendered_script_and_css_are_exact():
 html=HTML.read_text(encoding='utf-8')
 assert JS.read_text(encoding='utf-8')+'\n</script>' in html
 assert CSS.read_text(encoding='utf-8')+'\n</style>' in html

def test_annotations_are_local_only_and_exportable():
 s=JS.read_text(encoding='utf-8');assert 'localStorage.setItem(KEY' in s
 assert 'MissionControlReview=' in s and 'missioncontrol:annotation-saved' in s
 assert 'fetch(' not in s and 'XMLHttpRequest' not in s

def test_review_links_preserve_safe_target():
 s=JS.read_text(encoding='utf-8');assert 'rel="noopener noreferrer"' in s
 assert 'data-m4-note=' in s and 'launch:' in s and 'graph-node:' in s

def test_clash_risk_fixes_present():
 s=CSS.read_text(encoding='utf-8');j=JS.read_text(encoding='utf-8')
 assert '.m4-legend' in s and '.m4-viz svg' in s
 assert 'Truncated Y-axis 70–110' in j and 'Δ eligible' in j and '220' in json.dumps(_data()['coverage'])

def test_generated_source_rebuild_parity():
 path=ROOT/'scripts/rebuild_missioncontrol_m4.py';spec=importlib.util.spec_from_file_location('builder',path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 assert module.build()==HTML.read_text(encoding='utf-8')

def test_reverse_wrong_baseline_is_rejected():
 path=ROOT/'scripts/rebuild_missioncontrol_m4.py';spec=importlib.util.spec_from_file_location('builder2',path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 assert module.blob_sha(b'forged source')!=module.BASE_BLOB

def test_source_authority_digest_is_pinned():
 raw=(ROOT/'docs/missioncontrol_operations_atlas.html').read_bytes()
 blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 assert blob=='9b2a09eb7c4b4c718e9cd4924020121bc197f931'
