#!/usr/bin/env python3
"""Build and validate governed identities for generated outward artifacts.

This module is deliberately project-agnostic. Git/source remains authoritative for how an
artifact is built; this tool only creates and validates the release identity needed to bind a
generated binary back to source, build and evidence receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

TOKEN_RE = re.compile(r"^[A-Z0-9][A-Z0-9_-]*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHORT_SHA_RE = re.compile(r"^[0-9a-f]{8,40}$")
TS_RE = re.compile(r"^\d{8}T\d{6}Z$")


@dataclass(frozen=True)
class ArtifactIdentity:
    artifact_id: str
    theme: str
    artifact: str
    artifact_type: str
    version: str
    timestamp_utc: str
    source_repository: str
    source_commit: str
    source_paths: list[str]
    build_id: str
    input_ssot_hashes: list[str]
    evidence_receipts: list[str]
    semantic_hash: str | None
    filename: str
    sha256: str | None
    bytes: int | None
    previous_release: str | None


def _token(value: str, field: str) -> str:
    token = value.strip().upper().replace(" ", "_")
    if not TOKEN_RE.fullmatch(token):
        raise ValueError(f"invalid {field}: {value!r}")
    return token


def normalize_version(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("version must not be empty")
    return value if value.lower().startswith("v") else f"v{value}"


def normalize_timestamp(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if not TS_RE.fullmatch(value):
        raise ValueError("timestamp must be UTC YYYYMMDDTHHMMSSZ")
    return value


def validate_commit(commit: str) -> str:
    commit = commit.strip().lower()
    if not SHA_RE.fullmatch(commit):
        raise ValueError("source_commit must be a 40-character lowercase Git SHA")
    return commit


def validate_hashes(values: Iterable[object], field: str) -> list[str]:
    result: list[str] = []
    for raw in values:
        value = str(raw).strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError(f"{field} entries must be lowercase SHA-256 values")
        result.append(value)
    return result


def build_filename(
    *, theme: str, artifact: str, artifact_type: str, version: str,
    timestamp_utc: str, source_commit: str, extension: str,
) -> str:
    theme = _token(theme, "theme")
    artifact = _token(artifact, "artifact")
    artifact_type = _token(artifact_type, "artifact_type")
    version = normalize_version(version)
    timestamp_utc = normalize_timestamp(timestamp_utc)
    source_commit = validate_commit(source_commit)
    extension = extension.strip().lower().lstrip(".")
    if not re.fullmatch(r"[a-z0-9.]+", extension):
        raise ValueError("invalid extension")
    return (
        f"QPS__{theme}__{artifact}__{artifact_type}__{version}__"
        f"{timestamp_utc}__{source_commit[:8]}.{extension}"
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def create_identity(args: argparse.Namespace) -> ArtifactIdentity:
    commit = validate_commit(args.source_commit)
    timestamp = normalize_timestamp(args.timestamp)
    filename = build_filename(
        theme=args.theme,
        artifact=args.artifact,
        artifact_type=args.type,
        version=args.version,
        timestamp_utc=timestamp,
        source_commit=commit,
        extension=args.extension,
    )
    file_hash = None
    file_bytes = None
    if args.file:
        path = Path(args.file)
        if not path.is_file():
            raise ValueError(f"artifact file not found: {path}")
        file_hash = sha256_file(path)
        file_bytes = path.stat().st_size

    return ArtifactIdentity(
        artifact_id=args.artifact_id,
        theme=_token(args.theme, "theme"),
        artifact=_token(args.artifact, "artifact"),
        artifact_type=_token(args.type, "artifact_type"),
        version=normalize_version(args.version),
        timestamp_utc=timestamp,
        source_repository=args.source_repository,
        source_commit=commit,
        source_paths=list(args.source_path or []),
        build_id=args.build_id,
        input_ssot_hashes=validate_hashes(args.ssot_hash or [], "ssot_hash"),
        evidence_receipts=list(args.evidence_receipt or []),
        semantic_hash=(
            validate_hashes([args.semantic_hash], "semantic_hash")[0]
            if args.semantic_hash else None
        ),
        filename=filename,
        sha256=file_hash,
        bytes=file_bytes,
        previous_release=args.previous_release,
    )


def validate_identity(data: dict) -> list[str]:
    errors: list[str] = []
    required = [
        "artifact_id", "theme", "artifact", "artifact_type", "version",
        "timestamp_utc", "source_repository", "source_commit", "source_paths",
        "build_id", "input_ssot_hashes", "evidence_receipts", "filename",
    ]
    for key in required:
        if key not in data:
            errors.append(f"missing:{key}")
    if errors:
        return errors

    try:
        commit = validate_commit(str(data["source_commit"]))
        expected = build_filename(
            theme=str(data["theme"]),
            artifact=str(data["artifact"]),
            artifact_type=str(data["artifact_type"]),
            version=str(data["version"]),
            timestamp_utc=str(data["timestamp_utc"]),
            source_commit=commit,
            extension=str(data["filename"]).rsplit(".", 1)[-1],
        )
        if data["filename"] != expected:
            errors.append("filename_identity_mismatch")
        validate_hashes(data.get("input_ssot_hashes", []), "input_ssot_hashes")
        if data.get("semantic_hash"):
            validate_hashes([data["semantic_hash"]], "semantic_hash")
        if data.get("sha256"):
            validate_hashes([data["sha256"]], "sha256")
        if not data.get("source_paths"):
            errors.append("source_paths_empty")
        if not data.get("build_id"):
            errors.append("build_id_empty")
    except ValueError as exc:
        errors.append(str(exc))
    return errors


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create")
    c.add_argument("--artifact-id", required=True)
    c.add_argument("--theme", required=True)
    c.add_argument("--artifact", required=True)
    c.add_argument("--type", required=True)
    c.add_argument("--version", required=True)
    c.add_argument("--timestamp")
    c.add_argument("--source-repository", required=True)
    c.add_argument("--source-commit", required=True)
    c.add_argument("--source-path", action="append")
    c.add_argument("--build-id", required=True)
    c.add_argument("--ssot-hash", action="append")
    c.add_argument("--evidence-receipt", action="append")
    c.add_argument("--semantic-hash")
    c.add_argument("--previous-release")
    c.add_argument("--extension", required=True)
    c.add_argument("--file")
    c.add_argument("--output")

    v = sub.add_parser("validate")
    v.add_argument("manifest")
    return p


def main() -> int:
    args = parser().parse_args()
    if args.command == "create":
        identity = create_identity(args)
        text = json.dumps(asdict(identity), indent=2, sort_keys=True) + "\n"
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            print(text, end="")
        return 0

    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    errors = validate_identity(data)
    result = {"result": "PASS" if not errors else "FAIL", "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
