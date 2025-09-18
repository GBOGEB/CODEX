# Recursive Build & DMAIC Control Plan

## 1. Overview
This note captures the recurring build pipeline for the HELIUM_VCR_UHP baseline, including DMAIC metrics, content generation steps, artifact outputs, and handover sequencing for CODEX/CMB orchestration.

## 2. DMAIC Loop
- **Define:** Targets from Addendum II – Table 6 leakage limits, analyzers in WCS/QRB rooms, helium loss ≤1 Nm³/day, S-line relief to WCS.LP.  
- **Measure:** Track purge residual %, helium loss per intervention, RTM coverage, PSV/BD certification status, `/FS` orientation audit score.  
- **Analyze:** Pareto leak exceedances, purge cycles vs residual, S-line capacity margins, tamper seal reuse incidents.  
- **Improve:** Add DBB hardware, adjust eductor DP, revise gasket alloy allocation, update training.  
- **Control:** Quarterly QA reviews, KPI dashboard, automated CIS alerts for tamper seal breaks, SEED tag snapshots.

### KPI Set
| KPI | Target | Source |
|---|---|---|
| KPI.LeakPerJoint | ≤ Table 6 value | Helium MS logs |
| KPI.HeLossDay | ≤ 1 Nm³/day | CIS helium inventory dashboard |
| KPI.PurgeResidual | ≤ 0.05% | Purge log analyzer ppm |
| KPI.PSVReady | ≥ 95% certified | PSV/BD dossier |
| KPI.PnID_FS_Tagged | ≥ 98% | CAD review / digital twin |

## 3. Process Workflow (Mermaid)
```mermaid
flowchart TD
  A[Content generation (diff, patch, RTM)] --> B[Parsing & mapping (anchors, renames)]
  B --> C[Artifact engine (MD→PDF/DOCX/XLSX)]
  C --> D[Index & ranking (impact, risk, coverage)]
  D --> E[Patch & .GLOB emission]
  E --> F[Handover to CODEX/CMB orchestration]
  F --> G[Baseline update (Git SEED tags)]
  G --> H[DMAIC control (KPIs, reviews)]
  subgraph ServiceEvent
    S1[Isolate DBB] --> S2[Eductor pull-down]
    S2 --> S3[Helium backfill ×3]
    S3 --> S4[Break joint & replace gasket]
    S4 --> S5[Helium leak test vs Table 6]
    S5 --> S6[Log data & release]
  end
```

## 4. Artifact Generation
- **Markdown → PDF/DOCX:** Use pandoc with `-V toc=true -V numbersections=true` for clickable ToC and numbered headings.  
- **CSV → XLSX:** Import RTM.csv and ITP_HE_VCR.csv into spreadsheet templates for tender packs.  
- **Procedures & checklists:** Publish PROC_DBBA_Purge.md and PROC_He_LeakTest_ISO20485.md to QA system; attach to ITP.  
- **P&ID resources:** PID_SYMBOL_CHEATSHEET.md and PID_ASSEMBLY_PREVIEWS.md feed CAD legend updates.

## 5. Index & Ranking
Assign each change an impact score (0–5) considering safety, compliance, operations, vendor impact, and documentation load. Prioritise review of items ≥3.

## 6. Handover Steps
1. Review MASTER_DIFF.md and capture approvals (✅/❌/⏳).  
2. Apply RENAME_SBS.csv substitutions across source documents.  
3. Insert MASTER_PATCH.md into MASTER.docx at the location after Table 6.  
4. Generate updated PDFs/exports (symbols, assemblies, RTM, ITP).  
5. Commit changes; create SEED tag snapshot; package handover bundle.  
6. Provide CIS with updated requirement JSON for ingestion.

## 7. Reproducibility
- Git workflow: commit → tag `SEED_YYYYMMDD`.  
- Store `handover_master_applied.tgz` with all artifacts.  
- Document versions inside requirements.json meta block.
