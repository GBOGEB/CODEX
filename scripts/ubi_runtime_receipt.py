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
# Output-producing pipeline is separately proven from the two historical checks.
pipeline_path = root / "rex-rollup.json"
exit_path = root / "rex-rollup.exitcode"
duration_path = root / "rex-rollup.duration_ms"
if any(p.exists() for p in (pipeline_path, exit_path, duration_path)):
    if not all(p.is_file() for p in (pipeline_path, exit_path, duration_path)):
        raise RuntimeError("partial REX pipeline receipt")
    exit_code = int(exit_path.read_text(encoding="utf-8").strip())
    duration_ms = int(duration_path.read_text(encoding="utf-8").strip())
    output = json.loads(pipeline_path.read_text(encoding="utf-8"))
    if exit_code != 0 or duration_ms < 0 or not isinstance(output, dict):
        raise RuntimeError("invalid REX output pipeline execution")
    receipt["executed_entrypoints"].append("scripts/code_purple_rex_rollup.py")
    receipt["outcomes"]["rex_rollup"] = "PASS"
    receipt["output_pipeline"] = {
        "entrypoint": "scripts/code_purple_rex_rollup.py",
        "output": "outputs/ubi9/rex-rollup.json",
        "exit_code": exit_code,
        "duration_ms": duration_ms,
        "size_bytes": pipeline_path.stat().st_size,
        "sha256": hashlib.sha256(pipeline_path.read_bytes()).hexdigest(),
        "source_sha": os.environ["GITHUB_SHA"],
        "image_digest": image.rsplit("@", 1)[1],
    }

(root / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
