"""Pydantic v2 schema for the ABACUS Contract Governance YAML SSOT."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Audience(str, Enum):
    """Output audience classification for generated artifacts."""

    bidder = "bidder"
    internal = "internal"
    evaluation = "evaluation"


class SourceDocument(BaseModel):
    """Read-only source document mirrored from MASTER_input/."""

    model_config = ConfigDict(extra="forbid")

    doc_id: str = Field(pattern=r"^[A-Z0-9][A-Z0-9_.-]*$")
    title: str = Field(min_length=1)
    master_input_path: str = Field(min_length=1)
    frozen_baseline: bool = True

    @field_validator("master_input_path")
    @classmethod
    def must_be_master_input(cls, value: str) -> str:
        if not value.startswith("MASTER_input/"):
            raise ValueError("source documents must be addressed from MASTER_input/")
        if ".." in PurePosixPath(value).parts:
            raise ValueError("source document paths must not traverse upward")
        return value


class HeaderBinding(BaseModel):
    """Header-name extraction binding with observed position retained for audit."""

    model_config = ConfigDict(extra="forbid")

    header_name: str = Field(min_length=1)
    observed_column: str = Field(pattern=r"^[A-Z]+$")
    observed_index: int = Field(ge=1)


class Requirement(BaseModel):
    """Contract requirement row in the YAML SSOT."""

    model_config = ConfigDict(extra="forbid")

    req_id: str = Field(pattern=r"^REQ-[A-Z0-9_.-]+$")
    title: str = Field(min_length=1)
    text: str = Field(min_length=1)
    source_doc_id: str
    source_section: str = Field(min_length=1)
    audience: Audience = Audience.bidder
    header_bindings: list[HeaderBinding] = Field(default_factory=list)


class GeneratedSheet(BaseModel):
    """Generated workbook sheet contract."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=31)
    audience: Audience = Audience.bidder
    columns: list[str] = Field(min_length=1)


class BuildConfig(BaseModel):
    """Deterministic build settings."""

    model_config = ConfigDict(extra="forbid")

    fixed_docprops_timestamp: datetime
    content_hash_algorithm: Literal["sha256"] = "sha256"

    @field_validator("fixed_docprops_timestamp")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).replace(microsecond=0)


class GovernanceSSOT(BaseModel):
    """Top-level authoritative YAML SSOT."""

    model_config = ConfigDict(extra="forbid")

    ssot_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    package_id: str = Field(pattern=r"^[A-Z0-9][A-Z0-9_.-]*$")
    build: BuildConfig
    source_documents: list[SourceDocument] = Field(min_length=1)
    requirements: list[Requirement] = Field(min_length=1)
    generated_sheets: list[GeneratedSheet] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_references(self) -> "GovernanceSSOT":
        doc_ids = {doc.doc_id for doc in self.source_documents}
        unknown = sorted({req.source_doc_id for req in self.requirements} - doc_ids)
        if unknown:
            raise ValueError(
                f"requirements reference unknown source documents: {unknown}"
            )

        sheet_names = [sheet.name for sheet in self.generated_sheets]
        duplicates = sorted(
            {name for name in sheet_names if sheet_names.count(name) > 1}
        )
        if duplicates:
            raise ValueError(f"duplicate generated sheet names: {duplicates}")
        return self
