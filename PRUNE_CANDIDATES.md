# Prune candidates — CODEX

> **Non-destructive list.** Nothing in this file has been deleted. It records artifacts
> flagged during a cross-repo integration audit (ABACUS · CODEX · private cryoplant-project)
> for the owner to review and prune at their discretion. Removing already-tracked binaries
> rewrites history, which is deliberately left to the maintainer.

## 1. Privacy-sensitive content in a public repo (review first)

CODEX is **public**. The following tracked items carry cryoplant / vendor / offer material
that the project designates for the **private** `cryoplant-project` repo:

| Severity | Path | Note |
|---|---|---|
| **HIGH** | `05_vendor/VENDOR_COSTS.md` | Indicative EU pricing (has redaction markers but still public). |
| **MED–HIGH** | `Input/Addendum II -  Cryoplant Technical Requirements_0711_1143.docx` | Cryoplant technical requirements, committed binary. |
| **MED–HIGH** | `Input/Addendum II -  Cryoplant Technical Requirements_2609_1313.docx` | Cryoplant technical requirements, committed binary. |
| **MED** | `Input/cryoplant_deck_handover_R1C2.zip` | Cryoplant handover archive (binary-policy violation). |
| **MED** | `Full_VCR_Handover.docx`, `Full_VCR_Handover_master.docx`, `VCR_Only_Handover.docx`, `VCR_Only_Handover_master.docx`, `VCR_Summary.pdf`, `VCR_Summary_export.pdf`, `VCR_Summary_master.docx`, `VCR_Summary_master.pdf`, `VCR_ADR_OCD_Partial.docx`, `VCR_Quality_Procedures.docx`, `VCR_Requirements.docx`, `Addendum_book_master.docx` | VCR/handover docs matching offer/currency patterns. |
| LOW | `tools/house_style/templates/QPS_House_starter.docx` | Template binary (keep source, generate on demand). |

**Suggested handling:** move the cryoplant-specific items to the private `cryoplant-project`
repo (using its `BINARIES_MANIFEST.md` + `checksums.sha256` convention), and regenerate the
rest from source bundles rather than committing binaries.

## 2. Binary-policy cleanup (16 tracked binaries total)

New binaries are now blocked repo-wide by `.gitignore`. The pre-existing tracked ones listed
above remain in history until pruned. To stop tracking without deleting the working copy:

```bash
git rm --cached <path>        # untrack, keep local file
git commit -m "chore: untrack committed binary per binary policy"
```

(For full history removal use `git filter-repo` — maintainer's call.)

## 3. Cross-repo duplication (shared with cryoplant-project)

A self-index / branch-hygiene toolkit is byte-identical across CODEX and the private
`cryoplant-project` (22 files), e.g. `.codex/skills/mip-repo-self-index/*`,
`scripts/mip_repo_self_index.py`, `scripts/branch_hygiene_delete.py`,
`scripts/mip_kit_manifest.py`, `tools/bd_workflow_frequency.py`. **Recommendation:** promote
to a single versioned template owned by CODEX and consumed by the private repo — do **not**
merge the repos (the public/private boundary must stay intact).

## 4. Branch hygiene

42 remote branches. `scripts/branch_hygiene_delete.py` already exists for this; review and
prune merged/stale branches at your discretion.
