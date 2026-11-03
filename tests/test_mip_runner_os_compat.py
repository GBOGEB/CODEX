"""Guard Python 3.9 and pinned Playwright against ubuntu-latest alias drift."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RunnerCompatibilityTests(unittest.TestCase):
    def test_security_python39_stays_on_supported_ubuntu2404(self):
        source = (ROOT / ".github/workflows/security-scan.yml").read_text(encoding="utf-8")
        self.assertIn("os: [ubuntu-24.04, windows-latest, macos-latest]", source)
        self.assertIn("python-version: ['3.9', '3.10', '3.11', '3.12']", source)
        self.assertNotIn("ubuntu-latest", source)
        self.assertIn("ruff==0.16.6", source)

    def test_pinned_browser_runtime_uses_supported_runner(self):
        source = (ROOT / ".github/workflows/site-html-qa.yml").read_text(encoding="utf-8")
        self.assertIn("runs-on: ubuntu-24.04", source)
        self.assertNotIn("ubuntu-latest", source)
        self.assertIn("playwright==1.56.0", source)
        self.assertIn("python -m playwright install --with-deps chromium", source)


if __name__ == "__main__":
    unittest.main()
