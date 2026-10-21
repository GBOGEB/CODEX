import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mycelium_continuity import terminal_reconciliation as m
from mycelium_continuity import admission_timeline as n9
from mycelium_continuity.graph import sha256,validate_graph
from test_admission_timeline_public import PARENT as N8_PARENT, legacy_from_parent

PARENT=json.loads((ROOT/'N9_ADMISSION_READBACK_20261017.json').read_text())
DATA=json.loads((ROOT/'N10_TERMINAL_RECONCILIATION_20261021.json').read_text())
# Synthetic N9 graph built from the synthetic N8 parent: test paths, not native evidence.
N9_GRAPH,_=n9.extend_graph(N8_PARENT,legacy_from_parent(),n9.project(PARENT),parent_sha=sha256(N8_PARENT))

def rejects(test,mutate,parent=None):
    z=copy.deepcopy(DATA);p=copy.deepcopy(parent or PARENT);mutate(z,p)
    with test.assertRaises(ValueError):m.validate(z,p)

class TerminalReconciliation(unittest.TestCase):
    def test_base_population(self):
        self.assertEqual(m.validate(DATA,PARENT),{'sources':2,'cases':4})
    def test_observed_transitions(self):
        p=m.project(DATA,PARENT);x=p['metrics']
        self.assertEqual(x['resolved_since_parent'],2)
        self.assertEqual(x['still_nonterminal'],0)
        self.assertEqual(x['terminal_stable'],2)
        self.assertEqual(x['terminal_rerun_changed'],0)
        self.assertEqual(x['failed_now'],3)
        self.assertEqual(x['success_now'],1)
        self.assertEqual(x['red_terminal_resolved_after_merge'],2)
        self.assertEqual(x['owner_heads_moved'],2)
        self.assertEqual(x['effective_required_status_proven'],0)
        self.assertIsNone(x['accepted_root_closures'])
        self.assertIsNone(x['merged_with_pre_merge_terminal_success_proven'])
        self.assertEqual(p['source']['parent_snapshot_sha256'],sha256(PARENT))
        self.assertTrue(all(r['admission']=='HOLD' and r['gate'].startswith('HOLD') for r in p['rows']))
    def test_resolved_rows_are_codex_failures(self):
        rows=[r for r in m.project(DATA,PARENT)['rows'] if r['transition']=='NONTERMINAL_RESOLVED_FAILED']
        self.assertEqual(sorted(r['pr'] for r in rows),[1061,1063])
        self.assertTrue(all(r['repository']=='GBOGEB/CODEX' and r['gate']=='HOLD_FAILED_EXACT_HEAD' for r in rows))
    def test_parent_not_mutated(self):
        before=sha256(PARENT);m.project(DATA,PARENT)
        self.assertEqual(sha256(PARENT),before)
    def test_required_status_cannot_promote(self):
        z=copy.deepcopy(DATA);z['owners'][0]['required_status_verified']=True
        p=m.project(z,PARENT)
        self.assertEqual(p['admission'],'HOLD');self.assertEqual(p['metrics']['effective_required_status_proven'],1)
    def test_still_nonterminal_and_other_resolutions(self):
        for status,conclusion,expected,gate in [('in_progress',None,'STILL_NONTERMINAL','HOLD_NONTERMINAL_EXACT_HEAD'),
                                                 ('completed','success','NONTERMINAL_RESOLVED_SUCCESS','HOLD_UNVERIFIED_REQUIRED_STATUS'),
                                                 ('completed','cancelled','NONTERMINAL_RESOLVED_OTHER','HOLD_NON_GREEN_EXACT_HEAD')]:
            z=copy.deepcopy(DATA);z['cases'][0].update(run_status=status,run_conclusion=conclusion)
            row=m.project(z,PARENT)['rows'][0]
            with self.subTest(status=status,conclusion=conclusion):
                self.assertEqual(row['transition'],expected);self.assertEqual(row['gate'],gate)
    def test_not_after_merge_timing(self):
        p=copy.deepcopy(PARENT);z=copy.deepcopy(DATA)
        p['cases'][0]['merged_at']='2026-10-17T12:00:00Z';z['parent']['snapshot_sha256']=sha256(p)
        self.assertEqual(m.project(z,p)['rows'][0]['last_update_relative_to_merge'],'NOT_AFTER_MERGE')
    def test_rerun_may_change_terminal(self):
        z=copy.deepcopy(DATA);z['cases'][2].update(run_attempt=2,run_conclusion='success',run_updated_at='2026-10-18T09:00:00Z')
        row=m.project(z,PARENT)['rows'][2]
        self.assertEqual(row['transition'],'TERMINAL_RERUN_CHANGED');self.assertEqual(row['admission'],'HOLD')
    def test_terminal_rewrite_without_rerun_rejected(self):
        rejects(self,lambda z,p:z['cases'][2].update(run_conclusion='success'))
    def test_rerun_without_new_update_rejected(self):
        rejects(self,lambda z,p:z['cases'][2].update(run_conclusion='success',run_attempt=2))
    def test_terminal_cannot_regress_without_rerun(self):
        rejects(self,lambda z,p:z['cases'][3].update(run_status='queued',run_conclusion=None))
    def test_parent_hash_drift_rejected(self):
        rejects(self,lambda z,p:p['cases'][0].update(run_status='completed',run_conclusion='failure'))
    def test_parent_binding_rejected(self):
        for key,value in [('epoch','N8'),('schema','other'),('snapshot_sha256','a'*64)]:
            with self.subTest(key=key):rejects(self,lambda z,p:z['parent'].update({key:value}))
        rejects(self,lambda z,p:z.update(parent=None))
    def test_invalid_parent_rejected(self):
        rejects(self,lambda z,p:p.update(authority_transfer=True))
    def test_schema_authority_and_provenance_rejected(self):
        for key,value in [('schema','wrong'),('observation_class','DIRECT_NATIVE_ROOT'),('authority_transfer',True),('merge_authorized',True),('security_waiver',True),('accepted_root_closures',0),('cases',[]),('owners',None)]:
            with self.subTest(key=key):rejects(self,lambda z,p:z.update({key:value}))
    def test_dropped_case_rejected(self):
        rejects(self,lambda z,p:z['cases'].pop())
    def test_added_case_rejected(self):
        def add(z,p):
            c=copy.deepcopy(z['cases'][0]);c['run_id']=1;z['cases'].append(c)
        rejects(self,add)
    def test_duplicate_case_rejected(self):
        rejects(self,lambda z,p:z['cases'].append(copy.deepcopy(z['cases'][0])))
    def test_case_identity_rejected(self):
        for key,value in [('pr',True),('run_id',0),('run_attempt',0),('run_attempt',True),('repository','GBOGEB/OTHER')]:
            with self.subTest(key=key,value=value):rejects(self,lambda z,p:z['cases'][0].update({key:value}))
        rejects(self,lambda z,p:z['cases'].__setitem__(0,'case'))
    def test_source_drift_rejected(self):
        for key in ('head_sha','run_head_sha'):
            with self.subTest(key=key):rejects(self,lambda z,p:z['cases'][0].update({key:'a'*40}))
    def test_bad_event_and_status_rejected(self):
        for change in [{'event':'push'},{'run_status':'running','run_conclusion':None},{'run_status':'queued','run_conclusion':'failure'},{'run_conclusion':None}]:
            with self.subTest(change=change):rejects(self,lambda z,p:z['cases'][0].update(change))
    def test_creation_time_rewrite_rejected(self):
        rejects(self,lambda z,p:z['cases'][0].update(run_created_at='2026-10-17T11:01:49Z'))
    def test_update_time_reversal_rejected(self):
        rejects(self,lambda z,p:z['cases'][0].update(run_updated_at='2026-10-17T11:00:00Z'))
    def test_update_after_observation_rejected(self):
        rejects(self,lambda z,p:z['cases'][0].update(run_updated_at='2026-10-22T00:00:00Z'))
    def test_observation_time_rejected(self):
        for stamp in ['2026-10-21',None,'2026-10-17T10:00:00Z']:
            with self.subTest(stamp=stamp):rejects(self,lambda z,p:z.update(observed_at=stamp))
    def test_owner_population_rejected(self):
        rejects(self,lambda z,p:z['owners'].pop())
        rejects(self,lambda z,p:z['owners'].append(copy.deepcopy(z['owners'][0])))
        rejects(self,lambda z,p:z['owners'][0].update(repository='GBOGEB/OTHER'))
    def test_owner_fields_rejected(self):
        for key,value in [('branch','master'),('sha','unbound'),('protected',None),('required_status_verified',None),('visible_ruleset_count',-1),('visible_ruleset_count',True),('protection_detail','NOT_RECHECKED_IN_N9')]:
            with self.subTest(key=key,value=value):rejects(self,lambda z,p:z['owners'][0].update({key:value}))
    def test_graph_lineage_and_retention(self):
        g,metrics=m.extend_graph(N9_GRAPH,legacy_from_parent(),m.project(DATA,PARENT),parent_sha=sha256(N9_GRAPH))
        ids={n['id'] for n in g['nodes']}
        self.assertIn('sipoc:N10:C-N10-HOLD',ids)
        self.assertTrue(any(e['from']=='sipoc:N9:C-N9-HOLD' and e['to']=='sipoc:N10:S-N10-PARENT' and e['kind']=='TEMPORAL_SUCCESSOR' for e in g['edges']))
        self.assertEqual(sum(n['id'].startswith('run-terminal:N10:') for n in g['nodes']),4)
        self.assertEqual(sum(e['kind']=='REVERSE_PRESSURE' and e['from'].startswith('run-terminal:N10:') for e in g['edges']),3)
        self.assertEqual(metrics['legacy_sipoc_retention'],{'numerator':8,'denominator':8})
        self.assertEqual(metrics['legacy_edge_retention'],{'numerator':10,'denominator':10})
        self.assertEqual(metrics['legacy_pr_retention'],{'numerator':22,'denominator':22})
        self.assertIsNone(metrics['accepted_causal_root_closures'])
        after,before=validate_graph(g),validate_graph(N9_GRAPH)
        self.assertEqual(after['sipoc_nodes']-before['sipoc_nodes'],6)
        self.assertEqual(after['sipoc_edges']-before['sipoc_edges'],6)
        self.assertIn(['sipoc:N10:C-N10-HOLD'],[[x for x in w if x.startswith('sipoc:N10:C')] for w in after['waves']])
        self.assertFalse(any(e['binding'] in {'RECEIPT_BOUND','ACCEPTED'} for e in g['edges'] if e['from'].startswith('run-terminal:N10:')))
    def test_graph_parent_unchanged(self):
        before=sha256(N9_GRAPH);m.extend_graph(N9_GRAPH,legacy_from_parent(),m.project(DATA,PARENT),parent_sha=before)
        self.assertEqual(sha256(N9_GRAPH),before)
    def test_graph_wrong_digest(self):
        with self.assertRaises(ValueError):m.extend_graph(N9_GRAPH,legacy_from_parent(),m.project(DATA,PARENT),parent_sha='a'*64)
    def test_graph_requires_n9_epoch(self):
        with self.assertRaises(ValueError):m.extend_graph(N8_PARENT,legacy_from_parent(),m.project(DATA,PARENT),parent_sha=sha256(N8_PARENT))
    def test_graph_requires_run_and_gate_lineage(self):
        for prefix in ('run-admission:','gate-admission:','atom:N9:CPQ-016'):
            g=copy.deepcopy(N9_GRAPH);drop={n['id'] for n in g['nodes'] if n['id'].startswith(prefix)}
            g['nodes']=[n for n in g['nodes'] if n['id'] not in drop];g['edges']=[e for e in g['edges'] if e['from'] not in drop and e['to'] not in drop]
            with self.subTest(prefix=prefix),self.assertRaises(ValueError):m.extend_graph(g,legacy_from_parent(),m.project(DATA,PARENT),parent_sha=sha256(g))
    def test_graph_duplicate_extension_fails(self):
        g,_=m.extend_graph(N9_GRAPH,legacy_from_parent(),m.project(DATA,PARENT),parent_sha=sha256(N9_GRAPH))
        with self.assertRaises(ValueError):m.extend_graph(g,legacy_from_parent(),m.project(DATA,PARENT),parent_sha=sha256(g))
    def test_graph_rejects_unqualified_projection(self):
        for key,value in [('admission','PASS'),('root_closures',1),('schema','other')]:
            p=m.project(DATA,PARENT);p[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):m.extend_graph(N9_GRAPH,legacy_from_parent(),p,parent_sha=sha256(N9_GRAPH))
    def test_graph_rejects_wrong_schema_and_legacy_loss(self):
        g=copy.deepcopy(N9_GRAPH);g['schema']='v1'
        with self.assertRaises(ValueError):m.extend_graph(g,legacy_from_parent(),m.project(DATA,PARENT),parent_sha=sha256(g))
        for key in ('instances','edges','prs'):
            legacy=legacy_from_parent();legacy[key]=legacy[key]+[{'id':'X','from':'X','to':'Y','repo':'GBOGEB/X','pr':999}]
            with self.subTest(key=key),self.assertRaises(ValueError):m.extend_graph(N9_GRAPH,legacy,m.project(DATA,PARENT),parent_sha=sha256(N9_GRAPH))

if __name__=='__main__':unittest.main()
