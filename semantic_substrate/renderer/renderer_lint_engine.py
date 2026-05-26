from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import yaml

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'MANIFEST'

REQUIRED_MANIFEST_FILES = [
    'STYLE_GUIDE.md',
    'RENDER_RULES.md',
]

DARK_WARNING = {
    'background': '#4A3110',
    'text': '#FFE9A3',
}


@dataclass
class LintIssue:
    severity: str
    rule: str
    message: str
    location: str


class RendererLintEngine:
    def __init__(self):
        self.issues: list[LintIssue] = []

    def lint(self) -> dict:
        self._validate_manifest_files()
        self._validate_theme_governance()
        self._validate_renderer_rules()

        return {
            'issue_count': len(self.issues),
            'issues': [asdict(issue) for issue in self.issues],
            'status': 'pass' if not self.issues else 'warning',
        }

    def _add_issue(self, severity: str, rule: str, message: str, location: str):
        self.issues.append(
            LintIssue(
                severity=severity,
                rule=rule,
                message=message,
                location=location,
            )
        )

    def _validate_manifest_files(self):
        for filename in REQUIRED_MANIFEST_FILES:
            path = MANIFEST / filename
            if not path.exists():
                self._add_issue(
                    severity='error',
                    rule='manifest-required-file',
                    message=f'Missing manifest file: {filename}',
                    location=str(path),
                )

    def _validate_theme_governance(self):
        style_guide = MANIFEST / 'STYLE_GUIDE.md'
        if not style_guide.exists():
            return

        content = style_guide.read_text(encoding='utf-8')

        required_tokens = [
            'semantic colors must transform by theme',
            DARK_WARNING['background'],
            DARK_WARNING['text'],
        ]

        for token in required_tokens:
            if token not in content:
                self._add_issue(
                    severity='warning',
                    rule='theme-governance-token',
                    message=f'Missing governance token: {token}',
                    location=str(style_guide),
                )

    def _validate_renderer_rules(self):
        render_rules = MANIFEST / 'RENDER_RULES.md'
        if not render_rules.exists():
            return

        content = render_rules.read_text(encoding='utf-8')

        required_sections = [
            'Typography Engine',
            'Layout Engine',
            'Navigation Engine',
            'Contrast Engine',
        ]

        for section in required_sections:
            if section not in content:
                self._add_issue(
                    severity='warning',
                    rule='renderer-governance-section',
                    message=f'Missing renderer governance section: {section}',
                    location=str(render_rules),
                )


def export_lint_report(output_path: str | Path, report: dict):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__':
    engine = RendererLintEngine()
    report = engine.lint()

    reports_dir = ROOT / 'PIPELINE' / 'REPORTS'
    export_lint_report(reports_dir / 'renderer_lint_report.json', report)

    print(json.dumps(report, indent=2))

    if report['status'] != 'pass':
        raise SystemExit(1)
