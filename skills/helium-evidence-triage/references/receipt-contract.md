# Canonical receipt contract

One canonical receipt is the evidence object consumed by human views and downstream analysis.

Core identity: `schema`, `calculation_id`, optional `correlation_id`, `request_sha256`, `ssot_sha256`.

Provider identity: provider/version, implementation, EOS/dataset, source locator/repository/revision/commit/hash, authority role and lineage class.

State payload: T/P and pressure basis, h/s/rho, cp/cv/mu/k/Pr as applicable, phase/quality, raw-vs-derived marker and units.

Derived block: deltas, energy flow, exergy, equivalent duty, pressure loss, Re, PCA etc. Preserve enough source-state identity to reproduce each result.

Evidence/governance: evidence status, validation residual/tolerance, project disposition, project-supplied contract/requirement refs, timestamp/actor when appropriate.

View parity: Excel, HTML, federation and reports reproduce calculation id, SSOT digest, provider/version, states/properties, evidence status and disposition. Presentation rounding must not alter canonical truth.
