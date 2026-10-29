"""Coverage wave 14 (L3): QPS BT engine (PAL + Monte Carlo), pca_engine optional
layers (reporting, sklearn validation, NLPCA scaffold, with fakes for optional
deps), GISTAU/renderer scaffolds, release identity, export models, public-source
policy and the runtime-consumer map.
"""
from __future__ import annotations

import json
import random
import sys
import types

import pytest

from tests.coverage_waves._loader import ROOT, load, run_main

PAL = "automation/bt-engine/src/qps_bt_engine/pal.py"
MC = "automation/bt-engine/src/qps_bt_engine/montecarlo.py"
PNG = "src/gistau_ch15/visualization/export_png.py"
SHOT = "renderers/regression/screenshot_compare.py"
RELID = "scripts/check_release_identity.py"
PUBSRC = "qps/cost-master/ci/check_public_source_only.py"
RTMAP = "scripts/map_runtime_consumers.py"

W = {"reliability": 0.4, "performance": 0.3, "functional": 0.1, "quality": 0.1, "cost": 0.1}


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- PAL + Monte Carlo
def test_pal_scores_and_mandates():
    m = load(PAL)
    assert m.normalized_score({"scores": {"reliability": 1, "cost": 2}}, W) == pytest.approx(0.6)
    assert m.normalized_score({"legal_mandate": True}, W) == 1_000_000.0
    assert m.normalized_score({"safety_mandate": True, "scores": {}}, {}) == 1_000_000.0
    assert m.normalized_score({}, W) == 0.0


@pytest.mark.parametrize(("left", "right", "out"), [(1.0, 0.0, 1.0), (0.0, 1.0, 0.0), (0.5, 0.5, 0.5)])
def test_pal_compare(left, right, out):
    m = load(PAL)
    assert m.compare_requirements({"scores": {"reliability": left}}, {"scores": {"reliability": right}}, W) == out


def test_montecarlo_perturb_and_stability():
    m = load(MC)
    pal = load(PAL)
    pw = m.perturb_weights(dict(W, legal_mandate=9.0), random.Random(1), 0.05)
    assert "legal_mandate" not in pw and sum(pw.values()) == pytest.approx(1.0)
    assert m.perturb_weights({"a": 0.0}, random.Random(1), 0.1) == {"a": 0.0}
    reqs = [{"id": "hi", "scores": {"reliability": 1.0}}, {"id": "lo", "scores": {"cost": 0.1}},
            {"id": "law", "legal_mandate": True}]
    res = m.run_rank_stability(reqs, W, pal.normalized_score, m.MonteCarloConfig(iterations=25, seed=7))
    assert [r["id"] for r in res] == ["law", "hi", "lo"]
    assert res[0]["stability"] == 1.0 and res[0]["best_rank"] == res[0]["worst_rank"] == 1
    again = m.run_rank_stability(reqs, W, pal.normalized_score, m.MonteCarloConfig(iterations=25, seed=7))
    assert again == res
    assert m.run_rank_stability(reqs[:1], W, pal.normalized_score)[0]["mean_rank"] == 1
    assert m.MonteCarloConfig().iterations == 1000


# ---------------------------------------------------------------- scaffolds
def test_png_placeholder_and_screenshot_scaffold(tmp_path, capsys):
    (p,) = load(PNG).PublicationPNGExporter().export_placeholder(tmp_path / "pub")
    assert p.read_text(encoding="utf-8") == "PNG export scaffolding active.\n"
    r = load(SHOT).ScreenshotComparator().compare("a.png", "b.png")
    assert (r.similarity_score, r.passed, r.candidate_image) == (1.0, True, "b.png")
    run_main(SHOT)
    assert "scaffold active" in capsys.readouterr().out


def test_availability_export(tmp_path, monkeypatch):
    from gistau_ch15.properties import availability_export as ae
    rows = ae.write_backend_availability(tmp_path / "d" / "a.json")
    assert json.loads((tmp_path / "d" / "a.json").read_text(encoding="utf-8")) == rows and rows


def test_availability_export_main_uses_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_main("src/gistau_ch15/properties/availability_export.py")
    assert (tmp_path / "docs/gistau-ch15/data/backend_availability.json").is_file()


# ---------------------------------------------------------------- release identity
def test_release_identity_repo_pass(capsys):
    assert load(RELID).main() == 0
    assert "RELEASE_IDENTITY_PASS" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("version", "pyproject", "message"),
    [
        ('{"version": ""}', 'version = "1"\n', "has no version"),
        ('{"version": "1.0"}', "name = 'x'\n", "project version not found"),
        ('{"version": "1.0"}', 'version = "2.0"\n', "VERSION.json=1.0 pyproject.toml=2.0"),
    ],
)
def test_release_identity_failures(tmp_path, monkeypatch, version, pyproject, message):
    m = load(RELID)
    _write(tmp_path / "VERSION.json", version)
    _write(tmp_path / "pyproject.toml", pyproject)
    monkeypatch.setattr(m, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match=message):
        m.main()


