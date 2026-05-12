# Backbone Policy

## Protected backbone

The following are canonical and must not be renamed or replaced without explicit migration approval:

```text
docs/index.html
docs/dashboard.html
docs/plots/index.html
tools/losses/src/build_all.py
MANIFEST.json
GLOB_POLICY.md
.github/workflows/pages.yml
```

## Public URL stability

Published URLs are part of the user interface. Do not rename public files unless:

1. a redirect or replacement link is provided;
2. the manifest is updated;
3. the regression page documents the change;
4. link checks pass.

## Canonical promotion

Experimental dashboards may only become canonical after:

```text
[ ] feature parity check
[ ] visual comparison
[ ] data/schema compatibility review
[ ] regression comparison
[ ] stale artifact check
[ ] manifest update
[ ] public URL review
[ ] PR approval
```

## No silent replacement

Never overwrite a verified dashboard with a different semantic dashboard under the same filename without recording the change in:

```text
MANIFEST.json
CHANGELOG.md
docs/regression.html
docs/verification.html
```
