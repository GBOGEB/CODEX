import copy, json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from mycelium_continuity import admission_timeline as m
from mycelium_continuity.graph import sha256,validate_graph

DATA=json.loads((ROOT/'N9_ADMISSION_READBACK_20261017.json').read_text())
from mycelium_continuity.graph import make_node,make_edge

def fabricated_n8_parent():
    # Deliberately synthetic graph: test paths, not native evidence.
    names=['S-OBSERVE','I-VALIDATE','P-CODE-MAROON','P-PY310','P-GOVERNANCE','P-WORKER-TELEMETRY','O-JOIN','C-ADMISSION']
    nodes=[make_node('sipoc:N1:'+x,x,'SIPOC_INSTANCE','SIPOC',owner='GBOGEB/CODEX',source='SYNTHETIC',role=x[:1],legacy_id=x) for x in names]
    nodes+= [make_node('pr:historical:GBOGEB/ABACUS#'+str(i),'Synthetic '+str(i),'PR','ATOMS',owner='GBOGEB/ABACUS',source='SYNTHETIC',historical=True,repository='GBOGEB/ABACUS',number=i) for i in range(1,23)]
    nodes.append(make_node('sipoc:N8:C-N8-REENTRY','Synthetic preceding epoch','SIPOC_INSTANCE','SIPOC',owner='GBOGEB/CODEX',source='SYNTHETIC'))
    nodes.append(make_node('atom:N8:ABACUS-JOIN-WITHHELD','Synthetic join gap','EVIDENCE_GAP','BD',owner='GBOGEB/ABACUS',source='SYNTHETIC'))
    pairs=[(i,i+1) for i in range(7)]+[(0,2),(0,3),(1,4)]
    edges=[make_edge('sipoc:N1:'+names[a],'sipoc:N1:'+names[b],'SIPOC_DEPENDENCY','SIPOC',binding='DECLARED',source_ref='SYNTHETIC') for a,b in pairs]
    return {'schema':'code-purple.mycelium.graph.v2','nodes':nodes,'edges':edges,'authority_transfer':False,'dispatch_authorized':False,'admission':'HOLD'}
PARENT=fabricated_n8_parent()

def legacy_from_parent():
    return {'instances':[{'id':n['legacy_id']} for n in PARENT['nodes'] if n['id'].startswith('sipoc:N1:')],
            'edges':[{'from':e['from'].removeprefix('sipoc:N1:'),'to':e['to'].removeprefix('sipoc:N1:')} for e in PARENT['edges'] if e['kind']=='SIPOC_DEPENDENCY' and e['from'].startswith('sipoc:N1:')],
            'prs':[{'repo':n['repository'],'pr':n['number']} for n in PARENT['nodes'] if n['kind']=='PR' and n.get('historical')]}