# ---------------------------------------------------------------- export models
def test_export_models():
    from tools.export import export_models as em
    assert em.RUNTIME_SCHEMA_VERSION == "0.1" and em.GOVERNANCE_RUNTIME_ID
    assert em.RuntimeSource("k", "p", "yaml").as_dict() == {"key": "k", "path": "p", "kind": "yaml"}
    v = em.ValidationSummary("k", "pass", 1, "r.json", ({"code": "E"},))
    assert v.as_dict()["errors"] == [{"code": "E"}]
    assert em.strip_runtime_volatility({"checked_at": "t", "status": "pass"}) == {"status": "pass"}
    nodes = [{"id": "b", "stage": "Review", "parent": "a"}, {"id": "a", "stage": "ITT"}, {"id": "z", "stage": "?"}]
    assert em.ordered_links(nodes, "child") == [{"source": "a", "target": "b", "relationship": "child"}]
    assert [n["id"] for n in em.sort_nodes(nodes, ["ITT", "Review"])] == ["a", "b", "z"]


# ---------------------------------------------------------------- public-source policy
def test_public_source_clean_tree(tmp_path, capsys):
    root = tmp_path / "bridge"
    _write(root / "README.md", "public notes")
    _write(root / ".git" / "secret.pdf", "ignored")
    with pytest.raises(SystemExit) as exc:
        run_main(PUBSRC, [str(root)])
    assert exc.value.code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["passed"] is True and data["files_scanned"] == 1


def test_public_source_findings(tmp_path):
    root = tmp_path / "bridge"
    _write(root / "deck.pptx", "x")
    _write(root / "dump.tar.gz", "x")
    _write(root / "notes.md", "LKT - Offer 1 price 29.243")
    _write(root / "check_public_source_only.py", "29.243")
    big = root / "big.bin"
    big.write_bytes(b"0" * 2_000_001)
    out = tmp_path / "o" / "r.json"
    with pytest.raises(SystemExit) as exc:
        run_main(PUBSRC, [str(root), "--output", str(out)])
    assert exc.value.code == 3
    rules = sorted((f["path"], f["rule"]) for f in json.loads(out.read_text(encoding="utf-8"))["findings"])
    assert ("deck.pptx", "forbidden_binary_or_archive") in rules
    assert ("dump.tar.gz", "forbidden_binary_or_archive") in rules
    assert ("big.bin", "public_source_file_over_2MB") in rules
    assert sum(1 for p, r in rules if p == "notes.md") == 2
    assert not any(p == "check_public_source_only.py" for p, _ in rules)


# ---------------------------------------------------------------- runtime consumer map
def test_runtime_consumer_map(tmp_path, monkeypatch, capsys):
    m = load(RTMAP)
    _write(tmp_path / "a.py", "uses LID_ONE and ssot/x.yaml via run_mcp_sweep\n")
    _write(tmp_path / "b.py", "mcp_sweep again\n")
    _write(tmp_path / "c.yaml", "LID_ONE: 1\n")
    _write(tmp_path / "d.yaml", "nothing\n")
    _write(tmp_path / "e.png", "x")
    bound = _write(tmp_path / "bound.json", json.dumps({"candidates": [
        {"path": "a.py"}, {"path": "b.py"}, {"path": "c.yaml", "candidate_class": "CONSUMER_OR_CONTRACT_CANDIDATE"},
        {"path": "d.yaml"}, {"path": "e.png"}, {"path": "missing.py"}]}))
    reg = _write(tmp_path / "reg.yaml", "nodes:\n  LID_ONE: {path: ssot/x.yaml}\n  LID_TWO: 1\n")
    out = tmp_path / "out.json"
    for name, value in (("ROOT", tmp_path), ("BOUND", bound), ("REG", reg), ("OUT", out)):
        monkeypatch.setattr(m, name, value)
    m.main()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["consumer_population_from_census"] == 1 and data["mapped_consumers"] == 3
    assert data["logical_id_reference_counts"] == {"LID_ONE": 2}
    assert data["hard_coded_authority_path_counts"] == {"LID_ONE": 1}
    assert data["duplicate_runtime_family_candidates"] == {"MCP_SWEEP": ["a.py", "b.py"]}
    assert "RUNTIME_MAP_PASS" in capsys.readouterr().out
    monkeypatch.setattr(m, "BOUND", tmp_path / "none.json")
    with pytest.raises(SystemExit, match="bound census missing"):
        m.main()


