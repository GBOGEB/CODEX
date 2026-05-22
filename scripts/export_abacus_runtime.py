from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ABACUS = ROOT / 'abacus_runtime'
EXPORT = ROOT / 'runtime_export'

EXPORT.mkdir(exist_ok=True)

for item in ABACUS.iterdir():
    target = EXPORT / item.name

    if item.is_file():
        shutil.copy(item, target)

print('ABACUS runtime export complete.')
