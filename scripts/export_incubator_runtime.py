"""Export INCUBATOR runtime artifacts for portability and archival.

Follows the pattern established by export_abacus_runtime.py for consistency
across CODEX/ABACUS ecosystem.
"""

from pathlib import Path
import shutil


def main():
    """Export INCUBATOR runtime to outputs/incubator_export."""
    ROOT = Path(__file__).resolve().parents[1]
    INCUBATOR = ROOT / 'incubator'
    MAPS = ROOT / 'maps'
    SCRIPTS = ROOT / 'scripts'
    DOCS = ROOT / 'docs'
    EXPORT = ROOT / 'outputs' / 'incubator_export'

    # Clean export directory to remove stale files
    if EXPORT.exists():
        shutil.rmtree(EXPORT)

    EXPORT.mkdir(parents=True, exist_ok=True)

    # Export incubator tuple files
    incubator_export = EXPORT / 'incubator'
    incubator_export.mkdir(parents=True, exist_ok=True)
    for item in INCUBATOR.iterdir():
        if item.is_file():
            shutil.copy2(item, incubator_export / item.name)

    # Export maps
    maps_export = EXPORT / 'maps'
    maps_export.mkdir(parents=True, exist_ok=True)
    for map_file in ['category_map.yml', 'theme_map.yml', 'repo_ingress_map.yml']:
        map_path = MAPS / map_file
        if map_path.exists():
            shutil.copy2(map_path, maps_export / map_file)

    # Export incubator scripts
    scripts_export = EXPORT / 'scripts'
    scripts_export.mkdir(parents=True, exist_ok=True)
    for script_file in ['parse_chat_tuple.py', 'build_incubator_index.py', 'extract_themes.py']:
        script_path = SCRIPTS / script_file
        if script_path.exists():
            shutil.copy2(script_path, scripts_export / script_file)

    # Export generated docs
    docs_export = EXPORT / 'docs'
    docs_export.mkdir(parents=True, exist_ok=True)
    for doc_file in ['incubator_index.md', 'incubator_runtime_map.md']:
        doc_path = DOCS / doc_file
        if doc_path.exists():
            shutil.copy2(doc_path, docs_export / doc_file)

    # Create export metadata
    metadata = EXPORT / 'EXPORT_METADATA.txt'
    metadata.write_text(
        'INCUBATOR Runtime Export\n'
        '========================\n'
        '\n'
        'This export contains:\n'
        '  - incubator/*.yml: Tuple records and schema\n'
        '  - maps/*.yml: Category, theme, and repo ingress mappings\n'
        '  - scripts/*.py: Parser, index builder, theme extractor\n'
        '  - docs/*.md: Generated documentation\n'
        '\n'
        'For usage:\n'
        '  python scripts/parse_chat_tuple.py\n'
        '  python scripts/build_incubator_index.py\n'
        '  python scripts/extract_themes.py\n'
        '\n'
        'CODEX INCUBATOR W000/W001 scaffold\n'
        'Program: INCUBATOR\n'
        'Repository: GBOGEB/CODEX\n',
        encoding='utf-8'
    )

    print(f'INCUBATOR runtime export complete: {EXPORT}')


if __name__ == '__main__':
    main()
