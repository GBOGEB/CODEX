from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'
PAGES = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'pages'

MINIMAL_ARTIFACTS = {
    OUT / 'runtime_status.md': '# Runtime Status\n\nRecovered minimal runtime artifact.\n',
    OUT / 'topology_runtime.mmd': 'graph TD\n    recovery --> topology\n',
    PAGES / 'index.html': '<html><body><h1>Recovered Runtime Dashboard</h1></body></html>',
}


def repair_missing_artifacts() -> dict:
    repaired = []
    existing = []
    for path, content in MINIMAL_ARTIFACTS.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > 0:
            existing.append(str(path.relative_to(ROOT)))
            continue
        path.write_text(content, encoding='utf-8')
        repaired.append(str(path.relative_to(ROOT)))

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'repair-complete',
        'repaired': repaired,
        'existing': existing,
        'repair_count': len(repaired),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Repair missing runtime artifacts')
    parser.parse_args()
    report = repair_missing_artifacts()
    report_path = OUT / 'self_healing_runtime_report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
