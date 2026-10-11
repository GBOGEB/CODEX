"""Stage the SPINE-core tree from a PASS receipt (ADR-0002).

Copies exactly the files listed in SPINE_GATE_RECEIPT.json (overlays from
their sanitized source) into --out, verifying every sha256 on the way, and
writes STAGE_RECEIPT.json. Refuses to run on a FAIL receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def stage(root: Path, receipt_path: Path, out: Path) -> int:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("verdict") != "PASS":
        print(f"REFUSED: gate verdict is {receipt.get('verdict')}, not PASS")
        return 2
    if out.exists() and any(out.iterdir()):
        print(f"REFUSED: {out} is not empty")
        return 2
    out.mkdir(parents=True, exist_ok=True)
    mismatches = []
    for f in receipt["files"]:
        src = root / f.get("overlay_source", f["path"])
        data = src.read_bytes()
        if hashlib.sha256(data).hexdigest() != f["sha256"]:
            mismatches.append(f["path"])
            continue
        dst = out / f["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    if mismatches:
        print("FAIL: tree drifted since the gate ran:", *mismatches, sep="\n  ")
        return 1
    stage_receipt = {
        "stage": "SPINE_STAGE",
        "from_gate_receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        "admitted_tree_sha256": receipt["admitted_tree_sha256"],
        "files": len(receipt["files"]),
    }
    (out / "STAGE_RECEIPT.json").write_text(json.dumps(stage_receipt, indent=2) + "\n", encoding="utf-8")
    print(f"STAGED {len(receipt['files'])} files -> {out} (tree {receipt['admitted_tree_sha256'][:12]})")
    return 0


def smoke(root: Path, out: Path, python: str) -> int:
    """Run the manifest's smoke commands inside the staged tree."""
    import yaml

    manifest = yaml.safe_load((root / "spine" / "SPINE_MANIFEST.yaml").read_text(encoding="utf-8"))
    results, failed = [], 0
    for case in manifest.get("smoke") or []:
        argv = shlex.split(case["cmd"])
        if argv and argv[0] == "python":
            argv[0] = python
        proc = subprocess.run(argv, cwd=out / case["cwd"], capture_output=True, text=True, timeout=600)
        passed = proc.returncode == 0
        ok = passed if case.get("expect", "pass") == "pass" else not passed
        failed += not ok
        results.append({"name": case["name"], "expect": case.get("expect", "pass"),
                        "returncode": proc.returncode, "verdict": "PASS" if ok else "FAIL",
                        "tail": (proc.stdout + proc.stderr).strip().splitlines()[-3:]})
        print(f"  {'PASS' if ok else 'FAIL'}  {case['name']}  (rc={proc.returncode}, expect={case.get('expect', 'pass')})")
    if not results:
        print("FAIL: manifest declares no smoke cases (zero tests is a failure, not a pass)")
        failed = 1
    verdict = "PASS" if not failed else "FAIL"
    receipt = out / "STAGE_RECEIPT.json"
    data = json.loads(receipt.read_text(encoding="utf-8"))
    data["smoke"] = {"verdict": verdict, "cases": results}
    receipt.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"SPINE_SMOKE {verdict}: {len(results) - failed}/{len(results)}")
    return 0 if verdict == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=REPO_ROOT)
    ap.add_argument("--receipt", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--smoke", action="store_true", help="run manifest smoke cases in the staged tree")
    ap.add_argument("--python", default=sys.executable, help="interpreter for smoke cases")
    a = ap.parse_args(argv)
    root = a.root.resolve()
    receipt = a.receipt or root / "receipts" / "spine" / "SPINE_GATE_RECEIPT.json"
    rc = stage(root, receipt, a.out.resolve())
    if rc == 0 and a.smoke:
        rc = smoke(root, a.out.resolve(), a.python)
    return rc


if __name__ == "__main__":
    sys.exit(main())
