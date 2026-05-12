from pathlib import Path

forbidden_segment_exact = {
    "final",
    "final_final",
    "latest",
    "new_dashboard",
    "dashboard_old",
    "dashboard_new",
}
forbidden_filename_tokens = {"_old.", "_new.", "_final.", "_latest."}
allowlist = {"output/handover_final"}
MAX_VIOLATIONS_DISPLAYED = 50
violations = []
for p in Path(".").rglob("*"):
    s = str(p).replace("\\", "/")
    name = p.name.lower()
    segments = [part.lower() for part in p.parts if part]
    if s.lower() in allowlist:
        continue
    has_forbidden_segment = any(part in forbidden_segment_exact for part in segments)
    has_copy_segment = any(part.startswith("copy") for part in segments)
    has_backup_segment = any("backup" in part for part in segments)
    has_forbidden_filename = any(token in name for token in forbidden_filename_tokens)
    if (
        has_forbidden_segment
        or has_copy_segment
        or has_backup_segment
        or has_forbidden_filename
    ):
        violations.append(s)

if violations:
    raise SystemExit(
        "forbidden ambiguity paths found:\n"
        + "\n".join(sorted(violations)[:MAX_VIOLATIONS_DISPLAYED])
    )

print("glob policy check passed")
