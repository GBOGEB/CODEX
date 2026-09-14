# A9.1 Governance Execution

## State

A9.1 is a controlled governance mutation of the existing A9 publication contract. It does not introduce a second renderer or semantic authority layer.

The governing pull request is `PR-694`, classified as:

- `WAVE: W009`
- `SPRINT: S9-P2`
- `DOMAIN: EXECUTION_GOVERNANCE_INFRASTRUCTURE`
- `TYPE: GOVERNANCE`
- `CRITICALITY: HIGH`
- `TOPOLOGY IMPACT: NO`
- `SCHEMA MUTATION: CONTROLLED`

## First red

The first PR event was emitted while the pull-request body still contained the temporary placeholder `PR-ID: TBD`.

W003 therefore failed at `Run governance parser on PR metadata`. The mandatory governance schema requires `PR-ID` to match `^PR-[0-9]{3}$`.

This was a PR-metadata admission defect. The A9.1 publication implementation was not the failing surface; the same head's `ABACUS Multi-Format Publication` lane completed successfully.

## Repair

The PR body now declares the exact identifier:

`PR-ID: PR-694`

No hosted-publication claim is promoted from the pre-repair event. This trace commit intentionally re-enters exact-head CI after the corrected PR metadata exists in the GitHub event payload.

## Exact-head re-entry requirement

The repaired head must independently prove, at minimum:

1. W003 Governance Gate passes the corrected PR metadata;
2. Full Stack Governance CI accepts the governed lineage delta;
3. ABACUS Multi-Format Publication passes candidate generation and independent validation;
4. Markdown deterministic parity is preserved;
5. GitHub Pages remains a deployment candidate on pull-request heads rather than being misclassified as hosted proof;
6. the atomic publication decision is `WITHHOLD` while hosted Pages evidence is absent;
7. tamper tests reject invalid artifact or hosted-receipt hashes;
8. semantic closed-loop and replay checks remain green.

## Post-merge hosted proof

A pull-request head cannot satisfy the final Pages publication predicate because A9.1 deliberately deploys only on `push` to `main`.

After merge, the exact main SHA must execute:

`upload-pages-artifact -> deploy-pages -> hosted network fetch -> independent network refetch -> atomic PROMOTE`

`DEBT-007 multi_format_receipts` remains `PARTIAL` until that main-branch hosted proof exists. Producing or uploading an HTML directory is not sufficient evidence.

## Authority boundary

A9.1 governs publication evidence only. It does not convert render quality into engineering, compliance, safety, acceptance, negotiation, or release authority. Generated HTML, Markdown, PPTX, PDF and Pages outputs remain non-canonical derivatives of the governed SSOT.
