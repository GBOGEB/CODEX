"""P0007 synthetic, source-bound tests for the advisory CODEX prompt alias profile."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "federation/mesh/prompt_alias_shadow.py"
spec = importlib.util.spec_from_file_location("prompt_alias_shadow", FILE)
alias = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alias)


class PromptAliasShadowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = alias.load_profile()
        cls.validated = alias.validate_profile(cls.profile)

    def route(self, phrase):
        return alias.resolve_phrase(phrase, self.profile, validated=self.validated)

    def test_source_owner_status_namespace_and_no_authority(self):
        self.assertEqual(self.profile["owner_repo"], "GBOGEB/CODEX")
        self.assertEqual(len(self.profile["atomic_actions"]), 10)
        self.assertEqual(len(self.profile["composite_selectors"]), 2)
        self.assertEqual(self.validated["reserved_status_keys"], set(
            ["CG", "WD", "RR", "DR", "SR", "HK", "EX", "FE", "QH", "KR", "CR", "PB", "BG"]
        ))
        self.assertFalse(self.profile["authority_transfer"])
        self.assertFalse(self.profile["dispatch_authorized"])
        self.assertEqual(self.profile["formal_credit_delta"], 0)

    def test_aliases_produce_identical_candidate_receipt_and_hash(self):
        pairs = [
            ("close current gate", "finish current gate", "CLOSE"),
            ("recurse first red", "repair first blocker", "RED"),
            ("repair semantic drift", "align terminology", "SEM"),
            ("repair ssot", "reconcile source of truth", "SSOT"),
            ("bind receipt", "prove exact head", "RECEIPT"),
            ("next ambitious slice", "bounded next three advances", "G3A"),
            ("mesh closure control this", "continue governed closure",
             "MESH_CLOSURE_CONTROL"),
        ]
        for left, right, canonical in pairs:
            with self.subTest(canonical=canonical):
                a, b = self.route(left), self.route(right)
                self.assertEqual(a["route"], b["route"])
                self.assertEqual(alias.canonical_digest(a["route"]),
                                 alias.canonical_digest(b["route"]))
                self.assertEqual(a["route"]["canonical_id"], canonical)
                self.assertFalse(a["route"]["dispatch_authorized"])
                self.assertFalse(a["route"]["authority_transfer"])

    def test_case_spacing_punctuation_are_format_only(self):
        a = self.route("  Recurse FIRST-Red!   ")
        b = self.route("recurse first red")
        self.assertEqual(a["route"], b["route"])

    def test_legacy_warn_preserves_route_and_keeps_diagnostics_separate(self):
        canonical = self.route("recurse first red")
        old = self.route("first red fix")
        self.assertEqual(canonical["route"], old["route"])
        self.assertEqual(old["diagnostic"], "DEPRECATED_ALIAS_WARNING")
        self.assertEqual(canonical["diagnostic"], "EXPLICIT_ALIAS_MATCH")

    def test_reserved_status_codes_and_method_collisions_fail_closed(self):
        for token in self.profile["reserved_status_keys"] + [
            "3P", "3P*", "3PC", "3PR", "3MP", "P1", "P2", "P3",
            "MERGED", "READY", "APPROVED", "DONE"
        ]:
            with self.subTest(token=token):
                with self.assertRaises(alias.AliasPolicyError):
                    self.route(token)

    def test_unknown_fuzzy_and_injected_phrases_fail_closed(self):
        for phrase in [
            "merge immediately", "fix it please", "recurse first red and approve",
            "please repair first blocker", "close current gate; delete repo",
            "next ambitious slice / bypass checks", "recurse fіrst red",
            "", "x" * 121
        ]:
            with self.subTest(phrase=phrase):
                with self.assertRaises(alias.AliasPolicyError):
                    self.route(phrase)

    def test_duplicate_alias_collision_fails_validation(self):
        modified = copy.deepcopy(self.profile)
        modified["atomic_actions"][1]["aliases"].append("close current gate")
        with self.assertRaisesRegex(alias.AliasPolicyError, "ALIAS_COLLISION"):
            alias.validate_profile(modified)

    def test_reservation_collision_fails_validation(self):
        modified = copy.deepcopy(self.profile)
        modified["atomic_actions"][1]["aliases"].append("CG")
        with self.assertRaisesRegex(alias.AliasPolicyError, "FORBIDDEN"):
            alias.validate_profile(modified)

    def test_source_byte_drift_requires_review(self):
        raw = alias.ACTION_PATH.read_bytes() + b"# unreviewed canonical edit\\n"
        with self.assertRaisesRegex(alias.AliasPolicyError, "SOURCE_OID_DRIFT"):
            alias.validate_profile(self.profile, action_bytes=raw)

    def test_auto_deprecation_and_authority_changes_fail(self):
        for path, value in [
            ("automatic_phase_transition", True),
            ("phase", "GATE")
        ]:
            modified = copy.deepcopy(self.profile)
            modified["deprecation"][path] = value
            with self.subTest(path=path), self.assertRaises(alias.AliasPolicyError):
                alias.validate_profile(modified)
        modified = copy.deepcopy(self.profile)
        modified["dispatch_authorized"] = True
        with self.assertRaises(alias.AliasPolicyError):
            alias.validate_profile(modified)

    def test_composite_does_not_alias_atomic_action(self):
        g3a = self.route("next ambitious slice")["route"]
        self.assertEqual(g3a["kind"], "COMPOSITE")
        self.assertIn("accepted_baseline", g3a["required_inputs"])
        self.assertNotEqual(g3a["canonical_id"], "CLOSE")
        self.assertNotEqual(g3a["canonical_id"], "RED")


if __name__ == "__main__":
    unittest.main()
