import copy
import unittest

from scripts import validate_ssot_style_bridge as validator


class TestValidateSsotStyleBridge(unittest.TestCase):
    def setUp(self):
        self.manifest = validator.load_manifest(validator.DEFAULT_MANIFEST)

    def test_manifest_is_valid(self):
        self.assertEqual([], validator.validate_manifest(self.manifest))

    def test_pca_axes_must_stay_reversed_for_catchup(self):
        broken = copy.deepcopy(self.manifest)
        broken["pca_axes"] = list(reversed(broken["pca_axes"]))
        errors = validator.validate_manifest(broken)
        self.assertIn("pca_axes must be ordered P5 to P1", errors)

    def test_awake_score_counts_existing_probe_paths(self):
        score = validator.score_awake_probes(self.manifest)
        self.assertGreaterEqual(score["score"], 90.0)
        self.assertIn("ci", score["by_kind"])

    def test_penetration_score_separates_depth_from_presence(self):
        report = validator.score_penetration(self.manifest)
        self.assertGreaterEqual(report["score"], 80.0)
        self.assertIn("keb", report["by_kind"])
        self.assertLessEqual(report["by_kind"]["keb"]["depth"], report["by_kind"]["keb"]["total"])


if __name__ == "__main__":
    unittest.main()
