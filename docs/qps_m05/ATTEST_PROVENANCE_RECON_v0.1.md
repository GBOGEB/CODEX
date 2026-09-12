# M05 — Artifact Provenance / QA Recon

## Mission

Prove one bounded, current, runnable provenance path using the official `actions/attest` action and return an exact-SHA receipt for QPS/KEB/DOW consumption.

## Foreign-land finding

The local `GBOGEB/attest-build-provenance` repository is a fork of `actions/attest-build-provenance`. Upstream states that, as of v4, that action is only a wrapper around `actions/attest` and that new implementations should use `actions/attest` directly.

Therefore M05 does **not** adopt the fork as new infrastructure. It treats the fork as reference/history and targets the current official action.

## Bounded proof slice

This first pulse attests one deterministic text artifact created from the exact CODEX PR head.

Required evidence:

- exact CODEX source SHA;
- deterministic subject file;
- SHA-256 subject digest;
- `actions/attest@v4` execution;
- returned attestation ID and URL;
- local Sigstore bundle path copied into retained evidence;
- ordinary workflow artifact containing the subject, checksum and receipt.

## Authority boundary

An attestation proves provenance/signing linkage for the named subject. It does **not** prove engineering correctness, semantic correctness, physical validity, child acceptance, or release approval.

The QA Officer may use this as a stronger KR/evidence primitive; TM, PM and Governor retain their existing authorities.

## DoD

- [x] supersession path identified (`attest-build-provenance` -> `actions/attest` for new work)
- [x] bounded subject and receipt contract defined
- [ ] current PR workflow receives a runner and executes >0 steps
- [ ] official attestation created
- [ ] receipt artifact retained
- [ ] exact result consumed by QPS/KEB/DOW

## DoV

### DoV-1
Official attestation action executes on an exact CODEX SHA and emits a retained verifiable bundle + receipt.

### DoV-2
A separate QPS/KEB/DOW consumer reads the returned receipt and independently accepts/rejects/defer the provenance claim.

### DoV-3
The proof repeats automatically on a fresh head or recurrence without expedition-specific intervention.

## FIRST RED routing

- runner not assigned / zero steps -> Dockmaster
- permissions/OIDC/attestation API failure -> Engineer + QA
- receipt/schema failure after attestation -> Doctor/Engineer
- attestation PASS but governance misuse -> TM/Governor
