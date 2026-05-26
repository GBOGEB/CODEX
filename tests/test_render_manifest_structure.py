from pathlib import Path


MANIFEST_DIR = Path("MANIFEST")

REQUIRED_MANIFEST_FILES = [
    "CHANGELOG.md",
    "ROADMAP.md",
    "MASTER_SLIDE_REGISTRY.yaml",
    "MASTER_FIGURE_REGISTRY.yaml",
    "STYLE_GUIDE.md",
    "RENDER_RULES.md",
    "LINEAGE.md",
]


def test_a6_required_manifest_files_exist() -> None:
    missing = [name for name in REQUIRED_MANIFEST_FILES if not (MANIFEST_DIR / name).exists()]
    assert missing == []


def test_slide_and_figure_registries_use_expected_identifiers() -> None:
    slide_registry_path = MANIFEST_DIR / "MASTER_SLIDE_REGISTRY.yaml"
    figure_registry_path = MANIFEST_DIR / "MASTER_FIGURE_REGISTRY.yaml"

    assert slide_registry_path.exists()
    assert figure_registry_path.exists()

    slide_registry = slide_registry_path.read_text(encoding="utf-8")
    figure_registry = figure_registry_path.read_text(encoding="utf-8")

    assert "registry: MASTER_SLIDE_REGISTRY" in slide_registry
    assert "slide_id:" in slide_registry
    assert "registry: MASTER_FIGURE_REGISTRY" in figure_registry
    assert "figure_id:" in figure_registry
