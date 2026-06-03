# GOVERNANCE — Federation Index & Navigation Hub

> **Status: REFERENCE**
> This directory is a federation index and governance navigation hub.
> It does **not** redefine governance authority.
> All governance authority resides in the canonical sources listed below.

## Canonical Sources

| Source | Role |
|--------|------|
| [`GOVERNANCE.md`](../../GOVERNANCE.md) | Root governance authority *(create at repo root if absent)* |
| [`DELTA_1/`](../../DELTA_1/) | Delta governance artifacts and operational ownership |
| [`KEB/governance/`](../../KEB/governance/) | KEB governance rules, glossary, and metrics |
| [`MANIFEST/`](../../MANIFEST/) | Programme manifests, KPIs, and registry |

## Federation Index

| Federation Member | Governance Artifact | Location |
|-------------------|---------------------|----------|
| DELTA_1 | ADR template, taxonomy, operational ownership | `DELTA_1/` |
| KEB | Governance rules, glossary, metrics | `KEB/governance/` |
| MANIFEST | Programme metrics, convergence KPIs, layout governance | `MANIFEST/` |

## Governance Navigation

```
Repository Root
├── GOVERNANCE.md                    ← Root authority
├── DELTA_1/
│   ├── governance_adr_template.md   ← ADR template
│   ├── governance_taxonomy.md       ← Taxonomy
│   └── operational_ownership_matrix.md
├── KEB/governance/
│   ├── governance_rules.yml
│   ├── GLOSSARY.yml
│   └── metrics.yml
└── MANIFEST/
    ├── RTM.csv
    ├── CONVERGENCE_KPIS.yaml
    └── LAYOUT_GOVERNANCE.md
```

## Reconciliation Matrix

See [`reconciliation_matrix.md`](reconciliation_matrix.md) for the full overlap record.

> **Reconciliation Note:** Overlap with `GOVERNANCE.md` / `DELTA_1` / `KEB/governance` / `MANIFEST` measured at 76%.
> This layer was converted from an authoritative source to a federation index / navigation hub
> as part of PR-000A Governance Bootstrap Reconciliation.
