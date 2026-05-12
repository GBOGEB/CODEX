from pathlib import Path, PurePosixPath

forbidden_patterns = [
    "**/final_final/**",
    "**/latest/**",
    "**/new_dashboard/**",
    "**/dashboard_old/**",
    "**/dashboard_new/**",
    "**/copy*/**",
    "**/backup/**",
    "**/*_old.*",
    "**/*_new.*",
    "**/*_final.*",
    "**/*_latest.*",
]
allowlist = {"output/handover_final"}
violations = []


def matches_forbidden_pattern(path_str: str) -> bool:
    path = PurePosixPath(path_str.lower())
    for pattern in forbidden_patterns:
        normalized_pattern = pattern.lower()
        if normalized_pattern.endswith('/**'):
            base_pattern = normalized_pattern[:-3]
            if path.match(base_pattern) or any(parent.match(base_pattern) for parent in path.parents):
                return True
        elif path.match(normalized_pattern):
            return True
    return False


for p in Path('.').rglob('*'):
    s = str(p).replace('\\', '/')
    if s in allowlist:
        continue
    if matches_forbidden_pattern(s):
        violations.append(s)

if violations:
    raise SystemExit("forbidden ambiguity paths found:\n" + "\n".join(violations[:50]))

print("glob policy check passed")