class NativeChronology(unittest.TestCase):
    def test_base_population(self):
        self.assertEqual(m.validate(DATA),{'sources':2,'cases':4})
    def test_observed_dispositions(self):
        p=m.project(DATA)
        self.assertEqual(p['metrics']['nonterminal_at_readback'],2)
        self.assertEqual(p['metrics']['observed_failed'],1)
        self.assertEqual(p['metrics']['observed_success'],1)
        self.assertEqual(p['metrics']['effective_required_status_proven'],0)
        self.assertIsNone(p['metrics']['merged_with_pre_merge_terminal_success_proven'])
        self.assertTrue(all(r['gate'].startswith('HOLD') for r in p['rows']))
    def test_queued_and_failure_are_separate(self):
        p=m.project(DATA)
        self.assertEqual(sum('NONTERMINAL' in r['disposition'] for r in p['rows']),2)
        self.assertEqual(sum('FAILED' in r['disposition'] for r in p['rows']),1)
    def test_timing_cannot_promote(self):
        z=copy.deepcopy(DATA);z['owners'][0]['required_status_verified']=True
        self.assertEqual(m.project(z)['admission'],'HOLD')
    def test_run_concluded_before_merge_branch(self):
        z=copy.deepcopy(DATA);r=z['cases'][-1];r['run_updated_at']='2026-10-17T09:59:59Z'
        self.assertIn('ALREADY_UPDATED',m.project(z)['rows'][-1]['disposition'])
    def test_failed_before_merge_branch(self):
        z=copy.deepcopy(DATA);z['cases'][2]['run_updated_at']='2026-10-17T09:32:00Z'
        self.assertIn('FAILED_RUN_ALREADY',m.project(z)['rows'][2]['disposition'])
    def test_other_terminal_class(self):
        z=copy.deepcopy(DATA);z['cases'][0]['run_status']='completed';z['cases'][0]['run_conclusion']='cancelled'
        self.assertIn('OTHER_TERMINAL',m.project(z)['rows'][0]['disposition'])
    def test_empty_bad_schema_authority_fails(self):
        for action in (lambda d:d.update(schema='wrong'),lambda d:d.update(owners=[]),lambda d:d.update(cases=[]),lambda d:d.update(authority_transfer=True),lambda d:d.update(security_waiver=True),lambda d:d.update(merge_authorized=True),lambda d:d.update(accepted_root_closures=1)):
            z=copy.deepcopy(DATA);action(z)
            with self.subTest(action=action),self.assertRaises(ValueError):m.validate(z)
    def test_source_class_required(self):
        z=copy.deepcopy(DATA);z['observation_class']='DIRECT_NATIVE_ROOT'
        with self.assertRaises(ValueError):m.validate(z)
    def test_duplicate_owners_rejected(self):
        z=copy.deepcopy(DATA);z['owners'].append(copy.deepcopy(z['owners'][0]))
        with self.assertRaises(ValueError):m.validate(z)
    def test_duplicate_pr_rejected(self):
        z=copy.deepcopy(DATA);z['cases'].append(copy.deepcopy(z['cases'][0]));z['cases'][-1]['run_id']=12991
        with self.assertRaises(ValueError):m.validate(z)
    def test_duplicate_run_rejected(self):
        z=copy.deepcopy(DATA);z['cases'].append(copy.deepcopy(z['cases'][0]));z['cases'][-1]['pr']=8219
        with self.assertRaises(ValueError):m.validate(z)
    def test_boolean_identity_rejected(self):
        for col in ('pr','run_id'):
            z=copy.deepcopy(DATA);z['cases'][0][col]=True
            with self.subTest(col=col),self.assertRaises(ValueError):m.validate(z)
    def test_fake_hash_rejected(self):
        for col in ('head_sha','merge_sha','run_head_sha'):
            z=copy.deepcopy(DATA);z['cases'][0][col]='bad'
            with self.subTest(col=col),self.assertRaises(ValueError):m.validate(z)
    def test_sha_mismatch_rejected(self):
        z=copy.deepcopy(DATA);z['cases'][0]['run_head_sha']='a'*40
        with self.assertRaises(ValueError):m.validate(z)
    def test_invalid_conclusion_rejected(self):
        for status,conclusion in [('queued','success'),('completed',None),('running',None)]:
            z=copy.deepcopy(DATA);z['cases'][0].update(run_status=status,run_conclusion=conclusion)
            with self.subTest(status=status),self.assertRaises(ValueError):m.validate(z)
    def test_bad_repo_and_branch_rejected(self):
        for key,value in [('repository','other'),('branch','staging'),('sha','unbound'),('protected',None),('required_status_verified',None),('protection_detail','PERMITTED')]:
            z=copy.deepcopy(DATA);z['owners'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):m.validate(z)
    def test_missing_owner_rejected(self):
        z=copy.deepcopy(DATA);z['owners']=z['owners'][:1]
        with self.assertRaises(ValueError):m.validate(z)
    def test_invalid_timestamp_rejected(self):
        for stamp in ['2026-10-17','2026-13-17T09:00:00Z','2026-10-17T09:00:00+01:00',None]:
            z=copy.deepcopy(DATA);z['cases'][0]['merged_at']=stamp
            with self.subTest(stamp=stamp),self.assertRaises(ValueError):m.validate(z)
    def test_created_after_updated_rejected(self):
        z=copy.deepcopy(DATA);z['cases'][0]['run_updated_at']='2026-10-17T10:00:00Z';z['cases'][0]['run_created_at']='2026-10-17T11:00:00Z'
        with self.assertRaises(ValueError):m.validate(z)
    def test_merge_before_created_rejected(self):
        z=copy.deepcopy(DATA);z['cases'][0]['merged_at']='2026-10-17T10:00:00Z'
        with self.assertRaises(ValueError):m.validate(z)
    def test_bad_event_rejected(self):
        z=copy.deepcopy(DATA);z['cases'][0]['event']='push'
        with self.assertRaises(ValueError):m.validate(z)
    def test_wrong_graph_parent_digest(self):
        with self.assertRaises(ValueError):m.extend_graph(PARENT,legacy_from_parent(),m.project(DATA),parent_sha='a'*64)
    def test_graph_retention_and_expansion(self):
        g,metrics=m.extend_graph(PARENT,legacy_from_parent(),m.project(DATA),parent_sha=sha256(PARENT))
        self.assertGreater(len(g['nodes']),len(PARENT['nodes']))
        self.assertGreater(len(g['edges']),len(PARENT['edges']))
        self.assertEqual(metrics['legacy_sipoc_retention'],{'numerator':8,'denominator':8})
        self.assertEqual(metrics['legacy_edge_retention'],{'numerator':10,'denominator':10})
        self.assertEqual(metrics['legacy_pr_retention'],{'numerator':22,'denominator':22})
        self.assertIsNone(metrics['accepted_causal_root_closures'])
        self.assertGreaterEqual(len(validate_graph(g)['waves']),5)
    def test_duplicate_extension_fails(self):
        g,_=m.extend_graph(PARENT,legacy_from_parent(),m.project(DATA),parent_sha=sha256(PARENT))
        with self.assertRaises(ValueError):m.extend_graph(g,legacy_from_parent(),m.project(DATA),parent_sha=sha256(g))
    def test_parent_unchanged(self):
        before=sha256(PARENT)
        m.extend_graph(PARENT,legacy_from_parent(),m.project(DATA),parent_sha=before)
        self.assertEqual(sha256(PARENT),before)
    def test_bad_projected_admission(self):
        p=m.project(DATA);p['admission']='PASS'
        with self.assertRaises(ValueError):m.extend_graph(PARENT,legacy_from_parent(),p,parent_sha=sha256(PARENT))
    def test_html_query_and_escaping(self):
        p=m.project(DATA);p['rows'][0]['repository']='<img src=x onerror=alert(1)>'
        txt=m.render_html(p)
        self.assertNotIn('<img src=x onerror=alert(1)>',txt)
        self.assertIn('id="search"',txt)
        self.assertIn('id="filter"',txt)
        self.assertIn('function draw()',txt)
    def test_html_wrong_input_rejected(self):
        p=m.project(DATA);p['admission']='MERGE_ALLOWED'
        with self.assertRaises(ValueError):m.render_html(p)

if __name__=='__main__':unittest.main()