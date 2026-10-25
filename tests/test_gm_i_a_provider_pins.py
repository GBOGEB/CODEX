"""Guard GM-I-A provider pins against crossing incompatible attestation epochs.

These checks compare the immutable provider pinned by the workflow to the
already-authorized P002 bridge and fail-closed semantic validator. They never
grant engineering authority or replace the checksum/semantic validation.
"""

import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/gm-i-a-coolprop-fast-heavy-keb.yml"
BRIDGE = ROOT / "triage/GM_I_A_COOLPROP_FAST_HEAVY_KEB_BRIDGE.yaml"
VALIDATOR = ROOT / "scripts/validate_gm_i_a_coolprop_fast_heavy_keb.py"


def inspect_pins(workflow, bridge, validator):
    job = workflow["jobs"]["consume-provider-attestation"]
    env = job["env"]
    provider = bridge["provider"]
    checks = {
        "provider commit": (env["PROVIDER_COMMIT"], provider["attestation_commit"]),
        "provider path": (env["PROVIDER_PATH"], provider["attestation_path"]),
        "provider SHA-256": (env["EXPECTED_SHA256"], provider["attestation_sha256"]),
        "validator SHA-256": (validator.EXPECTED_DIGEST, provider["attestation_sha256"]),
        "validator source": (validator.EXPECTED_SOURCE, provider["source_head_sha"]),
        "validator merge": (validator.EXPECTED_MERGE, provider["source_merge_sha"]),
        "validator run": (validator.EXPECTED_RUN, provider["runtime_run_id"]),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            raise ValueError(f"GM-I-A P002 {name} does not match authoritative bridge")
    if bridge["consumer"]["authority_transfer"] is not False:
        raise ValueError("GM-I-A must not transfer authority")


class TestImmutableGMIAProviderPins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        yaml = YAML(typ="safe")
        cls.workflow = yaml.load(WORKFLOW.read_text(encoding="utf-8"))
        cls.bridge = yaml.load(BRIDGE.read_text(encoding="utf-8"))
        spec = importlib.util.spec_from_file_location("gm_i_a_validator", VALIDATOR)
        cls.validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.validator)

    def test_live_workflow_agrees_with_p002_bridge_and_validator(self):
        inspect_pins(self.workflow, self.bridge, self.validator)

    def test_previous_provider_commit_is_rejected(self):
        tampered = deepcopy(self.workflow)
        tampered["jobs"]["consume-provider-attestation"]["env"]["PROVIDER_COMMIT"] = (
            "a71924147117c02ccc70c9b6436d89623897606c"
        )
        with self.assertRaisesRegex(ValueError, "provider commit"):
            inspect_pins(tampered, self.bridge, self.validator)

    def test_checksum_only_repin_is_rejected(self):
        tampered = deepcopy(self.workflow)
        tampered["jobs"]["consume-provider-attestation"]["env"]["EXPECTED_SHA256"] = (
            "132ff84a3502f5ce39d4698fa772e98f7e8fba8e52587e698e8ea419197e1398"
        )
        with self.assertRaisesRegex(ValueError, "provider SHA-256"):
            inspect_pins(tampered, self.bridge, self.validator)

    def test_authority_transfer_is_rejected(self):
        tampered = deepcopy(self.bridge)
        tampered["consumer"]["authority_transfer"] = True
        with self.assertRaisesRegex(ValueError, "must not transfer authority"):
            inspect_pins(self.workflow, tampered, self.validator)


if __name__ == "__main__":
    unittest.main()
