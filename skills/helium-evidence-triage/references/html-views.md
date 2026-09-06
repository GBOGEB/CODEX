# Integrated human HTML views

Use a general helium-properties workbench, not a provider-validation dashboard.

Navigation: `Overview | Point | P1->P2 | Path | Grid | Exergy | Hydraulics | Analysis | Evidence`.

Overview shows engineering state/path, primary h/s, governing/reference source, evidence status and disposition. Point shows one state and properties. P1->P2 shows deltas, mass-flow energy and datum-valid exergy. Path shows compact T/P/mass-flow/h/s nodes and expandable transport/phase properties and edge hydraulics/exergy. Grid renders governed SSOT heatmaps/3D with operating points and validity boundaries. Exergy is withheld when datum alignment is unproven. Hydraulics shows pressure profile, reverse budget, controlling segment/user and uncertainty. Analysis contains pressure drop, exergy, PCA, sensitivity, Monte Carlo and BT. Evidence shows provider/version/lineage, locator, hashes, date/status/disposition; technical runtime internals stay behind diagnostics.

JavaScript may transform presentation (axis/property selection, log/linear, zoom, legend, heatmap/3D) but must not silently become the governing EOS.
