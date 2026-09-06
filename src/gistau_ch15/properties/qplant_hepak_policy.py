"""QPLANT-specific helium property governance for CODEX/KEB.

This policy is deliberately narrower than the generic HEPAK adapter:
- 2.0 K <= T <= 4.5 K inclusive: HEPAK is mandatory and governing.
- outside that band: CoolProp may govern unless a narrower child rule applies.
- NIST is validation/reference only.
- missing in-band HEPAK evidence is BLOCKING_MUST_EXECUTE; no fallback promotion.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

HEPAK_MIN_K = 2.0
HEPAK_MAX_K = 4.5


class QplantHepakPolicyError(ValueError):
    pass


def governing_provider_for_temperature(temperature_K: float) -> str:
    t = float(temperature_K)
    return "HEPAK" if HEPAK_MIN_K <= t <= HEPAK_MAX_K else "COOLPROP"


def validate_governing_source(*, temperature_K: float, provider: str, authority_role: str) -> None:
    expected = governing_provider_for_temperature(temperature_K)
    p = provider.upper()
    role = authority_role.upper()
    if role != "GOVERNING":
        return
    if expected == "HEPAK" and p != "HEPAK":
        raise QplantHepakPolicyError(
            f"QPLANT_HEPAK_REQUIRED: T={temperature_K} K is inside 2.0-4.5 K inclusive; got governing provider={provider}"
        )
    if p == "NIST":
        raise QplantHepakPolicyError("QPLANT_NIST_REFERENCE_ONLY: NIST cannot be governing runtime provider")


@dataclass(frozen=True)
class ChildArtifactPin:
    repository: str
    pr_number: int
    head_sha: str
    artifact_path: str
    artifact_blob_sha: str
    artifact_sha256: str

    def validate(self) -> None:
        if self.repository != "GBOGEB/cryoplant-project":
            raise QplantHepakPolicyError("unexpected child repository")
        if self.pr_number <= 0:
            raise QplantHepakPolicyError("child PR number must be positive")
        if len(self.head_sha) != 40:
            raise QplantHepakPolicyError("child head SHA must be a 40-character git SHA")
        path = PurePosixPath(self.artifact_path)
        if path.is_absolute() or ".." in path.parts:
            raise QplantHepakPolicyError("child artifact path must be repository-relative")
        if len(self.artifact_blob_sha) != 40:
            raise QplantHepakPolicyError("child artifact blob SHA must be a 40-character git blob SHA")
        if len(self.artifact_sha256) != 64:
            raise QplantHepakPolicyError("child artifact SHA256 must be a 64-character digest")


def fail_closed_receipt_status(receipt_available: bool) -> str:
    return "GOVERNING_RECEIPT_AVAILABLE" if receipt_available else "BLOCKING_MUST_EXECUTE"
