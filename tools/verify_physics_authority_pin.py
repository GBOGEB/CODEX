"""Verify the ABACUS helium-4 physics authority pin.

Two levels:

* ``meta_checksum`` / ``check_pin`` (no network, no ABACUS checkout): the pin
  is well formed and its ``meta_checksum_sha256`` matches its own content.
* ``verify_checkout`` (needs an ABACUS checkout): HEAD equals the pinned
  commit and every pinned file matches its sha256 (stale-SHA rejection).

Usage:
    python tools/verify_physics_authority_pin.py                 # pin only
    python tools/verify_physics_authority_pin.py --abacus PATH   # + checkout
    python tools/verify_physics_authority_pin.py --write-checksum
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PIN_PATH = REPO_ROOT / "governance" / "physics" / "HE4_PROPERTY_AUTHORITY_PIN.yaml"
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA64 = re.compile(r"^[0-9a-f]{64}$")


class PinError(ValueError):
    pass


def load_pin(path: Path = PIN_PATH) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def meta_checksum(pin: dict[str, Any]) -> str:
    """sha256 over the canonical JSON of commit, pinned file hashes and constants."""
    payload = {
        "commit_sha": pin["authority"]["commit_sha"],
        "pinned_files": sorted(
            ({"path": f["path"], "sha256": f["sha256"]} for f in pin["pinned_files"]),
            key=lambda f: f["path"],
        ),
        "pinned_constants": pin["pinned_constants"],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def check_pin(pin: dict[str, Any]) -> None:
    """Raise PinError if the pin is malformed or its meta checksum is stale."""
    auth = pin.get("authority", {})
    if auth.get("repository") != "GBOGEB/ABACUS":
        raise PinError("authority.repository must be GBOGEB/ABACUS")
    if not _SHA40.match(str(auth.get("commit_sha", ""))):
        raise PinError("authority.commit_sha must be a 40-character git SHA")
    files = pin.get("pinned_files") or []
    if not files:
        raise PinError("pinned_files is empty")
    seen = set()
    for f in files:
        p = f.get("path", "")
        if p.startswith("/") or ".." in Path(p).parts:
            raise PinError(f"pinned path must be repository-relative: {p}")
        if p in seen:
            raise PinError(f"duplicate pinned path: {p}")
        seen.add(p)
        if not _SHA40.match(str(f.get("git_blob_sha", ""))):
            raise PinError(f"{p}: git_blob_sha must be 40 hex characters")
        if not _SHA64.match(str(f.get("sha256", ""))):
            raise PinError(f"{p}: sha256 must be 64 hex characters")
    if pin.get("meta_checksum_sha256") != meta_checksum(pin):
        raise PinError("meta_checksum_sha256 does not match pin content (run --write-checksum)")


def verify_checkout(pin: dict[str, Any], abacus: Path) -> list[str]:
    """Return a list of mismatches between an ABACUS checkout and the pin."""
    problems: list[str] = []
    head = subprocess.run(
        ["git", "-C", str(abacus), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    ).stdout.strip()
    if head != pin["authority"]["commit_sha"]:
        problems.append(f"STALE_SHA: checkout HEAD {head or '(none)'} != pinned {pin['authority']['commit_sha']}")
    for f in pin["pinned_files"]:
        target = abacus / f["path"]
        if not target.is_file():
            problems.append(f"MISSING: {f['path']}")
            continue
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != f["sha256"]:
            problems.append(f"CONTENT_DRIFT: {f['path']} sha256 {digest} != pinned {f['sha256']}")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pin", type=Path, default=PIN_PATH)
    ap.add_argument("--abacus", type=Path, help="path to an ABACUS checkout to verify against the pin")
    ap.add_argument("--write-checksum", action="store_true", help="rewrite meta_checksum_sha256 in the pin")
    args = ap.parse_args(argv)

    pin = load_pin(args.pin)
    if args.write_checksum:
        text = args.pin.read_text(encoding="utf-8")
        new = re.sub(r"(?m)^meta_checksum_sha256: .*$", f"meta_checksum_sha256: {meta_checksum(pin)}", text)
        args.pin.write_text(new, encoding="utf-8")
        pin = load_pin(args.pin)
    try:
        check_pin(pin)
    except PinError as exc:
        print(f"PIN_INVALID: {exc}")
        return 1
    print(f"PIN_OK meta_checksum={pin['meta_checksum_sha256']}")
    if args.abacus:
        problems = verify_checkout(pin, args.abacus)
        for p in problems:
            print(p)
        if problems:
            return 1
        print(f"CHECKOUT_MATCHES_PIN {pin['authority']['commit_sha']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
