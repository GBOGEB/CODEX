"""Contract tests: wave naming ruleset, per-repo claims, federation roll-up and dedup."""
from __future__ import annotations

import subprocess
import sys
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
    claim = {"key": "QPS:W364", "name": "W364_DECK", "status": "ACTIVE", "aliases": ["w364-deck-plan"]}
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


def test_register_keeps_retired_names_reserved_across_runs(tmp_path):
    """dedup.reserved is carried from one register run to the next."""
    repo = tmp_path / "member"
    repo.mkdir()
    build_wave_register.git(repo, "init", "-q")

    def commit(claims: dict):
        (repo / ".waves").mkdir(exist_ok=True)
        (repo / ".waves" / "WAVE_CLAIMS.yaml").write_text(yaml.safe_dump(claims), encoding="utf-8")
        (repo / "triage" / "w300").mkdir(parents=True, exist_ok=True)
        (repo / "triage" / "w300" / "note.md").write_text("x\n", encoding="utf-8")
        (repo / "triage" / "w301").mkdir(parents=True, exist_ok=True)
        (repo / "triage" / "w301" / "note.md").write_text("x\n", encoding="utf-8")
        build_wave_register.git(repo, "add", ".")
        build_wave_register.git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                                "commit", "-qm", "c", "--allow-empty")

    out = tmp_path / "REGISTER.yaml"
    cmd = [sys.executable, str(ROOT / "scripts" / "build_wave_register.py"), "--strict",
           "--repo", f"GBOGEB/M={repo}", "--out", str(out)]
    commit(doc("GBOGEB/M", [{"key": "QPS:W300", "name": "W300_LEGACY_PLANT", "status": "CLOSED",
                             "aliases": ["legacy-plant"]}]))
    first = subprocess.run(cmd, capture_output=True, text=True)
    assert first.returncode == 0, first.stdout + first.stderr
    reserved = yaml.safe_load(out.read_text(encoding="utf-8"))["dedup"]["reserved"]
    assert {(e["kind"], e["key"]) for e in reserved} == {("name", "QPS:W300"), ("alias", "QPS:W300")}
    # W300's claim is removed; W301 reuses the retired name and alias.
    commit(doc("GBOGEB/M", [{"key": "QPS:W301", "name": "W300_LEGACY_PLANT", "status": "ACTIVE",
                             "aliases": ["legacy-plant"]}]))
    second = subprocess.run(cmd, capture_output=True, text=True)
    assert second.returncode == 2, second.stdout + second.stderr
    found = yaml.safe_load(out.read_text(encoding="utf-8"))["dedup"]["violations"]
    assert {(v["code"], v["key"]) for v in found} >= {
        ("D2_NAME_REUSE", "QPS:W301"), ("D3_ALIAS_CLASH", "QPS:W301")}


G = "gbogeb.global_waves/1"


def gdoc(*waves, steward="GBOGEB/CODEX"):
    return {"schema": G, "steward": steward, "waves": list(waves)}


def gwave(key="QPS:W060", name="W060_DOV_PCA_PULSE", **kw):
    w = {"key": key, "name": name, "status": "HOLD", "maturity": "CONVERGED",
         "origin": "GBOGEB/cryoplant-project"}
    w.update(kw)
    return w


def test_committed_global_waves_obey_the_ruleset(rules):
    d = yaml.safe_load((ROOT / wave_claims.GLOBAL_PATH).read_text(encoding="utf-8"))
    assert wave_claims.validate_global(d, rules) == []
    assert d["waves"], "the steward file must not be empty"


@pytest.mark.parametrize(
    "doc_, code",
    [
        ({"schema": "x"}, "G0_SCHEMA"),
        (gdoc(gwave(), steward="GBOGEB/ABACUS"), "G0_STEWARD"),
        (gdoc(gwave(maturity="SETTLED")), "G1_MATURITY"),
        (gdoc(gwave(origin="cryoplant")), "G2_ORIGIN"),
        (gdoc(gwave(paths=["architecture/w60/"])), "G3_GLOBAL_PATHS"),
        (gdoc(gwave(name="W061_DOV_PCA_PULSE")), "C3_NAME_NUMBER"),
        (gdoc(gwave(name="W060_DOV_FINAL")), "C4_RESERVED"),
        (gdoc(gwave(), gwave()), "D1_DUP_OWNER"),
    ],
)
def test_global_wave_rules(rules, doc_, code):
    assert code in codes(wave_claims.validate_global(doc_, rules))


