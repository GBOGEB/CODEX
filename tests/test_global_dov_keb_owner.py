"""Source-owned KEB Global DoV proof boundary; fixtures are never native."""
import json
import unittest
from pathlib import Path

FILE = (
    Path(__file__).resolve().parents[1]
    / "docs" / "ci" / "GLOBAL_DOV_KEB_OWNER_V1.json"
)


class KEBGlobalDoVControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FILE.read_text(encoding="utf-8"))

    def test_semantic_owner_not_orchestration(self):
        self.assertEqual("GBOGEB/CODEX", self.data["owner_repository"])
        self.assertEqual("OBSERVABILITY_ONLY",
                         self.data["orchestration_parent"]["scope"])

    def test_qps_remains_exclusive_acceptance_owner(self):
        self.assertEqual(
            "GBOGEB/cryoplant-project", self.data["acceptance_owner"]
        )
        self.assertFalse(self.data["evidence_gates"]["qps_owner_accepted"])

    def test_fixture_not_native(self):
        gates = self.data["evidence_gates"]
        self.assertEqual("SEMANTIC_CANDIDATE_ONLY", gates["fixture"])
        self.assertEqual("UNKNOWN", gates["native_peer_receipt"])
        self.assertFalse(gates["validated_provider_bytes"])
        self.assertFalse(gates["cross_repository_replay_verified"])
        self.assertEqual(0, gates["engineering_credit_delta"])

    def test_native_gate_has_executable_provenance(self):
        required = self.data["native_acceptance_requires"]
        self.assertTrue(any("exact_sha" in x for x in required))
        self.assertTrue(any("downloaded_provider_artifact" in x for x in required))
        self.assertTrue(any("run_and_job_attempt" in x for x in required))

    def test_cutover_does_not_delete_orphan_history(self):
        self.assertFalse(
            self.data["handover"]["purge_prior_to_native_cutover"]
        )


if __name__ == "__main__":
    unittest.main()
