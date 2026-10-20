"""Every OSV ignore is a documented false positive: it names the fixed version, the
requirements floor in the same directory excludes every affected version, and it expires."""
from __future__ import annotations

import datetime as dt
import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIGS = sorted(p for p in REPO_ROOT.glob("**/osv-scanner.toml") if ".git" not in p.parts and "node_modules" not in p.parts)
MAX_DAYS = 184


def _version(text: str) -> tuple[int, ...]:
    parts = [int(x) for x in re.findall(r"\d+", text)[:3]]
    return tuple(parts + [0] * (3 - len(parts)))


def _floors(requirements: Path) -> dict[str, tuple[int, ...]]:
    floors: dict[str, tuple[int, ...]] = {}
    for line in requirements.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([A-Za-z0-9_.-]+)\s*>=\s*([0-9][0-9.]*)", line)
        if m:
            name = m.group(1).lower()
            floors[name] = max(floors.get(name, ()), _version(m.group(2)))
    return floors


def test_configs_exist_for_the_scanned_manifests():
    assert {p.parent for p in CONFIGS} >= {REPO_ROOT, REPO_ROOT / "pca_engine"}


def test_every_ignore_is_excluded_by_the_local_requirements_floor():
    for cfg in CONFIGS:
        floors = _floors(cfg.parent / "requirements.txt")
        for entry in tomllib.loads(cfg.read_text(encoding="utf-8")).get("IgnoredVulns", []):
            package = entry["reason"].split(":", 1)[0].strip().lower()
            fixed = re.search(r"fixed in ([0-9][0-9.]*[0-9])", entry["reason"])
            assert fixed, f"{cfg}: {entry['id']} reason must read '<package>: ... fixed in X ...'"
            assert package in floors, f"{cfg}: no floor for {package}"
            assert floors[package] >= _version(fixed.group(1)), f"{cfg}: {package} floor below fix for {entry['id']}"


def test_every_ignore_expires_within_six_months():
    today = dt.datetime.now(tz=dt.UTC).date()
    for cfg in CONFIGS:
        for entry in tomllib.loads(cfg.read_text(encoding="utf-8")).get("IgnoredVulns", []):
            until = entry["ignoreUntil"]
            until = until.date() if isinstance(until, dt.datetime) else until
            assert isinstance(until, dt.date), f"{cfg}: {entry['id']} needs ignoreUntil"
            assert (until - today).days <= MAX_DAYS, f"{cfg}: {entry['id']} ignore too long-lived"
