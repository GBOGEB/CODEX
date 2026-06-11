#!/usr/bin/env bash
set -u

failures=0

section() {
  printf '\n== %s ==\n' "$1"
}

mark_failure() {
  failures=$((failures + 1))
  printf 'ENVIRONMENT-LIMITATION: %s\n' "$1"
}

section "Proxy environment"
python - <<'PY'
import os
from urllib.parse import urlsplit, urlunsplit

keys = sorted(k for k in os.environ if k.lower().endswith("proxy"))
if not keys:
    print("No proxy-related environment variables are set.")

for key in keys:
    value = os.environ[key]
    try:
        parts = urlsplit(value)
        if parts.username or parts.password:
            host = parts.hostname or ""
            if parts.port:
                host = f"{host}:{parts.port}"
            value = urlunsplit((parts.scheme, f"***:***@{host}", parts.path, parts.query, parts.fragment))
    except Exception:
        value = "<unparseable; redacted>"
    print(f"{key}={value}")
PY

section "npm registry configuration"
npm config get registry || mark_failure "Unable to read npm registry configuration."

section "npm registry reachability"
if npm ping --registry=https://registry.npmjs.org/; then
  printf 'npm registry ping passed.\n'
else
  mark_failure "npm registry ping failed; dependency installation may be blocked by proxy/firewall policy."
fi

section "npm package metadata reachability"
if npm view @types/express version --registry=https://registry.npmjs.org/; then
  printf '@types/express metadata lookup passed.\n'
else
  mark_failure "npm package metadata lookup failed for @types/express."
fi

section "GitHub remote reachability"
if git ls-remote https://github.com/GBOGEB/DOCX_RTM_Automation.git refs/heads/main >/dev/null; then
  printf 'GitHub ls-remote passed.\n'
else
  mark_failure "GitHub ls-remote failed; branch/PR verification may be blocked by proxy/firewall policy."
fi

section "Summary"
if [ "$failures" -eq 0 ]; then
  printf 'Network diagnostics passed.\n'
  exit 0
fi

printf 'Network diagnostics found %s environment limitation(s).\n' "$failures"
exit 1
