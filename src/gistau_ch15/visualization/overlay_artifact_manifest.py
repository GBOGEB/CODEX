from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OverlayArtifactRecord:
    """Manifest entry for one generated overlay artifact."""

    key: str
    path: str
    sha256: str
    size_bytes: int


class OverlayArtifactManifestBuilder:
    """Build and persist manifest metadata for generated overlay artifacts."""

    def build_records(
        self,
        artifacts: list[Path],
        *,
        root: Path | None = None,
    ) -> list[OverlayArtifactRecord]:
        base = (root or Path.cwd()).resolve()
        records: list[OverlayArtifactRecord] = []

        for artifact in artifacts:
            path = Path(artifact).resolve()
            payload = path.read_bytes()
            try:
                record_path = path.relative_to(base).as_posix()
            except ValueError:
                record_path = path.as_posix()
            records.append(
                OverlayArtifactRecord(
                    key=path.stem,
                    path=record_path,
                    sha256=hashlib.sha256(payload).hexdigest(),
                    size_bytes=len(payload),
                )
            )

        return sorted(records, key=lambda r: r.path)

    def write_manifest(
        self,
        artifacts: list[Path],
        output_path: str | Path,
        *,
        root: Path | None = None,
    ) -> Path:
        records = self.build_records(artifacts, root=root)

        payload = {
            "schema_version": "1.0",
            "artifact_count": len(records),
            "artifacts": [record.__dict__ for record in records],
        }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path
