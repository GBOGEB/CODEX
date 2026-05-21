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

    def __init__(self, config_path: str | None = None) -> None:
        if config_path is None:
            # Resolve relative to package root
            package_root = Path(__file__).parent.parent.parent
            self.config_path = package_root / 'themes' / 'semantic_cards.yaml'
        else:
            self.config_path = Path(config_path)
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        with self.config_path.open('r', encoding='utf-8') as handle:
            data = yaml.safe_load(handle)
            if data is None or not isinstance(data, dict):
                raise ValueError(
                    f"Invalid YAML in {self.config_path}: expected dict, got {type(data).__name__}"
                )
            return data

    def resolve(self, semantic_type: str, mode: str) -> SemanticCardTheme:
        semantic_cards = self.data.get('semantic_cards')
        if semantic_cards is None:
            raise ValueError("Missing 'semantic_cards' key in theme configuration")
        
        if semantic_type not in semantic_cards:
            available = ', '.join(sorted(semantic_cards.keys()))
            raise ValueError(
                f"Unknown semantic_type '{semantic_type}'. Available types: {available}"
            )
        
        type_config = semantic_cards[semantic_type]
        if mode not in type_config:
            available = ', '.join(sorted(type_config.keys()))
            raise ValueError(
                f"Unknown mode '{mode}' for semantic_type '{semantic_type}'. Available modes: {available}"
            )
        
        entry = type_config[mode]

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
