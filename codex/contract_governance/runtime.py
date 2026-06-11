"""Runtime verification helpers for the Contract Governance Workbench."""

from __future__ import annotations

import re

MIN_PEP660_PIP = (21, 3)


def parse_pip_major_minor(version: str) -> tuple[int, int]:
    """Return the leading pip major/minor version needed for PEP 660 checks."""

    match = re.match(r"^(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"unable to parse pip version for PEP 660 check: {version}")
    return int(match.group(1)), int(match.group(2))


def ensure_pep660_pip_version(version: str) -> None:
    """Fail if pip is too old for editable installs through PEP 660."""

    if parse_pip_major_minor(version) < MIN_PEP660_PIP:
        raise RuntimeError(
            "pip>=21.3 is required for PEP 660 editable installs; "
            f"found pip=={version}"
        )
