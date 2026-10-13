"""Regression guards for source-bound disjoint census percentages."""
import unittest
from verify_disjoint_census import verify

SHA = "a" * 40


def row(n=3, d=4, kind="statement"):
    item = {"status": "MEASURED", "numerator": n, "denominator": d, "source_sha": SHA, "run_id": 123}
    if kind in ("pipeline_outputs", "ldab_live_sessions", "dov"):
        item["receipt_sha256"] = "b" * 64
    return item


class CensusTests(unittest.TestCase):
    def base(self, pops=None):
        return {"repository": "GBOGEB/CODEX", "head_sha": SHA, "populations": pops or {}}

    def test_missing_is_unknown(self):
        result = verify(self.base())
        self.assertTrue(result["valid"])
        self.assertIsNone(result["populations"]["statement"]["percent"])

    def test_measured_coverage(self):
        self.assertEqual(verify(self.base({"statement": row()}))["populations"]["statement"]["percent"], 75)

    def test_denominator_zero_rejected(self):
        self.assertFalse(verify(self.base({"branch": row(0, 0)}))["valid"])

    def test_invalid_oversized_numerator(self):
        self.assertFalse(verify(self.base({"diff": row(5, 4)}))["valid"])

    def test_wrong_sha(self):
        item = row()
        item["source_sha"] = "c" * 40
        self.assertFalse(verify(self.base({"statement": item}))["valid"])

    def test_bool_is_not_integer(self):
        self.assertFalse(verify(self.base({"statement": row(True, 4)}))["valid"])

    def test_receipt_required(self):
        item = row(kind="pipeline_outputs")
        item.pop("receipt_sha256")
        self.assertFalse(verify(self.base({"pipeline_outputs": item}))["valid"])

    def test_verified_pipeline(self):
        self.assertTrue(verify(self.base({"pipeline_outputs": row(kind="pipeline_outputs")}))["valid"])

    def test_withheld_nonzero_rejected(self):
        self.assertFalse(verify(self.base({"ruff_files": {"status": "WITHHELD", "numerator": 0, "denominator": 7}}))["valid"])

    def test_boolean_run_id_rejected(self):
        item = row()
        item["run_id"] = True
        self.assertFalse(verify(self.base({"statement": item}))["valid"])

    def test_malformed_receipt_digest_rejected(self):
        item = row(kind="ldab_live_sessions")
        item["receipt_sha256"] = "not-a-digest"
        self.assertFalse(verify(self.base({"ldab_live_sessions": item}))["valid"])

    def test_wrong_length_receipt_digest_rejected(self):
        item = row(kind="dov")
        item["receipt_sha256"] = "b" * 63
        self.assertFalse(verify(self.base({"dov": item}))["valid"])

    def test_all_population_keys(self):
        self.assertEqual(len(verify(self.base())["populations"]), 9)


if __name__ == "__main__":
    unittest.main()
