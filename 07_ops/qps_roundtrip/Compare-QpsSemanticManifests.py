#!/usr/bin/env python3
"""Compare two QPS semantic manifests and emit a deterministic receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

VOLATILE_TOP_LEVEL = {
    "generated_utc",
    "artifact_path",
    "artifact_sha256",
    "source_path",
    "source_filename",
}


def canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: canonicalize(v)
            for k, v in sorted(value.items())
            if k not in VOLATILE_TOP_LEVEL
        }
    if isinstance(value, list):
        return [canonicalize(v) for v in value]
    return value


def sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def diff(a: Any, b: Any, path: str = "$", out: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if out is None:
        out = []
    if type(a) is not type(b):
        out.append({"path": path, "left": a, "right": b, "reason": "type_or_value"})
        return out
    if isinstance(a, dict):
        keys = sorted(set(a) | set(b))
        for key in keys:
            child = f"{path}.{key}"
            if key not in a:
                out.append({"path": child, "left": None, "right": b[key], "reason": "missing_left"})
            elif key not in b:
                out.append({"path": child, "left": a[key], "right": None, "reason": "missing_right"})
            else:
                diff(a[key], b[key], child, out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append({"path": path, "left_length": len(a), "right_length": len(b), "reason": "length"})
        for index, (left, right) in enumerate(zip(a, b)):
            diff(left, right, f"{path}[{index}]", out)
    elif a != b:
        out.append({"path": path, "left": a, "right": b, "reason": "value"})
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-difference", action="store_true")
    args = parser.parse_args()

    left_raw = json.loads(args.left.read_text(encoding="utf-8-sig"))
    right_raw = json.loads(args.right.read_text(encoding="utf-8-sig"))
    left = canonicalize(left_raw)
    right = canonicalize(right_raw)
    differences = diff(left, right)

    receipt = {
        "schema_version": 1,
        "control_id": "GOV-001",
        "left_manifest": str(args.left),
        "right_manifest": str(args.right),
        "left_semantic_sha256": sha256_json(left),
        "right_semantic_sha256": sha256_json(right),
        "semantic_match": not differences,
        "difference_count": len(differences),
        "differences": differences,
        "result": "PASS" if not differences else "DIFFERENT",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))

    if differences and not args.allow_difference:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