# ---------------------------------------------------------------- pca_engine optional layers
@pytest.fixture
def pca_pkg(monkeypatch):
    pytest.importorskip("numpy")
    monkeypatch.syspath_prepend(str(ROOT / "pca_engine" / "src"))
    import importlib
    return importlib.import_module("pca_engine")


def _data():
    import numpy as np
    rng = np.random.default_rng(0)
    base = rng.normal(size=(30, 2))
    return np.column_stack([base[:, 0], base[:, 0] * 2 + 0.01 * base[:, 1], base[:, 1]])


def test_pca_markdown_report(pca_pkg, tmp_path):
    from pca_engine.pca_core import fit_pca

    from pca_engine import reporting
    result = fit_pca(_data(), n_components=2)
    text = reporting.markdown_report(result)
    assert text.startswith("# PCA Report") and "Rows: 30" in text and "Features: 3" in text
    assert "| PC1 |" in text and "- PC2:" in text and "Retained components: 2" in text
    path = reporting.write_markdown_report(result, tmp_path / "r.md")
    assert path.read_text(encoding="utf-8") == text


def test_sklearn_validation_defers_without_sklearn(pca_pkg, monkeypatch):
    from pca_engine import sklearn_validation as sv
    monkeypatch.setitem(sys.modules, "sklearn", None)
    monkeypatch.setitem(sys.modules, "sklearn.decomposition", None)
    assert sv.validate_with_sklearn(_data()) == {"status": "DEFER_SKLEARN_NOT_INSTALLED"}


def test_sklearn_validation_with_fake_sklearn(pca_pkg, monkeypatch):
    import numpy as np
    from pca_engine.pca_core import fit_pca

    from pca_engine import sklearn_validation as sv
    ours = fit_pca(_data(), n_components=2)

    class FakePCA:
        def __init__(self, n_components):
            assert n_components == 2

        def fit(self, matrix):
            self.explained_variance_ = np.asarray(ours.eigenvalues_) + 0.5
            self.explained_variance_ratio_ = np.asarray(ours.explained_variance_ratio_)
            return self

    dec = types.ModuleType("sklearn.decomposition")
    dec.PCA = FakePCA
    pkg = types.ModuleType("sklearn")
    pkg.decomposition = dec
    monkeypatch.setitem(sys.modules, "sklearn", pkg)
    monkeypatch.setitem(sys.modules, "sklearn.decomposition", dec)
    res = sv.validate_with_sklearn(_data(), n_components=2)
    assert res["status"] == "PASS_VALIDATED"
    assert res["max_abs_eigenvalue_delta"] == pytest.approx(0.5) and res["max_abs_variance_ratio_delta"] == 0.0


def test_nlpca_fails_gracefully_without_tensorflow(pca_pkg, monkeypatch):
    from pca_engine import nlpca_autoencoder as nl
    monkeypatch.setitem(sys.modules, "tensorflow", None)
    assert nl.tensorflow_available() is False
    with pytest.raises(nl.OptionalDependencyError, match="TensorFlow is optional"):
        nl.build_autoencoder(4, 2)


class _FakeTensor:
    def __init__(self, shape):
        self.shape = shape


class _FakeModel:
    def __init__(self, inputs, outputs, name):
        self.name, self.outputs = name, outputs
        self.compiled = None

    def compile(self, optimizer, loss):
        self.compiled = (optimizer, loss)

    def fit(self, x, y, epochs, batch_size, verbose):
        return {"epochs": epochs}

    def predict(self, x, verbose=0):
        return [[0.0] * self.outputs.shape for _ in range(len(x))]


def _fake_keras():
    keras = types.SimpleNamespace()
    keras.Input = lambda shape, name: _FakeTensor(shape[0])
    keras.layers = types.SimpleNamespace(
        Dense=lambda width, activation=None, name=None: (lambda t: _FakeTensor(width)))
    keras.Model = _FakeModel
    tf = types.ModuleType("tensorflow")
    tf.keras = keras
    return tf


def test_nlpca_with_fake_keras(pca_pkg, monkeypatch):
    import numpy as np

    from pca_engine import nlpca_autoencoder as nl
    monkeypatch.setitem(sys.modules, "tensorflow", _fake_keras())
    assert nl.tensorflow_available() is True
    auto, enc = nl.build_autoencoder(4, 2, hidden_dims=(3,))
    assert auto.compiled == ("adam", "mse") and enc.outputs.shape == 2 and auto.outputs.shape == 4
    for bad in (0, 4, 5):
        with pytest.raises(ValueError, match="latent_dim"):
            nl.build_autoencoder(4, bad)
    res = nl.fit_nlpca(np.zeros((3, 4)), latent_dim=2, epochs=2)
    assert res["history"] == {"epochs": 2} and len(res["latent"]) == 3 and len(res["latent"][0]) == 2
