"""Utility pipeline for packaging conversation artifacts into ZIP archives.

The pipeline is intentionally lightweight so that it can be executed in offline
CI environments.  It scans a source directory for conversation folders,
creates deterministic ZIP archives for every folder and writes a manifest with
metadata about each archive.  A secondary helper combines one or more
manifests into a global index that downstream tooling can consume.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Sequence
import zipfile


@dataclass
class ConversationArchive:
    """Metadata describing an archived conversation."""

    conversation_id: str
    zip_path: str
    file_count: int
    size_bytes: int
    sha256: str


class ZipPipeline:
    """Create ZIP archives and manifest metadata for conversation folders."""

    def __init__(
        self,
        source_root: Path,
        output_root: Path,
        dataset_name: str,
        manifest_name: str = "conversations_manifest.json",
    ) -> None:
        self.source_root = Path(source_root)
        self.output_root = Path(output_root)
        self.dataset_name = dataset_name
        self.manifest_name = manifest_name

    # ------------------------------------------------------------------
    def run(self) -> Path:
        """Run the pipeline and return the manifest path."""

        dataset_output = self.output_root / self.dataset_name
        dataset_output.mkdir(parents=True, exist_ok=True)

        archives: List[ConversationArchive] = []
        for conversation_dir in sorted(self._iter_conversations()):
            archive_path = dataset_output / f"{conversation_dir.name}.zip"
            file_count = self._create_archive(conversation_dir, archive_path)
            sha256 = self.compute_file_hash(archive_path)
            archive = ConversationArchive(
                conversation_id=conversation_dir.name,
                zip_path=str(archive_path.relative_to(dataset_output)),
                file_count=file_count,
                size_bytes=archive_path.stat().st_size,
                sha256=sha256,
            )
            archives.append(archive)

        manifest = {
            "dataset": self.dataset_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_root": str(self.source_root),
            "entries": [asdict(archive) for archive in archives],
        }

        manifest_path = dataset_output / self.manifest_name
        manifest_path.write_text(json.dumps(manifest, indent=2))
        return manifest_path

    # ------------------------------------------------------------------
    def _iter_conversations(self) -> Iterable[Path]:
        for candidate in sorted(self.source_root.iterdir()):
            if candidate.is_dir():
                yield candidate

    # ------------------------------------------------------------------
    def _create_archive(self, conversation_dir: Path, archive_path: Path) -> int:
        files = [p for p in sorted(conversation_dir.rglob("*")) if p.is_file()]
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in files:
                arcname = file_path.relative_to(conversation_dir)
                zf.write(file_path, arcname.as_posix())
        return len(files)

    # ------------------------------------------------------------------
    @staticmethod
    def compute_file_hash(path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    # ------------------------------------------------------------------
    @staticmethod
    def build_global_index(manifest_paths: Sequence[Path], index_path: Path) -> dict:
        datasets = []
        for manifest_path in manifest_paths:
            manifest = json.loads(Path(manifest_path).read_text())
            entries = manifest.get("entries", [])
            total_size = sum(entry.get("size_bytes", 0) for entry in entries)
            dataset_info = {
                "dataset": manifest.get("dataset"),
                "manifest_path": str(manifest_path),
                "entry_count": len(entries),
                "total_size_bytes": total_size,
                "manifest_sha256": ZipPipeline.compute_file_hash(Path(manifest_path)),
            }
            datasets.append(dataset_info)

        index = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "datasets": datasets,
        }

        index_path = Path(index_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(json.dumps(index, indent=2))
        return index


__all__ = ["ZipPipeline", "ConversationArchive"]
