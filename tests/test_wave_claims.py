"""Contract tests: wave naming ruleset, per-repo claims, federation roll-up and dedup."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts import build_wave_register, wave_claims

ROOT = Path(__file__).resolve().parents[1]
S = "gbogeb.wave_claims/1"


@pytest.fixture(scope="module")
def rules():
    return wave_claims.load_naming_rules()


def doc(repo, owns, participates=()):
    return {"schema": S, "repo": repo, "owns": list(owns), "participates": list(participates)}


def codes(found):
    return sorted(f["code"] for f in found)


def test_codex_own_claims_obey_the_ruleset(rules):
    claims = yaml.safe_load((ROOT / wave_claims.CLAIMS_PATH).read_text(encoding="utf-8"))
    assert claims["repo"] == "GBOGEB/CODEX"
    assert wave_claims.validate_claims(claims, rules, "GBOGEB/CODEX") == []


@pytest.mark.parametrize("claim,code", [
    ({"key": "QPS:W364", "name": "w364_lower", "status": "ACTIVE"}, "C2_NAME"),
    ({"key": "QPS:W364", "name": "W365_OTHER_NUMBER", "status": "ACTIVE"}, "C3_NAME_NUMBER"),
    ({"key": "QPS:W364", "name": "W364_FINAL_COPY", "status": "ACTIVE"}, "C4_RESERVED"),
    ({"key": "QPS:W364", "name": "W364_DECK", "status": "DONE"}, "C5_STATUS"),
    ({"key": "QPS:W364", "name": "W364_DECK", "status": "ACTIVE", "aliases": ["Bad_Alias"]}, "C6_ALIAS"),
    ({"key": "QPS:W364", "name": "W364_DECK", "status": "ACTIVE", "aliases": ["deck-for-w370"]}, "C7_ALIAS_NUMBER"),
    ({"key": "W364", "name": "W364_DECK", "status": "ACTIVE"}, "C1_KEY"),
    ({"key": "BOOT:Wave-0", "name": "W000_BOOT", "status": "HOLD"}, "C2_NAME"),
])
def test_single_claim_rules(rules, claim, code):
    assert code in codes(wave_claims.validate_claims(doc("R", [claim]), rules, "R"))


def test_alias_may_name_its_own_number(rules):
    claim = {"key": "QPS:W364", "name": "W364_DECK", "status": "ACTIVE", "aliases": ["w364-deck"]}
    assert wave_claims.validate_claims(doc("R", [claim]), rules, "R") == []


def test_path_boundaries_nest_only_along_lineage(rules):
    outer = {"key": "QPS:W364", "name": "W364_DECK", "status": "ACTIVE", "paths": ["triage/w364/"]}
    child = {"key": "QPS:W365", "name": "W365_DECK", "status": "ACTIVE", "paths": ["triage/w364/sub/"],
             "parent": "QPS:W364"}
    stray = {"key": "QPS:W366", "name": "W366_OTHER", "status": "ACTIVE", "paths": ["triage/w364/x"]}
    assert wave_claims.validate_claims(doc("R", [outer, child]), rules, "R") == []
    found = wave_claims.validate_claims(doc("R", [outer, child, stray]), rules, "R")
    assert codes(found) == ["D5_PATH_OVERLAP"] and found[0]["key"] == "QPS:W366"


def test_role_rules(rules):
    owned = {"key": "QPS:W364", "name": "W364_DECK", "status": "ACTIVE"}
    found = wave_claims.validate_claims(
        doc("R", [owned], [{"key": "QPS:W364", "role": "reviewer"}, {"key": "QPS:W113", "role": "boss"}]), rules, "R")
    assert codes(found) == ["C8_ROLE", "C8_ROLE"]


def rollup(sets, observed, lineage=(), rules=None):
    return wave_claims.rollup(sets, observed, set(lineage), rules or wave_claims.load_naming_rules())


def test_contested_key_keeps_every_claimant_indexed(rules):
    sets = {
        "A": (doc("A", [{"key": "QPS:W113", "name": "W113_MESH_CLOSURE", "status": "ACTIVE", "aliases": ["mesh-x"]}]), False),
        "B": (doc("B", [{"key": "QPS:W113", "name": "W113_DOW_RECEIVER", "status": "ACTIVE"},
                        {"key": "QPS:W200", "name": "W200_MESH_CLOSURE", "status": "ACTIVE"}]), False),
        "C": (doc("C", [{"key": "QPS:W364", "name": "W364_DECK", "status": "ACTIVE", "aliases": ["mesh-x"]}]), True),
    }
    observed = {"QPS:W113": {"A", "B"}, "QPS:W200": {"B"}, "QPS:W364": {"C"}}
    claims, found, census = rollup(sets, observed, rules=rules)
    assert claims["QPS:W113"]["owner"] == "CONTESTED"
    assert claims["QPS:W113"]["claimants"] == ["A", "B"]
    got = {(f["code"], f["key"]) for f in found}
    assert ("D1_DUP_OWNER", "QPS:W113") in got
    assert ("D3_ALIAS_CLASH", "QPS:W113") in got and ("D3_ALIAS_CLASH", "QPS:W364") in got
    assert ("D4_SLUG_NO_LINEAGE", "QPS:W200") in got   # MESH_CLOSURE slug reused without lineage
    assert census["contested_keys"] == 1


def test_slug_carries_forward_only_along_lineage(rules):
    base = [{"key": "QPS:W364", "name": "W364_ICD_FAMILY", "status": "CLOSED"}]
    nxt = {"key": "QPS:W366", "name": "W366_ICD_FAMILY", "status": "ACTIVE"}
    observed = {"QPS:W364": {"R"}, "QPS:W366": {"R"}}
    _, found, _ = rollup({"R": (doc("R", base + [nxt]), False)}, observed, rules=rules)
    assert codes(found) == ["D4_SLUG_NO_LINEAGE"]
    _, found, _ = rollup({"R": (doc("R", base + [dict(nxt, parent="QPS:W364")]), False)}, observed, rules=rules)
    assert found == []
    _, found, _ = rollup({"R": (doc("R", base + [nxt]), False)}, observed, [("QPS:W366", "QPS:W364")], rules)
    assert found == []   # an observed lineage edge counts as the parent declaration


def test_canonical_name_is_never_reused_and_alias_never_shadows_a_name(rules):
    sets = {"R": (doc("R", [
        {"key": "QPS:W364", "name": "W364_DECK", "status": "ACTIVE"},
        {"key": "QPS:W365", "name": "W365_PLANT", "status": "ACTIVE", "aliases": ["w364-deck"]},
    ]), False)}
    _, found, _ = rollup(sets, {"QPS:W364": {"R"}, "QPS:W365": {"R"}}, rules=rules)
    assert {f["code"] for f in found} >= {"D3_ALIAS_CLASH"}


def test_numbering_no_backfill_and_next_free(rules):
    sets = {"R": (doc("R", [{"key": "QPS:W050", "name": "W050_HOLE", "status": "ACTIVE"},
                            {"key": "QPS:W382", "name": "W382_PLANT_SYNC", "status": "ACTIVE"}]), False)}
    _, found, census = rollup(sets, {"QPS:W381": {"R"}}, rules=rules)
    assert [(f["code"], f["key"]) for f in found if f["severity"] == "error"] == [("N1_BACKFILL", "QPS:W050")]
    assert census["next_free"] == {"QPS": "W383"}


def test_overlap_census_and_private_digests(rules):
    sets = {"P": (doc("P", [{"key": "QPS:W364", "name": "W364_SECRET_TOPIC", "status": "ACTIVE",
                             "aliases": ["secret-topic"], "paths": ["triage/w364/"]}]), True)}
    claims, found, census = rollup(sets, {"QPS:W364": {"P", "Q"}}, rules=rules)
    rec = claims["QPS:W364"]
    assert "name" not in rec and "aliases" not in rec and "paths" not in rec
    assert rec["name_sha256"] == wave_claims.digest("W364_SECRET_TOPIC") and rec["path_count"] == 1
    assert "SECRET" not in yaml.safe_dump(found).upper()
    assert codes(found) == ["O1_UNDECLARED_PARTICIPANT"] and census["undeclared_participants"] == 1


def test_private_names_are_redacted_in_local_messages(rules):
    bad = doc("P", [{"key": "QPS:W364", "name": "W364_secret", "status": "ACTIVE", "aliases": ["Secret_Alias"]}])
    text = yaml.safe_dump(wave_claims.validate_claims(bad, rules, "P", private=True))
    assert "secret" not in text.lower()


def test_proposer_names_from_own_records_and_defers_the_rest(tmp_path, rules):
    build_wave_register.git(tmp_path, "init", "-q")
    for f in ["triage/w368/QPS_W368_COOLDOWN_FULL_REBUILD_v0.1.yaml", "triage/w369/README.md",
              "shared/w370_notes.md"]:
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text("x\n", encoding="utf-8")
    build_wave_register.git(tmp_path, "add", ".")
    build_wave_register.git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "f")
    register = {"waves": [
        {"key": "QPS:W368", "namespace": "QPS", "id": "W368", "confidence": "exact",
         "repos": {"R": {"paths": 1, "anchor": "triage/w368"}}},
        {"key": "QPS:W369", "namespace": "QPS", "id": "W369", "confidence": "exact",
         "repos": {"R": {"paths": 1, "anchor": "triage/w369"}}},
        {"key": "QPS:W371", "namespace": "QPS", "id": "W371", "confidence": "exact",
         "repos": {"R": {"paths": 2, "anchor": "x"}, "S": {"paths": 2, "anchor": "y"}}},
    ]}
    draft = wave_claims.propose(register, "R", rules, repo_path=tmp_path)
    assert draft["owns"] == [{"key": "QPS:W368", "name": "W368_COOLDOWN_FULL_REBUILD", "status": "ACTIVE",
                              "paths": ["triage/w368/"]}]
    assert draft["_proposal"]["needs_name"] == ["QPS:W369"]
    assert draft["_proposal"]["contested_ties"] == ["QPS:W371"]
    body = {k: v for k, v in draft.items() if k != "_proposal"}
    assert wave_claims.validate_claims(body, rules, "R") == []


def test_committed_register_rollup_is_clean():
    """Control gate: the published register carries no claim errors."""
    reg = yaml.safe_load((ROOT / "federation" / "waves" / "WAVE_REGISTER.yaml").read_text(encoding="utf-8"))
    dedup = reg["dedup"]
    assert dedup["census"]["violations"]["error"] == 0, [v for v in dedup["violations"] if v["severity"] == "error"]
    assert reg["sources"]["GBOGEB/CODEX"]["claims_file"] is True
    w113 = next(e for e in reg["waves"] if e["key"] == "QPS:W113")
    assert w113["claim"]["owner"] == "GBOGEB/CODEX" and w113["status"] == "ACTIVE"
    assert w113["claim"]["name"] == "W113_MESH_CLOSURE_CONTROLLER"
