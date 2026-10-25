# MYRRHA WCS — Cross-Repository Index

> **Scope:** A single navigation surface for the MYRRHA QPLANT **Warm Compressor Station (WCS)**
> engineering content across the GBOGEB three-plane federation. This index is a **pointer**, not an
> SSOT — each linked artefact remains governed by its owning repository.

## Federation planes

| Plane | Repository | Role |
|-------|-----------|------|
| **Engineering SSOT** | [`GBOGEB/cryoplant-project`](https://github.com/GBOGEB/cryoplant-project) *(private)* | QPS engineering SSOT, OCD/ADR, release identity, owner approval |
| **Semantic / publication** | [`GBOGEB/CODEX`](https://github.com/GBOGEB/CODEX) *(this repo)* | KEB semantic-provenance, federation contracts, Pages publication |
| **Analytical runtime** | [`GBOGEB/ABACUS`](https://github.com/GBOGEB/ABACUS) | DOW analytical runtime, first-red diagnosis, CI, security |

## Canonical content homes

### Engineering SSOT — `cryoplant-project` (private)

- `PVPS/canonical/v4_3_controlled/` — PVPS controlled offer boundary, evidence control, hash manifest
- `architecture/w59/p02/` — ALaT human-knowledge release manifest
- `architecture/w59/p03/lkt/` — LKT 3P3×2 cycle QPS data and rollups
- `architecture/w61/W61_LKT_ALAT_ALIGNMENT.yaml` — LKT/ALaT alignment
- `controls/QPS_ALAT_*`, `controls/QPS_LKT_*` — ALaT/LKT negotiation, hierarchy and action controls

### Semantic / publication — `CODEX` (this repo)

- `rtm_integration/contract_followup/alat_clarification_bridge/` — ALaT clarification bridge (SSOT, RTM links, templates, generator, validator)
- `docs/qps-slide-system/` — QPS slide system (WCS node HTML/YAML)
- `docs/qps-source-bound-dense-decks-v1-6/bd005_current_lkt_fsd575_loop_point_v1_6.yaml` — LKT FSD575 loop point
- `07_ops/qps_roundtrip/` — WCS↔QRB roundtrip evidence
- `engineering_tools/hbhs_ep/docs/data/hcc_wcs_ssot.json` — HCC/WCS data

### Analytical runtime — `ABACUS`

- `qplant/handover_dashboard/src/wcs_scenarios.py` — WCS scenarios
- `qplant/w52_p2h_wcs_thermo_proof.py` + `tests/test_w52_p2h_wcs_thermo_proof.py` — WCS thermodynamic proof
- `analyses/compressors/` — compressor comparison analysis & visualisations
- `content/qplant/` — QPLANT lifecycle, process flow, thermodynamics, utilities (YAML)
- `myrrha_handover/` — self-contained **v0.4.7 handover snapshot** (browsable HTML; not SSOT)

## Handover snapshot

The dependency-free **v0.4.7 handover** (46 HTML views, `master/data.json` source of truth) is
preserved at [`GBOGEB/ABACUS:myrrha_handover/`](https://github.com/GBOGEB/ABACUS/tree/main/myrrha_handover).
See its `FEDERATION_POINTER.md` for the snapshot caveat. Original integration: ABACUS PR #437
(merged 2026-05-20); restored as a snapshot in ABACUS PR #2437.

## Source documents

- ALaT pre-study (C1393, 09/02/2023) & Kaeser **FSD 575 SFC** datasheet
- LKT pre-study & Kaeser **FSD 475 SFC** datasheet
