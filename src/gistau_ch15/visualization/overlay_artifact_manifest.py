from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

MANIFEST_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class OverlayArtifactRecord:
    """Manifest entry for one generated overlay artifact."""

    key: str
    path: str
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class OverlayArtifactManifest:
    """Typed representation of generated overlay manifest payload."""

    schema_version: str
    artifact_count: int
    artifacts: list[OverlayArtifactRecord]


class OverlayArtifactManifestBuilder:
    """Build, validate, load and persist generated overlay artifact metadata."""

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
                rel_path = path.relative_to(base).as_posix()
            except ValueError as e:
                raise ValueError(
                    f"Artifact {path} is outside root {base}. "
                    "Provide an explicit root parameter or ensure all artifacts "
                    "are under the current working directory."
                ) from e
            records.append(
                OverlayArtifactRecord(
                    key=path.stem,
                    path=rel_path,
                    sha256=hashlib.sha256(payload).hexdigest(),
                    size_bytes=len(payload),
                )
            )

        return sorted(records, key=lambda r: r.path)

    def build_manifest(
        self,
        artifacts: list[Path],
        *,
        root: Path | None = None,
        schema_version: str = MANIFEST_SCHEMA_VERSION,
    ) -> OverlayArtifactManifest:
        records = self.build_records(artifacts, root=root)
        return OverlayArtifactManifest(
            schema_version=schema_version,
            artifact_count=len(records),
            artifacts=records,
        )

    def to_payload(self, manifest: OverlayArtifactManifest) -> dict:
        return {
            "schema_version": manifest.schema_version,
            "artifact_count": manifest.artifact_count,
            "artifacts": [asdict(record) for record in manifest.artifacts],
        }

    def validate_manifest(self, manifest: OverlayArtifactManifest) -> None:
        if manifest.schema_version != MANIFEST_SCHEMA_VERSION:
            raise ValueError("Unsupported overlay manifest schema version")
        if manifest.artifact_count != len(manifest.artifacts):
            raise ValueError("artifact_count must match artifacts length")
        paths = [record.path for record in manifest.artifacts]
        if len(paths) != len(set(paths)):
            raise ValueError("Manifest contains duplicate artifact paths")

    def parse_payload(self, payload: dict) -> OverlayArtifactManifest:
        artifacts_payload = payload.get("artifacts")
        if not isinstance(artifacts_payload, list):
            raise ValueError("Manifest artifacts field must be a list")
        
        records = []
        for idx, item in enumerate(artifacts_payload):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Artifact at index {idx} must be a dict, got {type(item).__name__}"
                )
            try:
                records.append(OverlayArtifactRecord(**item))
            except TypeError as e:
                raise ValueError(
                    f"Artifact at index {idx} has invalid fields: {e}"
                ) from e
        
        manifest = OverlayArtifactManifest(
            schema_version=str(payload.get("schema_version", "")),
            artifact_count=int(payload.get("artifact_count", -1)),
            artifacts=records,
        )
        self.validate_manifest(manifest)
        return manifest

    def load_manifest(self, manifest_path: str | Path) -> OverlayArtifactManifest:
        payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        return self.parse_payload(payload)

    def write_manifest(
        self,
        artifacts: list[Path],
        output_path: str | Path,
        *,
        root: Path | None = None,
    ) -> Path:
        manifest = self.build_manifest(artifacts, root=root)
        self.validate_manifest(manifest)

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_payload(manifest), indent=2) + "\n",
            encoding="utf-8",
        )
        return path
