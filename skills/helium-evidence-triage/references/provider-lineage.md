# Provider and lineage classification

## Roles
- **GOVERNING**: project-selected authority for the state/property/decision.
- **PRIMARY_REFERENCE**: direct source-bound publication, table, dataset or reference implementation.
- **CORRELATED_DIAGNOSTIC**: useful implementation with materially overlapping model/data lineage.
- **INDEPENDENT_COMPARATOR**: sufficiently distinct model/dataset; independence must be argued from lineage.
- **OWNER_INTERIM**: engineering bound/assumption awaiting stronger evidence.

## HEPAK
Usually licensed/local. Capture actual version/build and supported I/O. Distinguish frontend/runtime recovered from numeric receipt returned. Do not expose/reverse-engineer restricted content. Commit only permitted interfaces, fingerprints/hashes, sanitized receipts and derived checks.

## NIST / REFPROP
Distinguish direct NIST publications/tables/datasets, REFPROP software/backend/version, and wrappers such as ctREFPROP. A wrapper is not the reference dataset.

## CoolProp
Capture package version, backend/fluid model, repository tag/commit when reproducibility matters, and underlying publication/correlation lineage for the challenged property. Independence is property-by-property.

## GASPROP / other EOS
Record exact source/vendor, version/tag/commit, EOS/dataset, property coverage, validity range and evidence role. Default to comparator until project governance promotes it.

## Independence check
Ask whether sources use different experimental data/correlations/EOS; whether one wraps another; whether they cite/embed the same correlation; whether different properties use different submodels; and whether datum/units/phase/interpolation are aligned.
