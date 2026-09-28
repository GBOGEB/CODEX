# W331-R2 HIST-BD-034 final KEB binding

Status: **FINAL-MERGE BINDING / REVIEW REQUIRED**

## Child identity

- Repository: `GBOGEB/cryoplant-project`
- Root issue: `#1617`
- Canonical child PR: `#1651`
- Exact source head: `082c50516713710b9fbaedc8398b295f164be1a8`
- Merge SHA: `4158da2e6fd77d660e5bb9496fb7c417f316904c`

Earlier KEB PR #824 challenged the broader, later-superseded #1650 candidate.
This receipt is the final binding to the canonical merged child.

## 3PR

**Refresh — PASS.** Current child lineage includes the merged BT0/BT3/BT4
hardening from #1646, exact BT2 authority classes from #1636, BT1 semantic-key
binding from #1632, W328 minimum-population/future-row rules, and the final
Decimal/locator residuals in #1651.

**Probe — PASS.** The semantic challenge requires all of the following:

- BT0 cannot convert from a repository-local self-attestation; protected or
  signed owner provenance remains an external gate.
- BT1 numeric validity does not inherit from unrelated metadata.
- BT2 uses minimum governed populations, permits explicit future rows, and
  recomputes cumulative flow from the farthest user toward QRB/QDB.
- BT2 admits only complete child-governed source-bearing authority classes.
- BT2 rejects placeholder/deferred state tokens embedded in source locators.
- Source-bound zero flow remains valid.
- Every exact nonzero mass-balance residual requires finite nonnegative source
  tolerance and satisfies `abs(residual) <= tolerance` with no float grace.
- Machine epsilon is used only for cumulative-flow recomputation.
- BT3/BT4 source-completeness guards remain independent of BT2.

**Rank — PASS / one semantic root.** No second engineering root is admitted.

## MIP

**Modernize — PASS:** exact source/provenance semantics replace permissive
serialization shortcuts.

**Innovate — PASS:** provenance, numerical exactness, and physical source
conversion remain separate evidence dimensions.

**Perpetuate — PROVISIONAL:** promote only after exact merged-child review is
clean and this CODEX receipt itself is review/CI clean.

## Authority boundary

This parent review does not create QPS engineering acceptance, physical blocker
conversion, strict-numerical credit, runtime-GOLD credit, or formal credit.
QPS #923 remains independent. Authority transfer is false.
