"""Regression guard for source-declared minimum safe transitive Python versions.

The native OSV scan must independently decide whether vulnerabilities clear.
This test only rejects removal/weakening of source minimums; it cannot grant
security, review, or merge-admission credit.
"""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def has_secure_floor(requirements: str, package: str, minimum: tuple[int, ...]) -> bool:
    matches = []
    for raw in requirements.splitlines():
        line = raw.split("#", 1)[0].strip()
        parsed = re.match(r"^([A-Za-z0-9_.-]+)(.*)$", line)
        if not parsed or parsed.group(1).casefold().replace("_", "-") != package.casefold():
            continue
        matches.append(parsed.group(2))
    if len(matches) != 1:
        return False
    clauses = matches[0]
    if "==" in clauses or "<=" in clauses:
        return False
    lower_bounds = re.findall(r"(?:^|,)\s*>=\s*(\d+(?:\.\d+)+)", clauses)
    if not lower_bounds:
        return False
    return max(tuple(int(part) for part in value.split(".")) for value in lower_bounds) >= minimum


class OsvPythonFloorTests(unittest.TestCase):
    def test_root_requirements_disallow_affected_python_versions(self):
        text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertTrue(has_secure_floor(text, "pygments", (2, 20, 0)))
        self.assertTrue(has_secure_floor(text, "idna", (3, 15)))

    def test_pca_engine_has_its_own_secure_floor(self):
        text = (ROOT / "pca_engine" / "requirements.txt").read_text(encoding="utf-8")
        self.assertTrue(has_secure_floor(text, "pygments", (2, 20, 0)))

    def test_legacy_unconstrained_and_pinned_versions_fail_closed(self):
        self.assertFalse(has_secure_floor("pytest>=8.0\n", "pygments", (2, 20, 0)))
        self.assertFalse(has_secure_floor("Pygments==2.9.0\n", "pygments", (2, 20, 0)))
        self.assertFalse(has_secure_floor("Pygments>=2.15.1\n", "pygments", (2, 20, 0)))
        self.assertFalse(has_secure_floor("idna>=3.9\n", "idna", (3, 15)))


if __name__ == "__main__":
    unittest.main()