def test_elevated_wave_is_federation_owned_and_members_only_participate(rules):
    sets = {
        "GBOGEB/ABACUS": (doc("GBOGEB/ABACUS", [], [{"key": "QPS:W060", "role": "receiver"}]), False),
        "GBOGEB/cryoplant-project": (
            doc("GBOGEB/cryoplant-project", [], [{"key": "QPS:W060", "role": "producer"}]), True),
    }
    observed = {"QPS:W060": {"GBOGEB/ABACUS", "GBOGEB/cryoplant-project"}}
    claims, found, census = wave_claims.rollup(sets, observed, set(), rules, global_doc=gdoc(gwave()))
    rec = claims["QPS:W060"]
    assert rec["owner"] == "FEDERATION" and rec["scope"] == "global"
    assert rec["origin"] == "GBOGEB/cryoplant-project" and rec["maturity"] == "CONVERGED"
    assert rec["participants"] == {"GBOGEB/ABACUS": "receiver", "GBOGEB/cryoplant-project": "producer"}
    assert found == []
    assert census["elevated_keys"] == {"total": 1, "by_maturity": {"CONVERGED": 1}}


def test_member_cannot_own_an_elevated_wave(rules):
    sets = {"GBOGEB/ABACUS": (doc("GBOGEB/ABACUS", [
        {"key": "QPS:W060", "name": "W060_ABACUS_PULSE", "status": "ACTIVE"}]), False)}
    claims, found, _ = wave_claims.rollup(sets, {"QPS:W060": {"GBOGEB/ABACUS"}}, set(), rules,
                                          global_doc=gdoc(gwave()))
    assert claims["QPS:W060"]["owner"] == "CONTESTED"
    d1 = [f for f in found if f["code"] == "D1_DUP_OWNER"]
    assert d1 and "elevated" in d1[0]["detail"]


def test_origin_declares_the_origin_role_and_undeclared_repos_warn(rules):
    sets = {"GBOGEB/cryoplant-project": (
        doc("GBOGEB/cryoplant-project", [], [{"key": "QPS:W060", "role": "receiver"}]), True)}
    observed = {"QPS:W060": {"GBOGEB/cryoplant-project", "GBOGEB/CODEX"}}
    _, found, _ = wave_claims.rollup(sets, observed, set(), rules, global_doc=gdoc(gwave()))
    assert codes(found) == ["G4_ORIGIN_ROLE", "O1_UNDECLARED_PARTICIPANT"]
    assert all(f["severity"] == "warning" for f in found)


def test_elevation_candidates_list_widely_recognised_ids(rules):
    observed = {"QPS:W200": {"A/a", "B/b", "C/c"}, "QPS:W201": {"A/a", "B/b"},
                "QPS:W202": {"A/a", "B/b", "C/c"}}
    sets = {"A/a": (doc("A/a", [{"key": "QPS:W202", "name": "W202_LOCAL", "status": "ACTIVE"}],
                        ), False)}
    _, _, census = wave_claims.rollup(sets, observed, set(), rules)
    cand = census["elevation_candidates"]
    assert cand["unowned"] == ["QPS:W200"] and cand["locally_owned"] == ["QPS:W202"]
    assert census["elevated_keys"]["total"] == 0


def test_validate_global_cli(tmp_path):
    p = tmp_path / "g.yaml"
    p.write_text(yaml.safe_dump(gdoc(gwave(maturity="?"))), encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "wave_claims.py"), "validate-global", str(p)],
                       capture_output=True, text=True, check=False)
    assert r.returncode == 1 and "G1_MATURITY" in r.stdout and r.stdout.isascii()
    ok = subprocess.run([sys.executable, str(ROOT / "scripts" / "wave_claims.py"), "validate-global"],
                        capture_output=True, text=True, check=False)
    assert ok.returncode == 0, ok.stdout
