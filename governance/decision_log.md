# Runtime Governance Decision Log

## W007-DEC-001: Use static-first dashboard foundation

- **Date:** 2026-06-05
- **Decision:** Implement GitHub Pages dashboards as dependency-free static HTML with placeholder metrics.
- **Rationale:** The ChatGPT GitHub connector became unstable during W007, so the repository needs a direct, deterministic foundation that does not depend on runtime services.
- **Consequence:** W008 should add a generator that reads checked-in SSOT YAML and updates the static dashboard views.

## W007-DEC-002: Add lowercase `ssot/` runtime models

- **Date:** 2026-06-05
- **Decision:** Add W007 dashboard runtime models under `ssot/` while leaving existing uppercase `SSOT/` files untouched.
- **Rationale:** The handoff explicitly names lowercase `ssot/` deliverables, and the repository already contains uppercase `SSOT/` assets with different purposes.
- **Consequence:** W008 should normalize or alias SSOT conventions across automation.

## W007-DEC-003: Treat missing review package artifacts as open risk

- **Date:** 2026-06-05
- **Decision:** Do not recreate historical review artifacts that were not discoverable; record them as gaps in audit and completion reporting.
- **Rationale:** The handoff instructed not to recreate existing artifacts.
- **Consequence:** Release governance must either restore those artifacts at expected paths or register authoritative alternate locations.
