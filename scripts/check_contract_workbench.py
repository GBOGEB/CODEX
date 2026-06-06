#!/usr/bin/env python3
"""CI drift guard for the MASTER Contract Workbench YAML SSOT."""

from __future__ import annotations

import argparse
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
        outputs = generate_outputs(
            contract_path=args.contract,
            schema_path=args.schema,
            output_dir=tmp_path / "generated",
            checkpoint_dir=tmp_path / "checkpoints",
            generated_at="20260605T000000Z",
        )
        missing = [name for name, path in outputs.items() if not Path(path).exists()]
        if missing:
            print(f"Missing generated outputs: {missing}")
            return 1

    print("MASTER Contract Workbench SSOT validation and derivative drift guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
