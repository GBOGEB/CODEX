#!/usr/bin/env python3
"""CI drift guard for the MASTER Contract Workbench YAML SSOT.

The repository intentionally does not commit generated derivatives. This guard
therefore prevents drift by rejecting tracked derivative payloads and proving the
SSOT can produce a deterministic, hash-manifested derivative set on demand.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.contract_workbench.generator import DEFAULT_CONTRACT, DEFAULT_SCHEMA, generate_outputs, load_contract, validate_contract

DERIVATIVE_ROOTS = (
    Path("MASTER_input/generated"),
    Path("MASTER_input/checkpoints"),
)
ALLOWED_TRACKED_NAMES = {".gitignore", ".gitkeep"}
DEFAULT_DETERMINISTIC_GENERATED_AT = "20260605T000000Z"


def _tracked_derivative_payloads() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", *(str(root) for root in DERIVATIVE_ROOTS)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payloads = []
    for line in result.stdout.splitlines():
        if Path(line).name not in ALLOWED_TRACKED_NAMES:
            payloads.append(line)
    return payloads


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _workspace_path(portable_ref: str) -> Path:
    return ROOT / "MASTER_input" / portable_ref


def _workspace_manifest_path(contract: dict[str, object]) -> Path:
    contract_id = str(contract.get("metadata", {}).get("contract_id", "MASTER-CW"))
    return _workspace_path(f"generated/reports/{contract_id}.manifest.json")


def _comparison_generated_at(contract: dict[str, object]) -> str:
    manifest_path = _workspace_manifest_path(contract)
    if not manifest_path.exists():
        return DEFAULT_DETERMINISTIC_GENERATED_AT
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    generated_at = manifest.get("generated_at")
    if not isinstance(generated_at, str) or not generated_at:
        raise ValueError(f"Existing manifest {manifest_path} does not define a generated_at timestamp")
    return generated_at


def _workspace_derivative_drifts(expected_manifest: dict[str, object], contract: dict[str, object]) -> list[str]:
    outputs = expected_manifest.get("outputs", {})
    output_hashes = expected_manifest.get("output_hashes", {})
    if not isinstance(outputs, dict) or not isinstance(output_hashes, dict):
        return ["manifest missing outputs or output_hashes mappings"]

    existing_names = [name for name, portable_ref in outputs.items() if _workspace_path(str(portable_ref)).exists()]
    if not existing_names:
        return []

    drifts: list[str] = []
    manifest_path = _workspace_manifest_path(contract)
    if not manifest_path.exists():
        drifts.append(f"missing existing derivative manifest: {manifest_path.relative_to(ROOT)}")
    for name, portable_ref in outputs.items():
        path = _workspace_path(str(portable_ref))
        if not path.exists():
            drifts.append(f"missing existing derivative payload: {portable_ref}")
            continue
        actual_hash = _sha256(path)
        expected_hash = str(output_hashes.get(name, ""))
        if actual_hash != expected_hash:
            drifts.append(f"hash drift for {portable_ref}: expected {expected_hash}, got {actual_hash}")
    return drifts


def _generate_to(base: Path, contract: Path, schema: Path, generated_at: str) -> dict[str, object]:
    outputs = generate_outputs(
        contract_path=contract,
        schema_path=schema,
        output_dir=base / "generated",
        checkpoint_dir=base / "checkpoints",
        generated_at=generated_at,
    )
    missing = [name for name, path in outputs.items() if not Path(path).exists()]
    if missing:
        raise RuntimeError(f"Missing generated outputs: {missing}")
    return json.loads(Path(outputs["manifest"]).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate MASTER Contract Workbench SSOT and derivative policy.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    contract = load_contract(args.contract)
    validate_contract(contract)

    payloads = _tracked_derivative_payloads()
    if payloads:
        print("Generated derivative payloads must not be tracked:")
        for payload in payloads:
            print(f"  - {payload}")
        return 1

    generated_at = _comparison_generated_at(contract)

    with tempfile.TemporaryDirectory(prefix="contract-workbench-") as tmp:
        tmp_path = Path(tmp)
        first_manifest = _generate_to(tmp_path / "first", args.contract, args.schema, generated_at)
        second_manifest = _generate_to(tmp_path / "second", args.contract, args.schema, generated_at)
        if first_manifest != second_manifest:
            print("Generated derivative manifests are not deterministic:")
            print(json.dumps({"first": first_manifest, "second": second_manifest}, indent=2))
            return 1

        drifts = _workspace_derivative_drifts(first_manifest, contract)
        if drifts:
            print("Existing generated derivatives drift from the YAML SSOT:")
            for drift in drifts:
                print(f"  - {drift}")
            return 1

    print("MASTER Contract Workbench SSOT validation and deterministic manifest drift guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
