from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
release = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))
ssot_text = (ROOT / "ssot" / "domain" / "repo" / "release.yaml").read_text(encoding="utf-8")
checks = {
    "version_json_present": bool(release.get("version")),
    "release_program_declared": "release_program: CODEX_2_0" in ssot_text,
    "target_2_0_declared": 'target_major_version: "2.0.0"' in ssot_text,
    "promotion_still_gated": "promotion_to_2_0_0_allowed: false" in ssot_text,
    "immutable_manifest_required": "immutable_release_manifest" in ssot_text,
}
status = "PASS" if all(checks.values()) else "FAIL"
out = ROOT / "release" / "CODEX_RC_PREFLIGHT.json"
out.parent.mkdir(exist_ok=True)
payload = {"schema_version":"1.0","probe":"CODEX_RC_PREFLIGHT","status":status,"checks":checks,"current_version":release.get("version"),"target_version":"2.0.0"}
out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
raise SystemExit(0 if status == "PASS" else 1)
