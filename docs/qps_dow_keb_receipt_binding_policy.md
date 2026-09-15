# QPS / DOW / KEB Receipt Binding Policy

Purpose: ensure future QPS, DOW and KEB receipts can be traced to exact source PR, commit SHA and file digest.

## Minimum binding tuple

Every promoted receipt should carry:

```text
source_repo
source_pr
source_sha
source_locator
file_digest
receipt_id
validation_result
downstream_consumer
```

## Promotion rule

- `PASS` or `ACCEPT` requires source PR, source SHA and file digest.
- `DEFER` may carry `TBD` digest only when the next action explicitly says to compute and bind the digest.
- `REJECT` requires the predicate or validation failure that caused rejection.

## QPS rule

QPS ranking, BT/PCA inputs and decision objects must not consume evidence that has no source locator or receipt binding.

## DOW rule

DOW must not record `ACCEPT` unless upstream proof is source-bound and exact-SHA bound.

## KEB rule

KEB must not promote knowledge from text memory alone. A KEB atom needs a source receipt, exact SHA, digest, replay proof or controlled DEFER reason.

## Expedition Technical Manager secondment

KEB may second a **Technical Manager (TM)** into a temporary QPS TRIAGE / Elastic Expedition mission.
The TM is the mission technical authority. TM does not replace Scientist, QA, or Governor.

TM owns:
- technical mission hypothesis and controlled baseline
- assumptions and interface correctness
- validity domains and applicability limits
- technical evidence hierarchy and evidence maturity
- architecture consistency
- technical debt and technical risk discovered during the expedition
- cross-repo technical conflicts
- scientific findings requiring engineering disposition
- technical acceptance criteria
- technical DoV recommendation
- synchronization of accepted evidence back into KEB

Authority separation:

```text
Scientist  -> investigates uncertainty and produces findings
TM         -> disposes those findings into the controlled technical baseline
QA         -> proves the claimed execution occurred and met the stated checks
Governor   -> decides whether the result may be accepted/promoted under authority,
              licence, schema and governance rules
```

A runtime result may therefore be QA PASS but TM REJECT when the result is outside the valid technical domain. Conversely, TM and QA may PASS while Governor remains HOLD.

Observed execution remains ground truth. TM must not promote a model, algorithm, backend, property value, interface, or validity claim merely because a workflow exists or a README describes it.

### TM outbound secondment tuple

When KEB seconds a TM, the mission handoff should carry:

```text
mission_id
technical_hypothesis
technical_baseline_ref
assumptions
interfaces
validity_domains
known_evidence_bindings
known_conflicts
technical_acceptance_criteria
technical_risks
requested_checks
```

### TM return-home tuple

When the mission contracts or closes, TM returns to KEB with:

```text
mission_id
accepted_technical_baseline
source_receipts
exact_shas
file_digests
validity_boundaries
interface_decisions
scientific_findings_disposition
unresolved_technical_risks
technical_dov_state
replay_or_consumer_proof
next_validation_action_or_closure_reason
```

KEB must preserve `VALIDATION_REQUIRED`, `DEFER`, and `REJECT` states as first-class evidence states rather than normalizing them to PASS.

## Management-gate participation

For expedition victories:
- DoV-1 requires `TM technical = ACCEPT` in addition to Engineer, Smoker runtime, QA, PM delivery, and Governor acceptance.
- DoV-2 additionally requires KEB evidence binding to the independent consumer execution.
- DoV-3 requires replay/fresh-runtime evidence to be returned automatically so the accepted technical baseline no longer depends on expedition memory.

### CoolProp example boundary

A CoolProp execution receipt may establish that an exact backend/source SHA successfully evaluated defined helium points. That does **not** by itself establish governing authority across the low-temperature helium domain. If HEPAK is the governing source for a band, TM must retain the CoolProp result as `INDEPENDENT_CHECK` / `VALIDATION_REQUIRED` until a source-bound HEPAK cross-check and acceptance criterion are satisfied.

## Analyst evidence boundary

DMAIC/PCA/BT recommendations may consume KEB evidence only when source class is explicit. `EXPERT_SEEDED` analytics must remain distinct from `MEASURED` or `OBSERVED` telemetry and cannot be used as if it were runtime proof.

## Draft versus strict validation

Use draft mode during early capture:

```bash
python scripts/validate_bridge_rows.py
```

Use strict mode before promotion:

```bash
python scripts/validate_bridge_rows.py --strict
```

Strict mode treats `TBD` as missing.