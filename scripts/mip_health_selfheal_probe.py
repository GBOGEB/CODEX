#!/usr/bin/env python3
"""Prove a fail-closed MIP health/self-heal loop on a transient fixture, stdlib only.

Repo-local probe named by ``health_probe`` in ``MIP/mip_surface.json``. It
reuses CODEX's existing runtime self-heal primitive
(``docs/wave_packages/runtime/self_healing_runtime.py:repair_missing_artifacts``)
but rebinds it to a temporary directory, so the source checkout is never
touched. It counts missing runtime artifacts before and after the repair,
checks the repaired files byte for byte, and binds the sanitized result to the
exact repository SHA.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PRIMITIVE = ROOT / "docs" / "wave_packages" / "runtime" / "self_healing_runtime.py"
PRIMITIVE_NAME = (
    "docs.wave_packages.runtime.self_healing_runtime.repair_missing_artifacts"
)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args],
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_primitive():
    spec = importlib.util.spec_from_file_location("mip_selfheal_primitive", PRIMITIVE)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {PRIMITIVE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def missing(paths: list[Path]) -> int:
    return sum(1 for path in paths if not (path.is_file() and path.stat().st_size > 0))


def _recompute_verification(receipt: dict[str, Any]) -> None:
    checks = receipt["checks"]
    failed = sorted(name for name, passed in checks.items() if not passed)
    verification = "PASS" if not failed else "FAIL"
    receipt["failed_checks"] = failed
    receipt["verification"] = verification
    receipt["return_state"] = "IMPROVED" if verification == "PASS" else "REGRESSED"


def build_receipt() -> dict[str, Any]:
    exact_sha = git("rev-parse", "HEAD")
    checkout_before = git("status", "--porcelain")

    module = load_primitive()
    canonical = dict(module.MINIMAL_ARTIFACTS)
    with tempfile.TemporaryDirectory(prefix="mip-health-selfheal-") as temp:
        fixture_root = Path(temp)
        # Rebind the primitive to the fixture: same artifacts, transient paths.
        module.ROOT = fixture_root
        module.MINIMAL_ARTIFACTS = {
            fixture_root / path.relative_to(ROOT): content
            for path, content in canonical.items()
        }
        targets = list(module.MINIMAL_ARTIFACTS)

        before_metric = missing(targets)
        report = module.repair_missing_artifacts()
        after_metric = missing(targets)
        repaired_exact = all(
            path.read_text(encoding="utf-8") == content
            for path, content in module.MINIMAL_ARTIFACTS.items()
            if path.is_file()
        )
        rerun = module.repair_missing_artifacts()
        fixture_digest = sha256_bytes(
            b"".join(path.read_bytes() for path in sorted(targets) if path.is_file())
        )

    checkout_after = git("status", "--porcelain")
    delta = after_metric - before_metric
    source_checkout_unchanged = checkout_before == "" and checkout_after == ""

    checks = {
        "before_metric_observed": before_metric == len(canonical) > 0,
        "repair_reported": report.get("status") == "repair-complete"
        and report.get("repair_count") == before_metric,
        "after_metric_closed": after_metric == 0,
        "after_fixture_exact": repaired_exact,
        "repair_idempotent": rerun.get("repair_count") == 0
        and len(rerun.get("existing", [])) == len(canonical),
        "improvement_delta": delta == -len(canonical),
        "source_checkout_clean_before": checkout_before == "",
        "source_checkout_clean_after_repair": checkout_after == "",
        "source_checkout_unchanged": source_checkout_unchanged,
    }

    receipt: dict[str, Any] = {
        "schema_version": "0.1",
        "program": "MIP",
        "diagnostic": "repo_health_selfheal",
        "verification": "FAIL",
        "exact_sha": exact_sha,
        "execution_context": "transient_controlled_fixture",
        "source_primitive": PRIMITIVE_NAME,
        "repair_class": "missing_runtime_artifact",
        "before_metric": before_metric,
        "after_metric": after_metric,
        "delta": delta,
        "metric_direction": "lower_is_better",
        "return_state": "REGRESSED",
        "source_checkout_unchanged": source_checkout_unchanged,
        "fixture_after_sha256": fixture_digest,
        "checks": checks,
        "failed_checks": [],
        "raw_receipt_retention": "transient_runner_only",
        "promotion_authority": False,
    }
    _recompute_verification(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run transient MIP health/self-heal proof."
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    receipt = build_receipt()

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    checkout_final = git("status", "--porcelain")
    receipt["checks"]["source_checkout_clean_after_output"] = checkout_final == ""
    receipt["source_checkout_unchanged"] = (
        receipt["source_checkout_unchanged"] and checkout_final == ""
    )
    receipt["checks"]["source_checkout_unchanged"] = receipt[
        "source_checkout_unchanged"
    ]
    _recompute_verification(receipt)

    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if receipt["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
