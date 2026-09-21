import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / "federation/qps/w286/validate_visual_golden_contract.py"
F = ROOT / "federation/qps/w286/QPS_W286_VISUAL_GOLDEN_SANITIZED_CONTRACT_v1.json"
S = importlib.util.spec_from_file_location("w286", V)
M = importlib.util.module_from_spec(S)
S.loader.exec_module(M)


def load():
    return json.loads(F.read_text(encoding="utf-8"))


def test_contract_passes():
    assert M.validate(load()) == []


def test_authority_inversion_rejected():
    d = load()
    d["semantic_authority"] = "CODEX_AUTHORITY"
    assert "authority_inversion" in M.validate(d)


def test_visual_divergence_required():
    d = load()
    d["visual_binary_hashes_pairwise_distinct"] = False
    assert "binary_divergence" in M.validate(d)


def test_source_repo_is_pinned():
    d = load()
    d["source_repo"] = "GBOGEB/not-the-child"
    assert "source_repo" in M.validate(d)


def test_source_pr_and_merge_are_pinned():
    d = load()
    d["source_pr"] = 9999
    d["source_merge"] = "0" * 40
    errors = M.validate(d)
    assert "source_pr" in errors
    assert "source_merge" in errors


def test_corpus_name_and_digest_are_pinned():
    d = load()
    d["corpus_name"] = "substituted-corpus"
    d["corpus_zip_sha256"] = "0" * 64
    errors = M.validate(d)
    assert "corpus_name" in errors
    assert "corpus_zip_sha256" in errors
