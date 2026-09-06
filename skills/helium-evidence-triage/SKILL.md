---
name: helium-evidence-triage
description: Program-agnostic helium thermophysical evidence, property-source comparison, and engineering triage workflow. Use when ChatGPT must hunt, validate, compare, or govern helium-property evidence from HEPAK, NIST/REFPROP publications or datasets, CoolProp, GASPROP, or other EOS implementations; build provenance-controlled receipts and hashes; run PRE, P1 PRODUCE, P2 CHALLENGE, P3 REENTER, POST, roll-up, propagate, and fan-out; support spatial hydraulics, reverse-pressure closure, exergy, PCA, sensitivity, Monte Carlo, or Bradley-Terry prioritization; or keep Excel/HTML human views synchronized to one SSOT without exposing licensed-runtime internals.
---

# Helium Evidence Triage

Treat helium-property work as an evidence and governance pipeline, not merely an EOS lookup. Keep project-specific states, tolerances, RTM/contract references, UI labels, and closure rules in a separate project profile.

Never invent a licensed HEPAK result. Distinguish **runtime/frontend recovered** from **numeric receipt returned**.

## Canonical cadence

Use `PRE -> P1 PRODUCE -> P2 CHALLENGE -> P3 REENTER -> POST -> ROLL-UP -> PROPAGATE -> FAN-OUT`.

Read `references/workflow.md` for the full cadence.

## Provider and lineage rules

Determine separately: property authority, implementation, underlying EOS/data/publication lineage, and evidence role. Use `GOVERNING`, `PRIMARY_REFERENCE`, `CORRELATED_DIAGNOSTIC`, `INDEPENDENT_COMPARATOR`, or `OWNER_INTERIM`.

Do not count two implementations sharing the same underlying correlations/data as independent validators. Distinguish direct NIST publication/table/dataset evidence from REFPROP software and wrappers. Keep licensed HEPAK binaries/workbooks private unless licence explicitly permits repository storage.

Read `references/provider-lineage.md`.

## Evidence hunt

Search repositories/files for source locators, prior receipts, grids, manifests, hashes, adapter contracts, and acceptance history before proposing new work. For every datum capture source/revision, provider/version, EOS/dataset lineage, coordinates/units, phase/quality semantics, evidence role, source hash, calculation hash, and project disposition. State exactly what evidence proves and does not prove.

## Property calculations

Use project-configured provider policy. Do not hard-code one universal temperature boundary. Preserve raw provider values before derivations. Compare sources only at identical state coordinates, units, phase convention, and datum/reference convention. If h/s datum alignment is not proven, withhold cross-source exergy.

## Receipts and hashes

Use one canonical SSOT receipt per calculation. Excel, HTML, federation, and analyses are consumers of that receipt. Include schema/calculation/correlation IDs, request hash, provider/version/implementation/EOS, authority/lineage, state inputs/outputs, raw-vs-derived marker, phase/quality, source locator/hash, evidence status, disposition, and SSOT digest.

Use `scripts/canonical_receipt.py`; read `references/receipt-contract.md`.

## Human views

Keep normal engineering UI free of Python/COM/runtime internals. Use `Overview | Point | P1->P2 | Path | Grid | Exergy | Hydraulics | Analysis | Evidence`. PCA is one Analysis view. HTML plots render structured SSOT arrays; axis swaps/log scales/zoom/legend/heat-map/3D behavior are presentation transforms only.

Read `references/html-views.md`.

## Hydraulics and reverse-pressure closure

Separate physics kernel from property provider. For spatial pressure-drop work bind downstream pressure requirement/location, local user limit, cumulative segment flow, ID/wall/schedule, lengths, K/Cv, roughness/elevation/transitions, spatial T(x)/h(x), heat leak/mixing, and provider/version per segment. Reverse solve from the controlling downstream boundary to determine allowable pressure-loss budget and highest-leverage missing evidence.

## PCA, sensitivity, Monte Carlo, BT

Keep methods distinct: PCA = covariance/dimensionality evidence from a governed matrix; sensitivity = causal parametric response; Monte Carlo = probabilistic propagation; Bradley-Terry = explicit pairwise priority. Never promote benchmark PCA weights as measured results.

## Project profile composition

Remain project-agnostic. When a project profile is active, load project states, contract/RTM locators, pressure limits, provider authority, UI labels, and propagation targets through `references/project-profile-interface.md`. Project profiles configure the generic method; they do not fork it.

## Output pattern

For substantial triage report: recovered evidence; what it proves/does not prove; PRE/P1/P2/P3/POST status; residual blockers primary vs secondary; next highest-leverage receipt/action; DoV effect. Never promote acceptance/score without the project governance receipt that earns it.
