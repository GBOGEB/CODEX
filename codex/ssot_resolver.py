"""Compatibility import for the canonical CODEX SSOT resolver.

New consumers should import from ``tools.ssot_resolver``. This module remains
only to avoid breaking existing package imports while resolver penetration is
migrated under W05.
"""
from tools.ssot_resolver import SsotResolutionError, load_manifest, resolve_ssot

# Historical public name retained for compatibility.
SSOTResolutionError = SsotResolutionError

__all__ = [
    "SSOTResolutionError",
    "SsotResolutionError",
    "load_manifest",
    "resolve_ssot",
]
