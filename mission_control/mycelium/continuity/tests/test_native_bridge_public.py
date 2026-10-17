"""Public safe no-external-artifact regression tests for N8 bridge contract."""
import hashlib, json, sys, tempfile, unittest, zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from mycelium_continuity.native_bridge import qualify_native, audit_compare

Q_SHA='a'*40;C_SHA='b'*40

def synthetic_zip(root, owner, mismatch=False, violated=False):
    p=Path(root)/(owner+'.zip')
    if owner=='qps':
        ses={'repo':'GBOGEB/cryoplant-project','exact_head_sha':Q_SHA,'session_id':'DBG-SYNTHETIC','qps_engineering_credit_delta':0}
        tele={'repo':ses['repo'],'exact_head_sha':Q_SHA,'session_id':'DBG-SYNTHETIC','compile_returncode':0,'debugger_returncode':0,'observed_steps':10,'status':'ACCEPT'}
        rec={'repo':ses['repo'],'exact_head_sha':Q_SHA,'session':ses,'telemetry':tele,'real_probe_steps':10,'authority_guards':{'qps_engineering_credit_delta':0},'dov_status':'PASS'}
        if violated:rec['real_probe_steps']=0
        contents={'debug_session.json':ses,'debugger_telemetry.json':tele,'qps_lldb_receipt.json':rec}
        obs={'repository':ses['repo'],'source_sha':Q_SHA,'run_id':111,'attempt':1,'job_id':222,'run_status':'completed','run_conclusion':'success','job_conclusion':'success','artifact_id':333}
    else:
        contents={'lldb_dap_live.json':{'status':'ACCEPT','dov_status':'PASS','source_exact_sha':('c'*40 if mismatch else C_SHA),'authority_guards':{'formal_engineering_credit_delta':0}},'lldb_mcp_live.json':{'status':'ACCEPT','dov_status':'PASS'}}
        obs={'repository':'GBOGEB/CODEX','source_sha':C_SHA,'run_id':444,'attempt':1,'job_id':555,'run_status':'completed','run_conclusion':'success','job_conclusion':'success','artifact_id':666}
    with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for k,v in contents.items():z.writestr(k,json.dumps(v))
    obs['artifact_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    return p,obs

class NativeBridgeSynthetic(unittest.TestCase):
    def test_two_domain_acceptances_remain_distinct(self):
        with tempfile.TemporaryDirectory() as td:
            q,qo=synthetic_zip(td,'qps');c,co=synthetic_zip(td,'codex')
            qa=qualify_native(q,qo);ca=qualify_native(c,co)
            self.assertEqual(qa['observed_steps'],10)
            self.assertEqual(ca['source_binding'],'EXACT_RUN_MATCH')
            self.assertIsNone(qa['owner_root_closure'])
            self.assertIsNone(audit_compare([qa,ca])['matched_effect'])
    def test_inner_sha_conflict_degrades_without_green_promotion(self):
        with tempfile.TemporaryDirectory() as td:
            c,co=synthetic_zip(td,'codex',mismatch=True)
            proof=qualify_native(c,co)
            self.assertEqual(proof['source_binding'],'INTERNAL_DAP_SOURCE_MISMATCH')
            self.assertIsNone(proof['join_to_abacus'])
    def test_native_member_denominator_cannot_be_forged(self):
        with tempfile.TemporaryDirectory() as td:
            q,qo=synthetic_zip(td,'qps',violated=True)
            with self.assertRaises(ValueError):qualify_native(q,qo)
    def test_native_checksum_rejects_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            q,qo=synthetic_zip(td,'qps');q.write_bytes(q.read_bytes()+b'mutation')
            with self.assertRaises(ValueError):qualify_native(q,qo)
    def test_skipped_job_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            q,qo=synthetic_zip(td,'qps');qo['job_conclusion']='skipped'
            with self.assertRaises(ValueError):qualify_native(q,qo)
    def test_unknown_source_owner_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            q,qo=synthetic_zip(td,'qps');qo['repository']='GBOGEB/not-owner'
            with self.assertRaises(ValueError):qualify_native(q,qo)
    def test_bad_run_attempt_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            q,qo=synthetic_zip(td,'qps');qo['attempt']=0
            with self.assertRaises(ValueError):qualify_native(q,qo)
    def test_no_zero_imputation_from_codex(self):
        with tempfile.TemporaryDirectory() as td:
            c,co=synthetic_zip(td,'codex');e=qualify_native(c,co)
            self.assertIsNone(e['observed_steps'])
            self.assertEqual(e['admission'],'HOLD')
            self.assertFalse(e['authority_transfer'])

    def test_additive_n8_projection_and_original_retention(self):
        from mycelium_continuity.native_bridge import extend
        from mycelium_continuity.graph import sha256
        with tempfile.TemporaryDirectory() as td:
            q,qo=synthetic_zip(td,'qps');c,co=synthetic_zip(td,'codex')
            qq=qualify_native(q,qo);cc=qualify_native(c,co)
            legacy={'instances':[{'id':'L'+str(i)} for i in range(8)],
                    'edges':[{'from':'L'+str(i),'to':'L'+str(i+1)} for i in range(7)]
                            +[{'from':'L'+str(i),'to':'L'+str(i+2)} for i in range(3)],
                    'prs':[{'repo':'GBOGEB/CODEX','pr':i} for i in range(1,23)]}
            mk=lambda id,kind,layer,owner='GBOGEB/CODEX':dict(id=id,title=id,kind=kind,layer=layer,owner=owner,source='SYNTHETIC',evidence='HISTORICAL')
            ns=[mk('repo:GBOGEB/CODEX','REPOSITORY','FEDERATION'),
                mk('repo:GBOGEB/cryoplant-project','REPOSITORY','FEDERATION','GBOGEB/cryoplant-project'),
                mk('contract:ABACUS_BD_LDAB','CONTRACT','FEDERATION'),
                mk('sipoc:N7:C-N7-HOLD','SIPOC_INSTANCE','SIPOC')]
            ns.extend(mk('sipoc:N1:L'+str(i),'SIPOC_INSTANCE','SIPOC') for i in range(8))
            for i in range(1,23):
                n=mk('pr:historical:GBOGEB/CODEX#'+str(i),'PR','TEMPORAL')
                n.update(repository='GBOGEB/CODEX',number=i,historical=True)
                ns.append(n)
            ed=[dict(from_='unused') for _ in ()]
            for edge in legacy['edges']:
                ed.append({'from':'sipoc:N1:'+edge['from'],'to':'sipoc:N1:'+edge['to'],
                           'kind':'SIPOC_DEPENDENCY','layer':'SIPOC','binding':'HISTORICAL','source_ref':'SYNTHETIC'})
            parent={'schema':'code-purple.mycelium.graph.v2','authority_transfer':False,
                    'dispatch_authorized':False,'admission':'HOLD','nodes':ns,'edges':ed}
            g,m=extend(parent,legacy,[qq,cc],n7_digest=sha256(parent))
            self.assertEqual(m['legacy_sipoc_retention'],{'numerator':8,'denominator':8})
            self.assertEqual(m['legacy_edge_retention'],{'numerator':10,'denominator':10})
            self.assertEqual(m['legacy_pr_retention'],{'numerator':22,'denominator':22})
            self.assertEqual(len(g['nodes'])-len(parent['nodes']),14)
            self.assertEqual(m['accepted_causal_root_closures'],None)
            with self.assertRaisesRegex(ValueError,'parent changed'):
                extend(parent,legacy,[qq,cc],n7_digest='0'*64)
            with self.assertRaisesRegex(ValueError,'two genuine'):
                extend(parent,legacy,[qq,qq],n7_digest=sha256(parent))
    def test_false_native_attempt_boolean_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            q,qo=synthetic_zip(td,'qps');qo['run_id']=True
            with self.assertRaises(ValueError):qualify_native(q,qo)
    def test_bad_repo_and_artifact_checks(self):
        with tempfile.TemporaryDirectory() as td:
            c,co=synthetic_zip(td,'codex')
            for k,v in [('artifact_id',0),('job_id',-1),('source_sha','BAD'),('attempt',0),('run_conclusion','failure')]:
                with self.subTest(k=k),self.assertRaises(ValueError):qualify_native(c,dict(co,**{k:v}))

if __name__=='__main__':unittest.main()