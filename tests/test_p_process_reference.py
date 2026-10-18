"""Fail-closed P-process -> MYCELIUM consumer tests (offline, zero secrets)."""
import copy
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from mission_control.mycelium.p_process_reference import validate, from_archives, sha256

SHA = "a"*40
REPOS = sorted("GBOGEB/"+v for v in (
    "ABACUS", "CODEX", "Q_engineering_tools", "cryoplant-project",
    "gg_MATH", "pipeline-automation-hub"))


def fixture():
    sources = {
        "state": {"lifted": False, "repos": {r: {
            "mode": "CODE_PURPLE" if r.endswith("ABACUS") else "EVERRED",
            "ruleset": "RED"} for r in REPOS}},
        "census": {"lifted": False, "lift": [{"ok": True},{"ok": False}]},
        "everred": {"roots": [{"id":"ABACUS-RC-2026-0001",
                               "severity":"P0","state":"BLOCKED_AUTHORITY"}]},
        "drift": {"repos": {r: {"red": True} for r in REPOS}}
    }
    blobs = {k:(json.dumps(v,sort_keys=True)+"\n").encode() for k,v in sources.items()}
    nodes = [{"id":"repo:"+repo,"kind":"repository","owner":repo,
              "mode":sources["state"]["repos"][repo]["mode"],"ruleset":"RED",
              "evidence":"PRODUCER_SNAPSHOT"} for repo in REPOS]
    nodes.append({"id":"root:ABACUS-RC-2026-0001","kind":"issue",
                  "owner":"GBOGEB/ABACUS","severity":"P0","state":"BLOCKED_AUTHORITY",
                  "evidence":"PRODUCER_SNAPSHOT"})
    candidate = {
        "schema":"mycelium.p_process.candidate/1.0",
        "authority_transfer":False,"mutation_enabled":False,
        "dispatch_authorized":False,"formal_credit_delta":0,
        "engineering_credit_delta":0,"merge_admission":"HOLD",
        "consumer_acceptance":"WITHHELD",
        "target":{"repository":"GBOGEB/CODEX","surface":"mission_control/mycelium",
                  "mechanism":"REFERENCE_CANDIDATE","owner_acceptance_required":True},
        "source":{"repository":"GBOGEB/pipeline-automation-hub",
                  "commit_sha":SHA,
                  "data_digests_sha256":{k:sha256(v) for k,v in blobs.items()}},
        "incident":{"lifted":False,"criteria_met":1,"criteria_total":2},
        "nodes":nodes,"edges":[{"from":"root:ABACUS-RC-2026-0001",
                               "to":"repo:GBOGEB/ABACUS",
                               "kind":"references","evidence":"DECLARED_SOURCE_LINK"}]
    }
    return candidate,blobs


def make_zip(path, candidate, blobs):
    paths={"state":"data/p_state.json","census":"code-purple/kit/census.json",
           "everred":"everred/data/everred.json","drift":"rulesets/drift.json"}
    manifest={"files_sha256":{paths[k]:sha256(data) for k,data in blobs.items()}}
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        for k,rel in paths.items():z.writestr("p-process/"+rel,blobs[k])
        z.writestr("p-process/manifest.json",json.dumps(manifest))
    nested=buf.getvalue()
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("mycelium-p-process-candidate.json",json.dumps(candidate))
        z.writestr("p-process-site-test.zip",nested)
        z.writestr("p-process-site-test.zip.sha256",
                   sha256(nested)+"  p-process-site-test.zip\n")


