import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate_gm_i_a_coolprop_fast_heavy_keb.py"
SPEC = importlib.util.spec_from_file_location("gm_i_a_keb", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def provider_fixture():
    return {
        "schema": "qps.gm_i_a.fast_heavy.federation_attestation.v1",
        "mission": "GM-I-A",
        "lane": "L9_FEDERATION",
        "provider_repo": "GBOGEB/CoolProp",
        "source_head_sha": MOD.EXPECTED_SOURCE,
        "source_merge_sha": MOD.EXPECTED_MERGE,
        "workflow": {"run_id": MOD.EXPECTED_RUN, "conclusion": "success"},
        "heavy": {"conclusion": "success", "build_seconds": 2.0, "queue_seconds": 0.5},
        "fast": {
            "conclusion": "success",
            "calculations_passed": 3,
            "build_invoked": False,
            "source_checkout_performed": False,
            "execute_seconds": 0.2,
            "queue_seconds": 0.1,
        },
        "runtime_economics": {"fast_execution_is_independent_of_source_build": True},
        "authority": {
            "scope": "COMPATIBILITY_RUNTIME_ONLY",
            "authority_transfer": False,
            "engineering_promotion": "WITHHELD",
        },
    }


def test_bridge_and_emitted_receipt_remain_candidate_only():
    bridge = MOD.load_bridge()
    data = provider_fixture()
    MOD.validate_provider(data)
    receipt = MOD.build_receipt(data, "a" * 64, bridge)

    assert bridge["knowledge_atom"]["object_type"] == "KEB_KNOWLEDGE_ATOM_CANDIDATE"
    assert receipt["object_type"] == "KEB_KNOWLEDGE_ATOM_CANDIDATE"
    assert receipt["status"] == "PASS_VALIDATED_CANDIDATE"
    assert receipt["canonical_keb_atom"] is False
    assert receipt["promotion_evidence_present"] is False
    assert receipt["authority_transfer"] is False
    assert receipt["formal_credit_delta"] == 0
