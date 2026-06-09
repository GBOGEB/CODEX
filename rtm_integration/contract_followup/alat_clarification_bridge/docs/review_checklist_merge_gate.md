# ALaT Clarification Bridge — Review Checklist and Merge Gate

## Draft PR gate

Keep the PR in Draft until all of the following exist and run in CI:

- SSOT validation tool: `tools/validate_ssot.py`
- Artifact generator: `tools/generate_bridge.py`
- CI workflow: `.github/workflows/build-clarification-bridge.yml`

## Required validation checks

- [ ] YAML loads successfully.
- [ ] Exactly Q3, Q4, and Q5 are present.
- [ ] Each parent question has at least one RTM link.
- [ ] Each parent question has stakeholder ownership.
- [ ] DBE actions exist for W and S nominal, transient, and abnormal handover boundaries.
- [ ] Generated Markdown artifact exists.
- [ ] Generated HTML artifact exists.
- [ ] Generated review checklist Markdown artifact exists.
- [ ] Generated stakeholder review and management summary artifacts exist from their templates.
- [ ] Generated Excel artifact exists when `openpyxl` is available.

## Bidder-facing answer gate

- [ ] Preserve the Q3/Q4/Q5 route.
- [ ] Use short bullet roll-ups.
- [ ] Keep internal sub-question numbers for SCK traceability only.
- [ ] Do not duplicate pressure, temperature, or flow values controlled by input/interface tables.
- [ ] Do not reference slides or internal preparation slide numbers in bidder-facing outputs.

## RTM and OFFER_list gate

- [ ] Confirm every `rtm_links` entry maps to `RTM_LINKS.yaml`.
- [ ] Confirm every `offer_actions` entry maps to `OFFER_REGISTER.yaml`.
- [ ] Confirm stakeholder owners accept open actions or update status before merge.


## Current PR status

This bridge remains Draft until GitHub CI is green and stakeholder sign-off closes the route preservation, W/S DBE confirmation, and bidder-facing exclusion checks. The placeholders in the generated stakeholder review are intentional review controls, not completed approvals.

## Pre-ready external blockers

The code-level checks are intentionally separate from the final merge decision. Before changing the PR from Draft to Ready:

- [ ] Confirm the GitHub Actions run for `.github/workflows/build-clarification-bridge.yml` is green on the PR branch.
- [ ] Confirm the CI run produced `alat_clarification_bridge.xlsx` after installing `openpyxl`.
- [ ] Confirm `tests/test_alat_clarification_bridge.py` is present in the PR file set and was executed by CI.
- [ ] Close stakeholder sign-offs for route preservation, W/S DBE confirmation, and bidder-facing exclusion.
- [ ] Post the completed status comment on the live PR if the automation environment could not update GitHub directly.
