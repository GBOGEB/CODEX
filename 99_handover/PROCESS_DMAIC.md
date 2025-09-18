# Recursive Build & DMAIC Control Plan

## Define
- Targets: Table 6 leakage limits, He loss ≤1 Nm³/day, analyzer accuracy ±1 ppm, S-line PSV ≥200 g/s @300 K to WCS.LP, BD/PSV populations fixed.
- Artifacts: MASTER_DIFF, MASTER_PATCH, rename map, RTM, ITP, QA procedures, P&ID legend, BOM, ADR, OCD, vendor summary, .glob.

## Measure
- Diff coverage (% of anchors updated).  
- Purge residual (%) per service event.  
- Helium loss (Nm³/day).  
- PSV dossier completeness (%).  
- P&ID /FS tag conformance (%).

## Analyze
- Investigate any residual >0.05 %, leak test failures, PSV capacity gaps, or missing tamper scans.  
- Rank changes using impact index (0–5) across scope, safety, acceptance, vendor, integration.

## Improve
- Add DBB kits to high-touch points, adjust eductor ΔP, update gasket alloy mix, schedule extra analyzer calibration if drift >±1 ppm/year.

## Control
- Quarterly QA review of KPIs.  
- CIS alerts on tamper seal scans and purge logs.  
- Maintain SEED tag (1.3.0) and archive `handover_master_applied.tgz`.

## Workflow Summary
1. Generate content (diff, patch, RTM).  
2. Parse & map anchors; apply rename map.  
3. Produce artifacts (Markdown → PDF/DOCX; CSV/XLSX).  
4. Index & rank changes for approval (Decision column).  
5. Issue patch & .glob; capture reproducibility instructions.  
6. Transfer to user/orchestrator; update baseline after approval.
