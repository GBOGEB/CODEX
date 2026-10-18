"""Fail-closed CODEX MYCELIUM stage consumer regression tests."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SRC=Path(__file__).resolve().parents[1]/"mission_control"/"mycelium"/"dependency_spine"/"stage_consumer.py"
spec=importlib.util.spec_from_file_location("stage_consumer",SRC)
assert spec and spec.loader
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
SHA="a"*40
C_SHA="b"*40

def fixture():
    r={"schema":"qps.dependency_spine.census/1.0",
       "repositories":{"GBOGEB/cryoplant-project":{"source_sha":SHA}},
       "governance":{"authority_transfer":False,"remote_dispatch_authorized":False,
                     "merge_admission":"HOLD","qps_child_disposition":"DEFER","engineering_credit_delta":0}}
    dig=module.checksum(module.pack(r))
    t={"schema":"qps.dependency_spine.stage_request/1.0","source_repo":"GBOGEB/cryoplant-project",
       "source_sha":SHA,"gateway":"CODEX_MYCELIUM_STAGE_ONLY","action_class":"STAGE_ONLY",
       "dispatch_authorized":False,"mutation_enabled":False,"review_approval_present":False,
       "merge_admission":"HOLD","formal_credit_delta":0,"qps_disposition":"DEFER",
       "receipt_sha256":dig}
    t["idempotency_key"]=module.checksum(module.pack(t))
    m={"schema":"qps.dependency_spine.sha256/1.0","source_shas":{"GBOGEB/cryoplant-project":SHA},
       "files":{"QPS_DEPENDENCY_SPINE_RECEIPT.json":dig}}
    return t,r,m

class ConsumerTests(unittest.TestCase):
    def test_no_source_is_defer(self):
        v=module.stage(None,None,C_SHA)
        module.verify(v)
        self.assertIsNone(v["source_head_sha"])
        self.assertEqual(v["stage_status"],"DEFER_SOURCE_ARTIFACT_NOT_STAGED")
    def test_synthetic_producer_contract_accepts_stage_only(self):
        t,r,m=fixture()
        self.assertEqual(module.validate_producer(t,r,m,SHA),module.checksum(module.pack(r)))
    def test_wrong_qps_head_rejected(self):
        t,r,m=fixture()
        with self.assertRaisesRegex(ValueError,"SOURCE_IDENTITY"):
            module.validate_producer(t,r,m,"c"*40)
    def test_bad_receipt_digest_rejected(self):
        t,r,m=fixture();r["governance"]["authority_transfer"]=True
        with self.assertRaisesRegex(ValueError,"SOURCE_CENSUS_DIGEST"):
            module.validate_producer(t,r,m,SHA)
    def test_forged_dispatch_rejected(self):
        t,r,m=fixture();t["dispatch_authorized"]=True
        t["idempotency_key"]=module.checksum(module.pack({k:v for k,v in t.items() if k!="idempotency_key"}))
        with self.assertRaisesRegex(ValueError,"PRODUCER_AUTHORITY_ESCALATION"):
            module.validate_producer(t,r,m,SHA)
    def test_bad_key_rejected(self):
        t,r,m=fixture();t["idempotency_key"]="0"*64
        with self.assertRaisesRegex(ValueError,"BAD_IDEMPOTENCY_KEY"):
            module.validate_producer(t,r,m,SHA)
    def test_missing_input_fails(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"SOURCE_ARTIFACT_UNAVAILABLE"):
                module.stage(Path(td),SHA,C_SHA)
    def test_realistic_source_bytes_staged_but_no_credit(self):
        t,r,m=fixture()
        with tempfile.TemporaryDirectory() as td:
            d=Path(td)
            for k,v in [("TASK",t),("RECEIPT",r),("SHA256",m)]:
                (d/f"QPS_DEPENDENCY_SPINE_{k}.json").write_bytes(module.pack(v))
            out=module.stage(d,SHA,C_SHA)
            module.verify(out)
            self.assertIsNotNone(out["source_receipt_sha256"])
            self.assertEqual(out["stage_status"],"STAGE_ONLY_VALIDATED_NO_AUTHENTICATED_CONSUMER_PROOF")
            self.assertFalse(out["authenticated_remote_execution"])
    def test_result_rehash_does_not_enable_merge(self):
        result=module.stage(None,None,C_SHA)
        result["merge_admission"]="PASS"
        result["stage_digest_sha256"]=module.checksum(module.pack({k:v for k,v in result.items() if k!="stage_digest_sha256"}))
        with self.assertRaisesRegex(ValueError,"CODEX_PROMOTION_FORBIDDEN"):
            module.verify(result)
    def test_result_tamper_detected(self):
        result=module.stage(None,None,C_SHA);result["source_head_sha"]="c"*40
        with self.assertRaisesRegex(ValueError,"RESULT_DIGEST_MISMATCH"):
            module.verify(result)
    def test_absent_source_sha_required(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"EXPECTED_SOURCE_SHA_REQUIRED"):
                module.stage(Path(td),None,C_SHA)
    def test_bad_consumer_sha_fails(self):
        with self.assertRaisesRegex(ValueError,"CONSUMER_HEAD_INVALID"):
            module.stage(None,None,"notsha")
