from __future__ import annotations

from pathlib import Path


class PublicationPNGExporter:
    """Publication export scaffold.

    Future revisions can integrate Plotly image export or matplotlib-based
    rendering while preserving deterministic CI-safe behavior.
    """

    def export_placeholder(self, output_dir: str | Path) -> list[Path]:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)

        placeholder = path / "publication_export_placeholder.txt"
        placeholder.write_text(
            "PNG export scaffolding active.\n",
            encoding="utf-8",
        )

        return [placeholder]
