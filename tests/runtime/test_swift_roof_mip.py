"""Adversarial contract and source-scope checks for the Swift roof."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'swift_roof_mip.py'
spec = importlib.util.spec_from_file_location('swift_roof_mip', PATH)
roof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(roof)
SHA = 'a' * 40


def trace():
    return '''(lldb) target create /tmp/Probe
Current executable set to Probe
(lldb) breakpoint set --file Probe.swift --line 4
Breakpoint 1: where = Probe main
(lldb) run
Process 3976 stopped
* thread #1, stop reason = breakpoint 1.1
    frame #0: Probe main
(lldb) thread step-over
Process 3976 stopped
* thread #1, stop reason = step over
    frame #0: Probe main
(lldb) thread step-over
Process 3976 stopped
* thread #1, stop reason = step over
    frame #0: dyld start
(lldb) thread backtrace
* thread #1, stop reason = step over
  * frame #0: dyld start
'''


def receipt(log=None, sha=SHA):
    log = trace() if log is None else log
    r = {'repo': roof.CODEX, 'exact_head_sha': sha, 'probe_status': 'ACCEPT',
         'dov_status': 'PASS', 'probe': {'status': 'ACCEPT', 'steps': 2,
          'lldb': {'returncode': 0, 'stdout': log}},
         'minimum_victory_condition': {'real_probe_steps_gt_zero': True}}
    r['receipt_sha256'] = hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()
    return r


class NativeProof(unittest.TestCase):
    def test_exact_two_stops_not_three_from_backtrace(self):
        self.assertEqual(roof.native_stops(trace()), {'breakpoint_stops': 1,
            'step_stops': 2, 'backtrace_present': True})

    def test_native_receipt_true_qualified_only_as_lldb_cli(self):
        x = roof.verify_native(receipt(), SHA)
        self.assertEqual(x['native_cli_steps'], 2)
        self.assertEqual(x['native_cli_probe'], 'PASS')
        self.assertEqual(x['lldb_dap_live'], 'UNVERIFIED')
        self.assertEqual(x['mcp_native'], 'UNVERIFIED')
        self.assertEqual(x['docker_native'], 'UNVERIFIED')
        self.assertEqual(x['admission'], 'HOLD')

    def test_no_credit_even_when_probe_success(self):
        self.assertEqual(roof.verify_native(receipt(), SHA)['credit'], 0)

    def test_reject_only_echoed_step_commands(self):
        forged = '(lldb) run\nProcess 1 stopped\nstop reason = breakpoint 1.1\n(lldb) thread step-over\n(lldb) thread step-over\n(lldb) thread backtrace\nframe #0: fake'
        with self.assertRaisesRegex(ValueError, 'genuine LLDB'):
            roof.verify_native(receipt(forged), SHA)

    def test_reject_backtrace_only_stop_reason(self):
        forged = '(lldb) run\nProcess 1 stopped\nstop reason = breakpoint\n(lldb) thread step-over\n(lldb) thread step-over\n(lldb) thread backtrace\n* thread #1, stop reason = step over\nframe #0: demo'
        with self.assertRaisesRegex(ValueError, 'genuine LLDB'):
            roof.verify_native(receipt(forged), SHA)

    def test_reject_one_actual_step(self):
        x = trace().replace('(lldb) thread step-over\nProcess 3976 stopped\n* thread #1, stop reason = step over\n    frame #0: dyld start', '(lldb) thread step-over\nerror: failed')
        with self.assertRaisesRegex(ValueError, 'genuine LLDB'):
            roof.verify_native(receipt(x), SHA)

    def test_reject_stale_sha(self):
        with self.assertRaisesRegex(ValueError, 'stale'):
            roof.verify_native(receipt(), 'b' * 40)

    def test_reject_forged_hash(self):
        r = receipt(); r['probe']['status'] = 'PASS'
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            roof.verify_native(r, SHA)

    def test_reject_nonzero_lldb(self):
        r = receipt(); r['probe']['lldb']['returncode'] = 1
        r['receipt_sha256'] = hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='receipt_sha256'}, sort_keys=True).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'not clean'):
            roof.verify_native(r, SHA)

    def test_reject_fraudulent_inflated_step_counter(self):
        r = receipt(); r['probe']['steps'] = 10
        r['receipt_sha256'] = hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='receipt_sha256'}, sort_keys=True).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'inflated'):
            roof.verify_native(r, SHA)

    def test_reject_false_producer_status(self):
        r = receipt(); r['probe_status'] = 'DEFER'
        r['receipt_sha256'] = hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='receipt_sha256'}, sort_keys=True).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'not accepted'):
            roof.verify_native(r, SHA)


class CensusGraph(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for repo, path, _ in roof.ASSETS:
            if repo == roof.CODEX:
                p = self.root / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('public struct Foo {}\n')

    def test_census_four_local_one_remote(self):
        c = roof.source_census(self.root, SHA)
        self.assertEqual(c['registered_local'], 4)
        self.assertEqual(c['eligible_federated_declared'], 5)
        self.assertIsNone(c['federated_verified'])
        self.assertTrue(c['local_mapping_complete'])
        self.assertEqual(c['assets'][-1]['binding'], 'EXTERNAL_DECLARED_NOT_READBACK')

    def test_fresh_swift_path_cannot_disappear_from_denominator(self):
        p = self.root / 'new/More.swift'; p.parent.mkdir(); p.write_text('// test\n')
        c = roof.source_census(self.root, SHA)
        self.assertEqual(c['eligible_local'], 5)
        self.assertEqual(c['local_unregistered'], ['new/More.swift'])
        self.assertFalse(c['local_mapping_complete'])

    def test_missing_swift_detected(self):
        (self.root / roof.ASSETS[1][1]).unlink()
        c = roof.source_census(self.root, SHA)
        self.assertFalse(c['local_mapping_complete'])
        self.assertEqual(len(c['local_missing']), 1)

    def test_content_hash_changes_with_source(self):
        p = self.root / roof.ASSETS[0][1]
        before = roof.source_census(self.root, SHA)['assets'][0]['content_sha256']
        p.write_text('mutated\n')
        after = roof.source_census(self.root, SHA)['assets'][0]['content_sha256']
        self.assertNotEqual(before, after)

    def test_source_sha_invalid(self):
        with self.assertRaisesRegex(ValueError, 'invalid source sha'):
            roof.source_census(self.root, 'main')

    def test_forward_dag_topologically_ranked(self):
        g = roof.graph()
        ranks = {n['id']: n['rank'] for n in g['nodes']}
        self.assertTrue(all(ranks[e['from']] < ranks[e['to']] for e in g['edges']))
        self.assertEqual(len(g['next_pulse_edges']), 1)

    def test_mermaid_separate_next_pulse(self):
        s = roof.mermaid(roof.graph())
        self.assertIn('flowchart LR', s)
        self.assertIn('N+1 only', s)

    def test_sipoc_owner_chain_separate(self):
        s = roof.sipoc()
        self.assertEqual(len(s), 6)
        self.assertTrue(any('QPS' in x['supplier'] for x in s))
        self.assertTrue(any('ABACUS' in x['supplier'] for x in s))


if __name__ == '__main__':
    unittest.main()

class ProducerHeadContract(unittest.TestCase):
    """Test the real receipt producer against GitHub's reserved PR event SHA."""

    @classmethod
    def setUpClass(cls):
        from unittest import mock
        cls.mock = mock
        producer = PATH.with_name('lldb_dap_runtime_probe.py')
        spec = importlib.util.spec_from_file_location('lldb_dap_runtime_probe', producer)
        cls.producer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.producer)

    def test_exact_checkout_sha_wins_over_synthetic_pr_event_sha(self):
        p = self.producer
        with self.mock.patch.dict(p.os.environ, {'GITHUB_SHA': 'b'*40, 'EXACT_HEAD': SHA}):
            with self.mock.patch.object(p, 'run', return_value={'returncode':0,'stdout':SHA+'\\n'}):
                self.assertEqual(p.git_sha(), SHA)

    def test_mismatched_checkout_head_fails_closed(self):
        p = self.producer
        with self.mock.patch.dict(p.os.environ, {'GITHUB_SHA': SHA, 'EXACT_HEAD': 'b'*40}):
            with self.mock.patch.object(p, 'run', return_value={'returncode':0,'stdout':SHA+'\\n'}):
                with self.assertRaisesRegex(RuntimeError, 'expected PR head'):
                    p.git_sha()

    def test_checkout_failure_cannot_fallback_to_event_sha(self):
        p = self.producer
        with self.mock.patch.dict(p.os.environ, {'GITHUB_SHA': SHA, 'EXACT_HEAD': SHA}):
            with self.mock.patch.object(p, 'run', return_value={'returncode':128,'stdout':''}):
                with self.assertRaisesRegex(RuntimeError, 'source HEAD unavailable'):
                    p.git_sha()

    def test_malformed_head_never_promoted(self):
        p = self.producer
        with self.mock.patch.dict(p.os.environ, {'GITHUB_SHA':SHA,'EXACT_HEAD':SHA}):
            with self.mock.patch.object(p, 'run', return_value={'returncode':0,'stdout':'main\\n'}):
                with self.assertRaisesRegex(RuntimeError, 'source HEAD unavailable'):
                    p.git_sha()

    def test_receipt_separates_checked_source_and_event_sha(self):
        p=self.producer
        with tempfile.TemporaryDirectory() as tmp:
            with self.mock.patch.dict(p.os.environ, {'GITHUB_SHA':'b'*40,'EXACT_HEAD':SHA,
                                                     'GITHUB_REPOSITORY':roof.CODEX}):
                with self.mock.patch.object(p,'run',return_value={'returncode':0,'stdout':SHA+'\\n'}):
                    with self.mock.patch.object(p,'classify_surfaces',return_value={}):
                        r=p.emit_receipt(Path(tmp)/'native.json',{'status':'ACCEPT','steps':2})
            self.assertEqual(r['exact_head_sha'],SHA)
            self.assertEqual(r['github_event_sha'],'b'*40)
            self.assertEqual(r['source_sha_basis'],'GIT_CHECKOUT_HEAD')
            proof=dict(r);proof.pop('receipt_sha256')
            self.assertEqual(r['receipt_sha256'],
                hashlib.sha256(json.dumps(proof,sort_keys=True).encode()).hexdigest())
