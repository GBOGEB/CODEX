% GISTAU Chapter 15 — Validated Thermodynamic Model
% Version 0.7.0

---

# GISTAU Chapter 15: from book to validated model

_OVERVIEW · Slide 1_

- Chapter 15 thermodynamic tools rebuilt as code, a CI-gated validation and an online engineering portal.
- Helium-4 physics is governed by GBOGEB/ABACUS at 4c2f669 (CoolProp==7.2.0); CODEX consumes it and never governs it.
- L1 validated model: 4 of 4 checked worked examples reproduce the book (12 of 12 quantities); 1 open pending a source check.

### Objectives

- L0 parse and trace: book source to tuples to source snippets
- L1 validated model: reproduce the Ch15 worked examples within the book's printed precision (current)
- L2 digital shadow: QPS Line-S triage scenarios from design data and evidence registers
- L3 twin: live PLC/historian feed (later)

---

# Who governs helium-4 physics

_AUTHORITY · Slide 2_

- CODEX and pinned ABACUS routing: PARITY at every probe (1.8, 1.99, 2, 2.1768, 3, 4.5, 4.6, 300 K).
- Pin covers 7 ABACUS files by git blob and sha256; meta checksum 6e6913561461…

### Governance

- **0 < T <= 4.5 K**: rule: HEPAK governs, including He-II below the lambda point
- **T > 4.5 K**: rule: CoolProp (Ortiz-Vega EOS) governs, including supercritical
- **T < 2.1768 K**: rule: CoolProp out of range in any role (COOLPROP_OUT_OF_RANGE)
- **NIST**: rule: validation reference only, never governing

---

# L1 validation: Ch15 worked examples

_VALIDATION · Slide 3_

### Checklist

- **T00 state point, 1 bar / 300 K**: result: pass; book vs provider: h 1563.32 vs 1563.32 J/g · s 28.0075 vs 28.0077 J/g·K · ρ 0.1604 vs 0.160391 kg/m³
- **T02 free expansion, 14 to 1 bar + 100 W**: result: pass; book vs provider: T out 19.16 vs 19.1586 K · h in 101.92 vs 101.922 J/g · h out 103.92 vs 103.922 J/g
- **T02 mass flow from heat input**: result: pass; book vs provider: ṁ 7.39 vs 7.38449 g/s · h in 106.67 vs 106.674 J/g · h out 120.21 vs 120.216 J/g
- **T04 expander, 14 to 1.2 bar**: result: pass; book vs provider: T out 12.93 vs 12.9344 K · h out 70.85 vs 70.8532 J/g · P -2981.6 vs -2981.63 W
- **T05 cold compressor, 0.5 to 1.7 bar**: result: open (source check); book vs provider: T out 7.72 vs 9.10519 K · h out 42.37 vs 49.1488 J/g · P 5336 vs 8049.84 W

### Notes

- Tolerances: 0.05 K, 0.05 J/g, 0.005 J/g·K, 0.5 % density, 1 % derived.
- 7 examples excluded with a stated reason (HEPAK two-phase, ambiguous transcription); never counted as passing.
- Recorded from CI run 39116863100; CI fails if the record drifts.

---

# Open item: T05 cryogenic compressor

_VALIDATION · Slide 4_

- First CI run (ABACUS 4c2f669, CoolProp 7.2.0): inlet state agrees with the book (h1 29.03 J/g both), but the book's implied work 5336 W / 400 g/s = 13.34 J/g is below the isentropic work for 0.5 -> 1.7 bar from 5 K (15.09 J/g), which is impossible for eta_s = 0.75. Verify outlet pressure, efficiency and inlet temperature in Fig. 15.31, p. 638.

### Changes

- Verify Fig. 15.31 (p. 638) against the printed book: inlet temperature, outlet pressure, efficiency.

---

# Independent reference: NIST TN 1334

_VALIDATION · Slide 5_

- Governing provider checked against NIST TN 1334 (Arp & McCarty) rows; enthalpy compared as differences (different reference states).
- Tolerance 1 % on density and Δh; all rows at T ≤ 4.5 K, so the check is advisory.
- First CI comparison: all rows within tolerance (CODEX #1007).

### Checklist

- **Row A**: state: 4.5 K / 300 kPa
- **Row B_10kPa**: state: 3.6 K / 10 kPa
- **Row B_20kPa**: state: 3.6 K / 20 kPa
- **Row B_40kPa**: state: 3.6 K / 40 kPa

---

# Cross-check incarnation: ideal-gas helium

_CROSS-CHECK · Slide 6_

- A deliberately simple ideal-gas model runs beside the governing provider; disagreement is a signal, never averaged away.
- Measured validity domain: T ≥ 50 K and ideal-gas density ≤ 2.5 kg/m³.
- Physics outputs of the governing provider hashed in CI: 3586bca7fa97… over 24 grid points.

---

# Engineering toolbox and portal

_TOOLS · Slide 7_

- Six calculators in the browser: state point, compressor, JT valve, expander, heat exchanger, equivalent power.
- Plotly views: T–s diagram with isobars, heat-exchanger end temperatures, power breakdown, validity-domain map.
- Browser maths is a mirror of the Python engine; a CI test requires identical results.

### Artifacts

- https://gbogeb.github.io/CODEX/gistau-ch15/toolbox.html
- https://gbogeb.github.io/CODEX/gistau-ch15/l1_validation.html
- https://gbogeb.github.io/CODEX/gistau-ch15/physics_authority.html
- https://gbogeb.github.io/CODEX/gistau-ch15/

---

# CI gates behind every number

_GOVERNANCE · Slide 8_

### Governance

- **Pin verification**: rule: ABACUS checkout must match the pinned commit, git blobs and sha256
- **Physics output checksum**: rule: provider outputs over the grid must equal the recorded checksum
- **Basic incarnation**: rule: within tolerance everywhere inside its measured domain
- **NIST TN 1334**: rule: governing provider within tolerance of the reference rows
- **L1 worked examples**: rule: checked examples pass; committed record equals the fresh run

---

# Next steps

_PLAN · Slide 9_

### Checklist

- **T05**: next: Correct the Fig. 15.31 transcription from the printed book, re-record L1; state: open
- **Ch.3**: next: Add the GISTAU Chapter 3 source and build the book navigator; state: open
- **HEPAK**: next: Bind HEPAK receipts to validate the two-phase examples (T ≤ 4.5 K); state: open
- **L2**: next: QPS Line-S triage scenarios on the validated provider; state: planned