class PProcessConsumer(unittest.TestCase):
    def test_positive_is_deferred_not_accepted(self):
        c,b=fixture();r=validate(c,b,SHA)
        self.assertEqual((r["checked_repos"],r["checked_roots"],r["checked_edges"]),(6,1,1))
        self.assertEqual(r["source_parity"],"PASS")
        self.assertEqual((r["decision"],r["merge_admission"],r["consumer_acceptance"]),
                         ("DEFER","HOLD","WITHHELD"))

    def test_nested_native_zip_and_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            c,b=fixture();path=Path(d)/"native.zip";make_zip(path,c,b)
            r=from_archives(path,SHA)
            self.assertEqual(r["manifest_verified_files"],4)
            self.assertEqual(r["checked_roots"],1)
            self.assertEqual(len(r["outer_sha256"]),64)

    def test_bad_sha_and_mutated_source(self):
        c,b=fixture()
        with self.assertRaisesRegex(ValueError,"stale producer head"):
            validate(c,b,"b"*40)
        b["census"]=b"{}"
        with self.assertRaisesRegex(ValueError,"source digest"):
            validate(c,b,SHA)

    def test_security_promotion_rejected(self):
        for key,val in (
            ("mutation_enabled",True),("dispatch_authorized",True),
            ("authority_transfer",True),("formal_credit_delta",1),
            ("engineering_credit_delta",1),("merge_admission","PASS"),
            ("consumer_acceptance","ACCEPT")):
            with self.subTest(key=key):
                c,b=fixture();c[key]=val
                with self.assertRaises(ValueError):validate(c,b,SHA)

    def test_duplicate_and_missing_graph_nodes(self):
        for key in ("duplicate","missing"):
            c,b=fixture()
            if key=="duplicate":c["nodes"].append(copy.deepcopy(c["nodes"][0]))
            else:c["nodes"].pop()
            with self.assertRaises(ValueError):validate(c,b,SHA)

    def test_unowned_or_promoted_edges(self):
        for key,val in (("to","repo:GBOGEB/CODEX"),("evidence","PRODUCER_NATIVE")):
            c,b=fixture();c["edges"][0][key]=val
            with self.assertRaises(ValueError):validate(c,b,SHA)

    def test_forged_lift_denominator(self):
        c,b=fixture();c["incident"]["criteria_met"]=2
        with self.assertRaisesRegex(ValueError,"lift denominator"):validate(c,b,SHA)

    def test_archive_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("../injection","bad")
            with self.assertRaises(ValueError):from_archives(p,SHA)

    def test_root_identity_and_owner_preserved(self):
        c,b=fixture();c["nodes"][-1]["owner"]="GBOGEB/CODEX"
        with self.assertRaisesRegex(ValueError,"root state drift"):validate(c,b,SHA)


def fleet_fixture(count=16):
    """Six-source-authority, 16-root candidate with digest-reconciled inputs."""
    candidate, blobs = fixture()
    families = (
        ("ABACUS", "ABACUS"),
        ("CODEX", "CODEX"),
        ("CRYO", "cryoplant-project"),
        ("GGMATH", "gg_MATH"),
        ("QET", "Q_engineering_tools"),
        ("PAH", "pipeline-automation-hub"),
    )
    roots = []
    nodes = [n for n in candidate["nodes"] if n["kind"] == "repository"]
    edges = []
    for i in range(count):
        family, owner = families[i % len(families)]
        rid = f"{family}-RC-2026-{i + 1:04d}"
        roots.append({"id": rid, "state": "BLOCKED_AUTHORITY", "severity": "P0"})
        nodes.append({
            "id": "root:" + rid, "kind": "issue",
            "owner": "GBOGEB/" + owner,
            "state": "BLOCKED_AUTHORITY", "severity": "P0",
            "evidence": "PRODUCER_SNAPSHOT",
        })
        edges.append({
            "from": "root:" + rid, "to": "repo:GBOGEB/" + owner,
            "kind": "references", "evidence": "DECLARED_SOURCE_LINK",
        })
    blobs["everred"] = (
        json.dumps({"roots": roots}, sort_keys=True) + "\n"
    ).encode("utf-8")
    candidate["source"]["data_digests_sha256"]["everred"] = sha256(
        blobs["everred"]
    )
    candidate["nodes"] = nodes
    candidate["edges"] = edges
    return candidate, blobs


