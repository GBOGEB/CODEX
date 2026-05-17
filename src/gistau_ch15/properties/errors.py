from __future__ import annotations


class PropertyBackendUnavailable(RuntimeError):
    """Raised when a required property backend is not installed or not importable."""
