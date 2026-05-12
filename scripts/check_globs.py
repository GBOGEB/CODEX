from pathlib import Path

forbidden = ["final_final", "latest", "new_dashboard", "dashboard_old", "dashboard_new", "copy", "backup", "_old.", "_new.", "_final.", "_latest."]
allowlist = {"output/handover_final"}
violations = []
for p in Path('.').rglob('*'):
    s = str(p).replace('\\', '/')
    name = p.name.lower()
    if s in allowlist:
        continue
    if any(token in name for token in forbidden):
        violations.append(s)

if violations:
    raise SystemExit("forbidden ambiguity paths found:\n" + "\n".join(violations[:50]))

print("glob policy check passed")
