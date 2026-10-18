"""Adversarial tests for immutable historical vs source-bound P3 owner-readback."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / 'scripts'
import sys
sys.path.insert(0, str(SRC))
spec = importlib.util.spec_from_file_location('swift_roof_p3', SRC/'swift_roof_p3.py')
p3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p3)
HISTORY = json.loads((Path(__file__).resolve().parents[2] / 'runtime' / 'debug' / 'swift_roof' / 'historical-owner-crosswalk.json').read_text())
SHA = 'b' * 40


class OwnerHistory(unittest.TestCase):
    def test_historical_crosswalk_bound_not_reaccepted(self):
        h = p3.owner_history(HISTORY)
        self.assertEqual(h['status'], 'HISTORICAL_DOCUMENT_CROSSWALK_ONLY')
        self.assertFalse(h['strict_steps_comparable'])
        self.assertEqual(h['owner_documents_matched'], 2)

    def test_reject_wrong_owner_sha(self):
        h = copy.deepcopy(HISTORY); h['qps']['source_sha'] = SHA
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            p3.owner_history(h)

    def test_reject_wrong_receipt_digest(self):
        h = copy.deepcopy(HISTORY); h['abacus']['receipt_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            p3.owner_history(h)

    def test_reject_wrong_owner_identity(self):
        h = copy.deepcopy(HISTORY); h['abacus']['repo'] = p3.QPS
        with self.assertRaisesRegex(ValueError, 'owner roles'):
            p3.owner_history(h)

    def test_reject_historical_defer_as_accept(self):
        h = copy.deepcopy(HISTORY); h['qps']['disposition'] = 'DEFER'
        with self.assertRaisesRegex(ValueError, 'disposition'):
            p3.owner_history(h)


class WaveBurndown(unittest.TestCase):
    def test_w2_zero_credit_and_noncomparable(self):
        out = p3.produce(HISTORY, sha=SHA, p1='success', p2='success', run_id=111)
        self.assertEqual(out['merge_admission'], 'HOLD')
        self.assertEqual(out['root_closure_credit'], 0)
        self.assertEqual(out['qps_engineering_credit_delta'], 0)
        self.assertEqual(out['comparison_class'], 'NONCOMPARABLE_METHOD_AND_HEAD_CHANGE')
        self.assertEqual(out['pulses'][2]['pass_fraction'], {'numerator': 2, 'denominator': 2})
        self.assertEqual(out['current_owner_chain']['status'], 'DEFER_NO_CURRENT_PRODUCER_RECEIPT')

    def test_n_is_one_failed_one_skipped_not_two_failures(self):
        n = p3.produce(HISTORY, sha=SHA, p1='unknown', p2='unknown')['pulses'][1]
        self.assertEqual(n['states'], {'P1': 'FAILURE', 'P2': 'SKIPPED'})
        self.assertEqual(n['pass_fraction']['numerator'], 0)
        self.assertEqual(n['pass_fraction']['denominator'], 2)

    def test_queued_is_null_not_zero(self):
        row = p3.pulse_row('N+1', p1='success', p2='unknown', sha=SHA, cohort='W2')
        self.assertIsNone(row['pass_fraction'])
        self.assertEqual(row['terminal_jobs'], 1)

    def test_reject_unknown_good_state(self):
        with self.assertRaisesRegex(ValueError, 'unrecognized'):
            p3.pulse_row('N+1', p1='passed', p2='success', sha=SHA, cohort='W2')

    def test_reject_producer_claim_with_nonterminal_job(self):
        with self.assertRaisesRegex(ValueError, 'native success'):
            p3.produce(HISTORY, sha=SHA, p1='failure', p2='success', native={})

    def test_no_owner_acceptance_by_default(self):
        x = p3.current_join(None, sha=SHA)
        self.assertEqual(x['owner_decision'], 'WITHHELD')
        self.assertEqual(x['matched_owners'], 0)

    def test_reject_bad_current_sha(self):
        with self.assertRaisesRegex(ValueError, 'current exact head'):
            p3.produce(HISTORY, sha='main', p1='success', p2='success')


class NativeWorkflowContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (Path(__file__).resolve().parents[2] / '.github' / 'workflows' / 'swift-roof-mip-testflight.yml').read_text()

    def test_every_checkout_pins_pr_source_not_merge(self):
        self.assertEqual(self.raw.count('ref: ${{ github.event.pull_request.head.sha || github.sha }}'), 3)
        self.assertEqual(self.raw.count('persist-credentials: false'), 3)

    def test_synthetic_pr_merge_never_qualifies_exact_head(self):
        self.assertIn('assert current==expected', self.raw)
        self.assertIn('ATTEMPT_NOT_PROOF', self.raw)

    def test_federated_observer_runs_after_failed_p1(self):
        self.assertIn('needs: [census-contract, native-macos]', self.raw)
        self.assertIn('if: always()', self.raw)
        self.assertIn('P1_STATUS: ${{ needs.census-contract.result }}', self.raw)

    def test_no_privileged_fork_or_secrets(self):
        self.assertNotIn('pull_request_target:', self.raw)
        self.assertNotIn('secrets.', self.raw)
        self.assertIn('contents: read', self.raw)

    def test_all_three_native_evidence_artifacts_published(self):
        for n in ('swift-roof-p1-', 'swift-roof-p2-', 'swift-roof-p3-'):
            self.assertIn(n, self.raw)

class CliReceiptFlight(unittest.TestCase):
    def setUp(self):
        from unittest import mock
        self.mock = mock
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'
        self.repo.mkdir()
        from swift_roof_mip import ASSETS, CODEX
        for owner, path, _ in ASSETS:
            if owner != CODEX:
                continue
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('public struct Proven {}\\n')
        import subprocess
        subprocess.run(['git','init','-q'], cwd=self.repo, check=True)
        subprocess.run(['git','add','.'],cwd=self.repo,check=True)
        subprocess.run(['git','-c','user.name=Test','-c','user.email=test@example.org','commit','-qm','seed'],cwd=self.repo,check=True)
        self.sha = subprocess.check_output(['git','rev-parse','HEAD'],cwd=self.repo,text=True).strip()
        self.out = Path(self.tmp.name) / 'out'
        self.history = Path(self.tmp.name) / 'history.json'
        self.history.write_text(json.dumps(HISTORY))

    def test_native_census_cli_builds_hash_manifest(self):
        from swift_roof_mip import main as roof_main
        args = ['roof','--root',str(self.repo),'--mode','census','--expected-head',self.sha,'--out',str(self.out)]
        with self.mock.patch('sys.argv',args):
            self.assertEqual(roof_main(),0)
        manifest=json.loads((self.out/'manifest.json').read_text())
        self.assertEqual(manifest['source_sha'],self.sha)
        self.assertEqual(manifest['admission'],'HOLD')
        self.assertEqual(len(manifest['sha256']),3)
        d=json.loads((self.out/'swift-roof.json').read_text())
        self.assertEqual(d['source']['registered_local'],4)
        self.assertIsNone(d['source']['federated_verified'])
        self.assertIsNone(d['native'])

    def test_native_cli_fails_on_missing_source(self):
        from swift_roof_mip import main as roof_main
        (self.repo/'runtime/debug/lldb_dap_probe/Probe.swift').unlink()
        args=['roof','--root',str(self.repo),'--mode','census','--expected-head',self.sha,'--out',str(self.out)]
        with self.mock.patch('sys.argv',args), self.assertRaisesRegex(ValueError,'missing local Swift'):
            roof_main()

    def test_verify_cli_fails_without_receipt(self):
        from swift_roof_mip import main as roof_main
        args=['roof','--root',str(self.repo),'--mode','verify','--expected-head',self.sha,'--out',str(self.out)]
        with self.mock.patch('sys.argv',args), self.assertRaisesRegex(ValueError,'native receipt missing'):
            roof_main()

    def test_p3_main_writes_hashed_burndown_and_null(self):
        args=['p3','--root',str(self.repo),'--expected-head',self.sha,'--history',str(self.history),
              '--p1','success','--p2','unknown','--out',str(self.out)]
        with self.mock.patch('sys.argv',args), self.mock.patch.dict('os.environ',{'GITHUB_RUN_ID':'1001','GITHUB_RUN_ATTEMPT':'2'}):
            self.assertEqual(p3.main(),0)
        from hashlib import sha256
        raw=(self.out/'p3-wave-observation.json').read_bytes()
        m=json.loads((self.out/'sha256-manifest.json').read_text())
        self.assertEqual(m['p3_observation_sha256'],sha256(raw).hexdigest())
        self.assertEqual(m['gate'],'HOLD')
        d=json.loads(raw)
        self.assertEqual(d['run_id'],1001)
        self.assertEqual(d['run_attempt'],'2')
        self.assertIsNone(d['pulses'][2]['pass_fraction'])
        self.assertEqual(d['pulses'][2]['terminal_jobs'],1)

    def test_p3_main_source_mismatch_rejected(self):
        args=['p3','--root',str(self.repo),'--expected-head','f'*40,'--history',str(self.history),
              '--p1','success','--p2','success','--out',str(self.out)]
        with self.mock.patch('sys.argv',args), self.assertRaisesRegex(ValueError,'checked-out head differs'):
            p3.main()

    def test_p3_main_bad_history_rejected(self):
        self.history.write_text('{}')
        args=['p3','--root',str(self.repo),'--expected-head',self.sha,'--history',str(self.history),
              '--p1','success','--p2','success','--out',str(self.out)]
        with self.mock.patch('sys.argv',args), self.assertRaisesRegex(ValueError,'history schema'):
            p3.main()

    def test_p3_inconsistent_status_fails_before_artifacts(self):
        args=['p3','--root',str(self.repo),'--expected-head',self.sha,'--history',str(self.history),
              '--p1','success','--p2','GREEN','--out',str(self.out)]
        with self.mock.patch('sys.argv',args), self.assertRaisesRegex(ValueError,'unrecognized native'):
            p3.main()
        self.assertFalse(self.out.exists())


class OwnerCurrentLiveContracts(unittest.TestCase):
    def setUp(self):
        from test_swift_roof_mip import receipt
        self.sha = 'a'*40
        self.receipt = receipt()
        self.abacus = {'consumer_repo':p3.ABACUS, 'producer_repo':p3.CODEX,
                       'producer_exact_head_sha':self.sha,
                       'producer_receipt_sha256':self.receipt['receipt_sha256'],
                       'current_disposition':'ACCEPT'}
        self.qps = {'child_repo':p3.QPS, 'producer_repo':p3.CODEX,
                    'producer_exact_head_sha':self.sha,
                    'producer_receipt_sha256':self.receipt['receipt_sha256'],
                    'current_child_disposition':'ACCEPT'}

    def test_native_without_owner_is_defer(self):
        d=p3.current_join(self.receipt,sha=self.sha)
        self.assertEqual(d['status'],'DEFER_OWNER_RECEIPTS_PENDING')
        self.assertEqual(d['code_x_real_steps'],2)
        self.assertEqual(d['owner_decision'],'WITHHELD')

    def test_one_owner_insufficient(self):
        d=p3.current_join(self.receipt,sha=self.sha,abacus=self.abacus)
        self.assertEqual(d['matched_owners'],1)
        self.assertEqual(d['status'],'DEFER_OWNER_RECEIPTS_PENDING')

    def test_both_matching_owners_do_not_grant_qps_credit(self):
        d=p3.current_join(self.receipt,sha=self.sha,abacus=self.abacus,qps=self.qps)
        self.assertEqual(d['status'],'CURRENT_OWNER_DOCUMENTS_BOUND')
        self.assertEqual(d['matched_owners'],2)
        self.assertEqual(d['owner_decision'],'REFER_TO_QPS_OWNER')
        self.assertEqual(d['qps_engineering_credit'],0)

    def test_qps_new_head_with_stale_receipt_rejected(self):
        q=copy.deepcopy(self.qps);q['producer_receipt_sha256']='e'*64
        with self.assertRaisesRegex(ValueError,'current owner exact-source'):
            p3.current_join(self.receipt,sha=self.sha,abacus=self.abacus,qps=q)

    def test_qps_defer_cannot_promote(self):
        q=copy.deepcopy(self.qps);q['current_child_disposition']='DEFER'
        with self.assertRaisesRegex(ValueError,'current owner does not accept'):
            p3.current_join(self.receipt,sha=self.sha,abacus=self.abacus,qps=q)

    def test_false_abacus_owner_rejected(self):
        a=copy.deepcopy(self.abacus);a['consumer_repo']=p3.QPS
        with self.assertRaisesRegex(ValueError,'owner wrong repository'):
            p3.current_join(self.receipt,sha=self.sha,abacus=a,qps=self.qps)
