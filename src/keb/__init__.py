"""KEB (Knowledge Exchange Bridge) client package.

Loads shared governance vocabulary and rules from KEB/governance/ and exposes
them for consumption by other CODEX modules.
"""

from src.keb.keb_client import KebClient

__all__ = ["KebClient"]