class PProcessFleetPenetration(unittest.TestCase):
    def test_six_repos_sixteen_roots_and_sixteen_edges_remain_withheld(self):
        candidate, blobs = fleet_fixture()
        result = validate(candidate, blobs, SHA)
        self.assertEqual(
            (result["checked_repos"], result["checked_roots"],
             result["checked_edges"]), (6, 16, 16)
        )
        self.assertEqual(result["decision"], "DEFER")
        self.assertEqual(result["consumer_acceptance"], "WITHHELD")
        self.assertEqual(result["merge_admission"], "HOLD")
        self.assertEqual(result["engineering_credit_delta"], 0)

    def test_sixteen_root_evidence_survives_nested_archive(self):
        with tempfile.TemporaryDirectory() as d:
            candidate, blobs = fleet_fixture()
            path = Path(d) / "native.zip"
            make_zip(path, candidate, blobs)
            result = from_archives(path, SHA)
            self.assertEqual(
                (result["checked_roots"], result["checked_edges"]), (16, 16)
            )
            self.assertEqual(result["manifest_verified_files"], 4)
            self.assertEqual(result["decision"], "DEFER")

    def test_duplicate_and_missing_root_edges_fail_closed(self):
        for mutation in ("duplicate", "missing"):
            with self.subTest(mutation=mutation):
                candidate, blobs = fleet_fixture()
                if mutation == "duplicate":
                    candidate["edges"][1] = copy.deepcopy(candidate["edges"][0])
                else:
                    candidate["edges"].pop()
                with self.assertRaises(ValueError):
                    validate(candidate, blobs, SHA)

    def test_cross_repo_root_authority_forgery_rejected(self):
        candidate, blobs = fleet_fixture()
        candidate["edges"][0]["to"] = "repo:GBOGEB/CODEX"
        with self.assertRaisesRegex(ValueError, "cross-authority edge"):
            validate(candidate, blobs, SHA)

    def test_source_root_duplication_rejected_after_rehash(self):
        candidate, blobs = fleet_fixture()
        roots = json.loads(blobs["everred"])["roots"]
        roots.append(copy.deepcopy(roots[0]))
        blobs["everred"] = json.dumps({"roots": roots}).encode("utf-8")
        candidate["source"]["data_digests_sha256"]["everred"] = sha256(
            blobs["everred"]
        )
        with self.assertRaisesRegex(ValueError, "duplicate source roots"):
            validate(candidate, blobs, SHA)

    def test_six_repo_population_forgery_rejected_after_rehash(self):
        candidate, blobs = fleet_fixture()
        state = json.loads(blobs["state"])
        state["repos"].pop("GBOGEB/CODEX")
        blobs["state"] = json.dumps(state).encode("utf-8")
        candidate["source"]["data_digests_sha256"]["state"] = sha256(
            blobs["state"]
        )
        with self.assertRaisesRegex(ValueError, "repo population"):
            validate(candidate, blobs, SHA)

    def test_boolean_credit_and_stale_producer_denied(self):
        for key in ("formal_credit_delta", "engineering_credit_delta"):
            with self.subTest(key=key):
                candidate, blobs = fleet_fixture()
                candidate[key] = False
                with self.assertRaisesRegex(ValueError, "forbidden promotion"):
                    validate(candidate, blobs, SHA)
        candidate, blobs = fleet_fixture()
        candidate["source"]["commit_sha"] = "f" * 40
        with self.assertRaisesRegex(ValueError, "stale producer head"):
            validate(candidate, blobs, SHA)

    def test_nested_zip_checksum_forgery_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            candidate, blobs = fleet_fixture()
            path = Path(d) / "nested.zip"
            make_zip(path, candidate, blobs)
            with zipfile.ZipFile(path, "r") as archive:
                entries = {
                    info.filename: archive.read(info)
                    for info in archive.infolist()
                }
            entries["p-process-site-test.zip.sha256"] = (
                b"0" * 64 + b"  p-process-site-test.zip\n"
            )
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                for name, raw in entries.items():
                    archive.writestr(name, raw)
            with self.assertRaisesRegex(ValueError, "nested ZIP SHA mismatch"):
                from_archives(path, SHA)


if __name__=="__main__":
    unittest.main()
