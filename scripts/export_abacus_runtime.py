from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ABACUS = ROOT / 'abacus_runtime'
EXPORT = ROOT / 'outputs' / 'runtime_export'

# Clean export directory to remove stale files
if EXPORT.exists():
    shutil.rmtree(EXPORT)

EXPORT.mkdir(parents=True, exist_ok=True)

# Recursively copy entire abacus_runtime directory
for item in ABACUS.iterdir():
    target = EXPORT / item.name

    if item.is_file():
        shutil.copy2(item, target)
    elif item.is_dir():
        shutil.copytree(item, target)

print('ABACUS runtime export complete.')
