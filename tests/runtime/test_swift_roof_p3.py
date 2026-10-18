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
