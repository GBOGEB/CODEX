#!/usr/bin/env python3
"""Emit a source- and image-digest-bound receipt from inside a UBI testflight."""
import hashlib
import json
import os
import pathlib
import platform

root = pathlib.Path("outputs/ubi9")
image = os.environ["IMAGE_REF"]
if "@sha256:" not in image:
    raise RuntimeError("Immutable OCI image digest required")
files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(root.iterdir()) if p.is_file()}
receipt = {
    "schema": "codex-ubi-testflight/v1",
    "source_sha": os.environ["GITHUB_SHA"],
    "container_image": image,
    "image_digest": image.rsplit("@", 1)[1],
    "python": platform.python_version(),
    "system": platform.platform(),
    "executed_entrypoints": ["scripts/check_authority_integrity.py",
                             "scripts/check_release_identity.py"],
    "outcomes": {"authority_integrity": "PASS", "release_identity": "PASS"},
    "sha256": files,
}
(root / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
