"""Export INCUBATOR runtime artifacts for portability and archival."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.parse_chat_tuple import load_tuple_documents

DEFAULT_MAP_FILES = ("category_map.yml", "theme_map.yml", "repo_ingress_map.yml")
DEFAULT_SCRIPT_FILES = (
    "parse_chat_tuple.py",
    "build_incubator_index.py",
    "extract_themes.py",
    "export_incubator_runtime.py",
)
DEFAULT_DOC_FILES = (
    "incubator_index.md",
    "incubator_runtime_map.md",
    "INCUBATOR_ABACUS_BRIDGE.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional export output directory (default: outputs/incubator_export).",
    )
    return parser.parse_args()


def export_incubator_runtime(root: Path, output_dir: Path | None = None) -> Path:
    """Export incubator runtime package from repository root to output_dir."""
    incubator = root / "incubator"
    maps = root / "maps"
    scripts = root / "scripts"
    docs = root / "docs"
    export = output_dir or (root / "outputs" / "incubator_export")

    if export.exists():
        shutil.rmtree(export)
    export.mkdir(parents=True, exist_ok=True)

    tuple_docs = load_tuple_documents(incubator)

    incubator_export = export / "incubator"
    incubator_export.mkdir(parents=True, exist_ok=True)
    for item in incubator.iterdir():
        if item.is_file():
            shutil.copy2(item, incubator_export / item.name)

    maps_export = export / "maps"
    maps_export.mkdir(parents=True, exist_ok=True)
    for map_file in DEFAULT_MAP_FILES:
        map_path = maps / map_file
        if map_path.exists():
            shutil.copy2(map_path, maps_export / map_file)

    scripts_export = export / "scripts"
    scripts_export.mkdir(parents=True, exist_ok=True)
    for script_file in DEFAULT_SCRIPT_FILES:
        script_path = scripts / script_file
        if script_path.exists():
            shutil.copy2(script_path, scripts_export / script_file)

    docs_export = export / "docs"
    docs_export.mkdir(parents=True, exist_ok=True)
    for doc_file in DEFAULT_DOC_FILES:
        doc_path = docs / doc_file
        if doc_path.exists():
            shutil.copy2(doc_path, docs_export / doc_file)

    metadata = export / "EXPORT_METADATA.txt"
    metadata.write_text(
        "INCUBATOR Runtime Export\n"
        "========================\n"
        "\n"
        f"Tuple count validated pre-export: {len(tuple_docs)}\n"
        "\n"
        "This export contains:\n"
        "  - incubator/*.yml: Tuple records and schema\n"
        "  - maps/*.yml: Category, theme, and repo ingress mappings\n"
        "  - scripts/*.py: Parser, index builder, theme extractor, export utility\n"
        "  - docs/*.md: Generated documentation and ABACUS bridge notes\n"
        "\n"
        "Bridge relevance:\n"
        "  - docs/INCUBATOR_ABACUS_BRIDGE.md\n"
        "  - Bridge companion script: scripts/export_abacus_runtime.py\n"
        "\n"
        "For usage:\n"
        "  python scripts/parse_chat_tuple.py\n"
        "  python scripts/build_incubator_index.py\n"
        "  python scripts/extract_themes.py\n"
        "  python scripts/export_incubator_runtime.py\n"
        "\n"
        "CODEX INCUBATOR W000/W001 scaffold\n"
        "Program: INCUBATOR\n"
        "Repository: GBOGEB/CODEX\n",
        encoding="utf-8",
    )
    return export


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    export_path = export_incubator_runtime(root, args.output_dir)
    print(f"INCUBATOR runtime export complete: {export_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
