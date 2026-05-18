from __future__ import annotations

from pathlib import Path

from gistau_ch15.visualization.pages_artifact_refresh import (
    PagesArtifactRefresh,
)


def refresh_overlay_artifacts() -> list[Path]:
    """Refresh GitHub Pages-visible overlay artifacts."""

    return PagesArtifactRefresh().refresh()


if __name__ == "__main__":
    refresh_overlay_artifacts()
