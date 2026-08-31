from copy import deepcopy
from pathlib import Path
import unittest

import yaml

from scripts.validate_qps_artifact_product_lineage import validate_contract


CONTRACT = Path("federation/qps/QPS_ARTIFACT_PRODUCT_LINEAGE_CONTRACT_v0.1.yaml")


class ArtifactProductLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))

    def test_controlled_contract_is_valid(self):
        self.assertEqual(validate_contract(deepcopy(self.data)), [])

    def test_missing_docx_is_rejected(self):
        data = deepcopy(self.data)
        data["build_model"]["outputs"] = [x for x in data["build_model"]["outputs"] if x["artifact_type"] != "DOCX"]
        self.assertTrue(validate_contract(data))

    def test_peer_artifact_chain_is_rejected(self):
        data = deepcopy(self.data)
        data["build_model"]["outputs"][1]["parent"] = "Excel"
        self.assertTrue(validate_contract(data))

    def test_false_completion_is_rejected(self):
        data = deepcopy(self.data)
        data["completion_gate"]["completion_claim_allowed"] = True
        self.assertTrue(validate_contract(data))


if __name__ == "__main__":
    unittest.main()

