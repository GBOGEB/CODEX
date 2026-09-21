import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "federation/global_mesh/GLOOB_PANDOC_FEDERATION_CONTRACT_v1.json"
VALIDATOR = ROOT / "tools/validate_gloob_pandoc_federation.py"
SPEC = importlib.util.spec_from_file_location("gloob_validator", VALIDATOR)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def load():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_gloob_pandoc_federation_contract():
    assert MOD.validate(load())["formal_credit_delta"] == 0


def test_non_hex_producer_head_fails_closed():
    data = load()
    data["producer"]["head_sha"] = "x" * 40
    with pytest.raises(ValueError, match="producer head"):
        MOD.validate(data)


def test_non_hex_consumer_head_fails_closed():
    data = load()
    data["consumers"][0]["head_sha"] = "X" * 40
    with pytest.raises(ValueError, match="consumer head"):
        MOD.validate(data)


def test_removed_named_authority_guard_fails_closed():
    data = load()
    data["authority"]["must_not"] = data["authority"]["must_not"][:-1]
    with pytest.raises(ValueError, match="prohibition"):
        MOD.validate(data)


def test_changed_owner_set_fails_closed():
    data = load()
    data["authority"]["gloob_owns"] = ["semantic_depth"]
    with pytest.raises(ValueError, match="gloob ownership"):
        MOD.validate(data)


def test_non_object_consumer_entry_fails_closed():
    data = load()
    data["consumers"].append("malformed-consumer")
    with pytest.raises(ValueError, match="consumer entries"):
        MOD.validate(data)
