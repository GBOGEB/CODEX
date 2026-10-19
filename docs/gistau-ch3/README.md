# GISTAU Chapter 3 — Claude cycle source extract

Source: G. Gistau Baguer, *Cryogenic Helium Refrigeration for Middle and Large Powers*, Springer, 2020.
Original PDF sha256 `1b2843cf89c85e5415e89107a7fb5fdfb9673986a71dd669abe33ae0d4ff1b41` (725 pp., not committed; see `GISTAU/sources/master/source_manifest.yaml`).
PDF page = printed book page + 38 in Chapter 3 (e.g. Fig. 3.46, p. 123 = PDF 161) and + 35 in Chapter 15.

| Section | Book pp. | PDF pp. | Use |
|---|---|---|---|
| Ch. 3 Basic Thermodynamic Cycles | 77–150 | 115–188 | cycle topology, T–s states |
| §3.5.1–3.5.2 Claude cycle formation | 120–122 | 158–160 | Brayton precooling + JT expansion, Figs. 3.44–3.45 |
| §3.5.3.1 One turbine | 122–125 | 160–163 | baseline balance and T_turbine optimisation |
| §3.5.3.2–3.5.3.3 Two turbines, parallel vs series | 125–130 | 163–168 | arrangement decision |
| §3.5.5–3.5.7 Efficiency, JT expander, digest | 133–135 | 171–173 | Strobridge/Green correlation, Eq. 3.18 |
| §3.6.4 LN₂-precooled Claude cycle | 137–139 | 175–177 | alternative (not yet transcribed) |
| Ch. 15 Cryo Tool Box | 613–640 | 648–675 | see `docs/gistau-ch15/` |

Numerical benchmarks are in `data/claude_cycle_benchmarks.json`. Headline: the §3.5.3.1 one-turbine case
(50 W at 4.41 K + 0.5 g/s liquefaction, 14/1.2 bar, η_t 0.75) drops total cycle flow from 35.90 to 30.19 g/s and
isothermal power from 55.76 to 47.01 kW when the turbine discharge temperature is optimised (20.00 → 14.93 K).

These are textbook reference cases for generating and testing design alternatives. They are not QPS design targets
and do not by themselves establish QPS contract compliance or justify accepting a bidder's architecture.

"Chapter 3 Final.pdf" (X. L. Wang and J. Q. Zhang, *The Accelerator Cryoplant*) is separate ESS literature, not
Chapter 3 of this book; keep the two source identities apart.
