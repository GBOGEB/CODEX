from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SemanticCardTheme:
    background: str
    text: str
    border: str


class SemanticThemeRuntime:
    """Runtime semantic-theme resolver.

    This layer ensures semantic meaning survives:
    - dark mode
    - PDF rendering
    - HTML rendering
    - PPTX rendering
    - snapshot generation
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        if config_path is None:
            # Resolve to src/renderers/themes/semantic_cards.yaml
            self.config_path = Path(__file__).resolve().parent / 'themes' / 'semantic_cards.yaml'
        else:
            self.config_path = Path(config_path)
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        with self.config_path.open('r', encoding='utf-8') as handle:
            return yaml.safe_load(handle) or {}

    def resolve(self, semantic_type: str, mode: str) -> SemanticCardTheme:
        semantic_cards = self.data.get('semantic_cards')
        if not isinstance(semantic_cards, dict):
            raise KeyError("Missing 'semantic_cards' section in theme configuration.")

        semantic_entry = semantic_cards.get(semantic_type)
        if not isinstance(semantic_entry, dict):
            valid_semantic_types = ', '.join(sorted(semantic_cards.keys()))
            raise KeyError(
                f"Unknown semantic type '{semantic_type}'. Valid options: {valid_semantic_types}"
            )

        entry = semantic_entry.get(mode)
        if not isinstance(entry, dict):
            valid_modes = ', '.join(sorted(semantic_entry.keys()))
            raise KeyError(f"Unknown mode '{mode}' for '{semantic_type}'. Valid options: {valid_modes}")

        return SemanticCardTheme(
            background=entry['background'],
            text=entry['text'],
            border=entry['border'],
        )


if __name__ == '__main__':
    runtime = SemanticThemeRuntime()
    warning_dark = runtime.resolve('warning', 'dark')

    print('warning.dark')
    print(f'  background={warning_dark.background}')
    print(f'  text={warning_dark.text}')
    print(f'  border={warning_dark.border}')
