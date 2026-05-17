# QCELL SVG Rebuild v0.6.2 Follow-up

## Core correction

Temperature and pressure must not share the same colour grammar.

Temperature is the dominant thermodynamic variable and remains the primary analysis view.
Pressure is secondary/diagnostic and must use a separate palette and optional layer.

## Implemented direction

- Temperature analysis is the default view.
- Pressure diagnostics are hidden by default.
- Combined viewing requires explicit layer toggles.
- Pressure uses purple/grey diagnostic palettes only.
- Cryogenic temperature colours are reserved for thermal interpretation.

## Geometry correction

The large rectangular 50 K shield frame is visually too dominant and mechanically box-like.

Next SVG phase should evolve the 50 K stage toward:
- chamfered window square
- rounded thermal shell
- nested protective envelope
- shorter horizontal span
- clearer warm/cold hierarchy

## v0.7.0 focus

- SVG grammar/style proof
- boundary elegance
- nested shell hierarchy
- external flow arrows
- separate legends
- HTML-hosted SVG workflow
- GitHub Pages readiness
