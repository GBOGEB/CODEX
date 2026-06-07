#!/usr/bin/env python3
"""CI drift guard for the MASTER Contract Workbench YAML SSOT.

The repository intentionally does not commit generated derivatives. This guard
therefore prevents drift by rejecting tracked derivative payloads and proving the
SSOT can produce a deterministic, hash-manifested derivative set on demand.
"""

from __future__ import annotations

import argparse
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
DETERMINISTIC_GENERATED_AT = "20260605T000000Z"


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


def _generate_to(base: Path, contract: Path, schema: Path) -> dict[str, str]:
    outputs = generate_outputs(
        contract_path=contract,
        schema_path=schema,
        output_dir=base / "generated",
        checkpoint_dir=base / "checkpoints",
        generated_at=DETERMINISTIC_GENERATED_AT,
    )
    missing = [name for name, path in outputs.items() if not Path(path).exists()]
    if missing:
        raise RuntimeError(f"Missing generated outputs: {missing}")
    manifest = json.loads(Path(outputs["manifest"]).read_text(encoding="utf-8"))
    return manifest["output_hashes"]


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

    with tempfile.TemporaryDirectory(prefix="contract-workbench-") as tmp:
        tmp_path = Path(tmp)
        first_hashes = _generate_to(tmp_path / "first", args.contract, args.schema)
        second_hashes = _generate_to(tmp_path / "second", args.contract, args.schema)
        if first_hashes != second_hashes:
            print("Generated derivative hashes are not deterministic:")
            print(json.dumps({"first": first_hashes, "second": second_hashes}, indent=2))
            return 1

    print("MASTER Contract Workbench SSOT validation and deterministic derivative drift guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
