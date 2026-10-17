"""Public-safe synthetic CODEX native tests for standalone continuity module.

No original user ZIP, private artifact or sensitive repo file is committed.
Synthetic fixtures never count as native BD/LLDB root evidence.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from mycelium_continuity.ingest import build_graph
from mycelium_continuity.graph import project_metrics,validate_graph
from mycelium_continuity.audit import audit_summary
from mycelium_continuity.journal import seal,verify,known_at,drift
from mycelium_continuity.render import mermaid_sipoc,dashboard
from mycelium_continuity.cli import build,verify as verify_bundle


ROLES=['S-OBSERVE','I-VALIDATE','P-CODE-MAROON','P-PY310','P-GOVERNANCE','P-WORKER-TELEMETRY','O-JOIN','C-ADMISSION']
SIPOC=[('S-OBSERVE','I-VALIDATE'),('I-VALIDATE','P-CODE-MAROON'),('I-VALIDATE','P-PY310'),('I-VALIDATE','P-GOVERNANCE'),('I-VALIDATE','P-WORKER-TELEMETRY'),('P-CODE-MAROON','O-JOIN'),('P-PY310','O-JOIN'),('P-GOVERNANCE','O-JOIN'),('P-WORKER-TELEMETRY','O-JOIN'),('O-JOIN','C-ADMISSION')]
REPOS=['GBOGEB/ABACUS','GBOGEB/CODEX','GBOGEB/cryoplant-project','GBOGEB/gg_MATH','GBOGEB/pipeline-automation-hub']
CONTRACTS=[('CODEX_UI_GOVERNANCE','GBOGEB/CODEX'),('CODEX_EXECUTION_GOVERNANCE','GBOGEB/CODEX'),('MISSIONCONTROL_GOLDEN_THREAD',REPOS[4]),('MISSIONCONTROL_SIPOC',REPOS[4]),('MISSIONCONTROL_BD',REPOS[4]),('ABACUS_BD_LDAB',REPOS[0])]


def fixture():
    original={'schema':'code-purple.mesh-projection.v1','admission':'HOLD','dispatch':'STAGED_NOT_LAUNCHED','source_snapshot_date':'2026-10-01','instances':[], 'edges':[], 'prs':[]}
    for i,id in enumerate(ROLES):
        role='S' if i==0 else 'I' if i==1 else 'P' if 2<=i<=5 else 'O' if i==6 else 'C'
        repo=REPOS[0] if i in (2,3,4) else REPOS[4]
        original['instances'].append({'id':id,'sipoc_role':role,'repo':repo,'source_sha':'a'*40,'incarnation':'synthetic-'+id,
                                      'mode':'OBSERVE','state':'READY','owner_issue':100+i,'root_id':None})
    original['edges']=[{'from':a,'to':b,'kind':'SIPOC_DEPENDENCY'} for a,b in SIPOC]
    original['prs']=[{'repo':REPOS[0],'pr':1000+i,'head_sha':'a'*40,'state':'open','url':'https://github.com/GBOGEB/ABACUS/pull/'+str(1000+i),'title':'synthetic history'} for i in range(22)]
    live={'schema':'code-purple.source-readback.v1','observed_on':'2026-10-17',
          'repositories':[{'repo':r,'branch':'master' if r==REPOS[4] else 'main','sha':'b'*40,'protected':False} for r in REPOS],
          'source_contracts':[{'authority':a,'repository':r,'path':'synthetic/'+a+'.yaml','role':a,'verified':'CONNECTOR_FILE_READBACK'} for a,r in CONTRACTS],
          'sources':['https://github.com/GBOGEB/pipeline-automation-hub/issues/358'],
          'authorization':{'dispatch_authorized':False,'merge_authorized':False,'accepted_causal_root_closures':None},
          'cpq_statuses':[{'id':f'CPQ-{i:03d}','state':('ACTIVE' if i in (3,5) else 'UNKNOWN_NEEDS_READER' if i in (16,18) else 'TODO' if i in (9,10,11,13,15) else 'DONE')} for i in range(1,19)],
          'pull_requests':[{'repo':REPOS[4],'number':number,'head_sha':'c'*40,'merge_commit_sha':'d'*40,
                            'merged_at':'2026-10-17T10:00:00Z','state':'merged','native_workflow_run_id':i+123,
                            'native_workflow_outcome':result,**({'native_artifact_id':999,
                            'native_artifact_sha256':'f'*64,'native_artifact_byte_verified':True} if number==596 else {})}
                           for i,(number,result) in enumerate(((594,'failure'),(596,'success')))]}
    return original,live


def local_graph(native_verified=False):
    a,b=fixture();return build_graph(a,b,verified_native_digest='f'*64 if native_verified else None)

class ContinuityPortableTests(unittest.TestCase):
    def test_synthetic_declared_denominators(self):
        a,b=fixture();g=build_graph(a,b);m=project_metrics(g,a)
        self.assertEqual(m['legacy_sipoc_retention']['numerator'],8)
        self.assertEqual(m['legacy_edge_retention']['numerator'],10)
        self.assertEqual(m['legacy_pr_retention']['numerator'],22)
        self.assertEqual(m['nodes'],85)
        self.assertEqual(m['edges'],115)
    def test_original_8_not_pruned(self):
        g=local_graph();self.assertEqual(len([x for x in g['nodes'] if x['id'].startswith('sipoc:N1:')]),8)
    def test_extra_wave_is_separate_and_acyclic(self):
        g=local_graph();m=validate_graph(g)
        self.assertEqual(len(m['waves']),5)
        self.assertEqual(len([x for x in g['nodes'] if x['id'].startswith('sipoc:N7:')]),8)
    def test_raw_native_bool_cannot_forge_proof(self):
        g=local_graph();self.assertFalse(any(e['binding']=='RECEIPT_BOUND' for e in g['edges']))
    def test_local_verifier_may_emit_receipt(self):
        g=local_graph(True);self.assertEqual(sum(e['binding']=='RECEIPT_BOUND' for e in g['edges']),3)
    def test_wrong_digest_degrades_to_observed(self):
        a,b=fixture();g=build_graph(a,b,verified_native_digest='0'*64)
        self.assertEqual(next(n for n in g['nodes'] if n['kind']=='ARTIFACT')['evidence'],'OBSERVED')
    def test_synthetic_no_accepted_roots(self):
        g=local_graph(True);self.assertFalse(any(e['binding']=='ACCEPTED' for e in g['edges']))
    def test_missing_repository_rejected(self):
        a,b=fixture();b['repositories'].pop()
        with self.assertRaisesRegex(ValueError,'five-repo'):build_graph(a,b)
    def test_missing_pr_history_rejected(self):
        a,b=fixture();a['prs'].pop()
        with self.assertRaisesRegex(ValueError,'22 PR'):build_graph(a,b)
    def test_unexpected_cpq_state_rejected(self):
        a,b=fixture();b['cpq_statuses'][0]['state']='MERGE'
        with self.assertRaisesRegex(ValueError,'lifecycle'):build_graph(a,b)
    def test_mutation_gate_rejected(self):
        a,b=fixture();b['authorization']['dispatch_authorized']=True
        with self.assertRaisesRegex(ValueError,'dispatch'):build_graph(a,b)
    def test_missing_provenance_rejected(self):
        g=local_graph();g['nodes'][0]['source']=''
        with self.assertRaisesRegex(ValueError,'missing source'):validate_graph(g)
    def test_sipoc_cycle_rejected(self):
        g=local_graph();e=copy.deepcopy(next(x for x in g['edges'] if x['kind']=='SIPOC_DEPENDENCY'))
        e.update({'from':'sipoc:N1:C-ADMISSION','to':'sipoc:N1:S-OBSERVE'});g['edges'].append(e)
        with self.assertRaisesRegex(ValueError,'cycle'):validate_graph(g)
    def test_global_reference_cycles_are_not_execution_cycles(self):
        self.assertTrue(validate_graph(local_graph()))
    def test_invalid_receipt_without_proof_rejected(self):
        g=local_graph();g['edges'][0]['binding']='RECEIPT_BOUND'
        with self.assertRaisesRegex(ValueError,'unproven'):validate_graph(g)
    def test_intent_has_value_effort_not_false_statistics(self):
        a=audit_summary();self.assertEqual(len(a['features']),20);self.assertFalse(a['scores_are_observed'])
    def test_prune_only_candidate_not_deleted(self):
        a=audit_summary();self.assertTrue(any(x['decision']=='PRUNE_CANDIDATE_ONLY' for x in a['features']))
    def test_bitemporal_knowledge_selection(self):
        def record(id,day):return dict(id=id,type='SOURCE_FROZEN',recorded_on=day,observed_on=day,evidence_class='HISTORICAL_INPUT',admission='HOLD',authoritative_mutation=False)
        j=seal([record('old','2026-10-01'),record('new','2026-10-17')]);self.assertTrue(verify(j))
        self.assertEqual(len(known_at(j,'2026-10-02')['selected_events']),1)
    def test_checksum_tamper_detected(self):
        a=dict(id='a',type='SOURCE_FROZEN',recorded_on='2026-10-01',evidence_class='HISTORICAL_INPUT',admission='HOLD',authoritative_mutation=False)
        j=seal([a]);j['events'][0]['subject']='tampered'
        with self.assertRaisesRegex(ValueError,'digest'):verify(j)
    def test_drift_suspends_green_reuse(self):
        a,b=fixture();before=copy.deepcopy(b);b['repositories'][0]['sha']='1'*40
        result=drift(before,b);self.assertEqual(result['changed_count'],1);self.assertFalse(result['automatic_prior_green_reuse'])
    def test_six_view_desktop_mobile_without_external_scripts(self):
        from mycelium_continuity.graph import sha256
        g=local_graph();a,b=fixture();m=project_metrics(g,a)
        src=dashboard(dict(graph=g,metrics=m,live=b,n1_sha256='a'*64,graph_sha256=sha256(g),cpq_open=9,native_artifact_sha256=None,release_id='SYNTHETIC'))
        self.assertEqual(src.count('class="panel"'),6)
        self.assertIn('REMOTE_METADATA_ONLY_NOT_BYTE_VERIFIED',src)
        self.assertIn('id="zoom"',src)
    def test_mermaid_preserves_new_and_old_nodes(self):
        txt=mermaid_sipoc(local_graph());self.assertIn('P-N7-TOPOLOGY',txt);self.assertIn('P-CODE-MAROON',txt)
    def test_portable_build_without_real_bytes_never_false_verified(self):
        a,b=fixture()
        with tempfile.TemporaryDirectory() as t:
            t=Path(t);z=t/'SYNTHETIC_NOT_ORIGINAL.zip'
            with zipfile.ZipFile(z,'w') as archive:
                archive.writestr('mesh.json',json.dumps(a))
                for name in ('GLOSSARY.md','NEXT_PULSE.md','QA_RECEIPT.json','index.html','screenshot_desktop.png'):
                    archive.writestr(name,'{}' if name=='QA_RECEIPT.json' else 'SYNTHETIC FIXTURE')
            inp=t/'synthetic_readback.json';inp.write_text(json.dumps(b))
            out=t/'output';result=build(z,inp,out)
            self.assertEqual(result['nodes'],85)
            self.assertTrue(verify_bundle(out)['legacy_retention'])
            self.assertIn('REMOTE_METADATA_ONLY_NOT_BYTE_REVERIFIED',(out/'docs/STATUS.md').read_text())
            self.assertNotIn('DOWNLOAD_CRC_SHA256_VERIFIED',(out/'docs/STATUS.md').read_text())

if __name__=='__main__':unittest.main()