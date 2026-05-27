# ROADMAP

# ABACUS_RENDER_PIPELINE

## Current Maturity

ALPHA A6

Execution strategy alignment:

- OPTION A = NOW
- OPTION C = LATER

Primary objective:

- visible execution over storage optimization

---

# W000 — Stage 0 (NOW): Simple + Working

Operational storage decision:

- use GitHub Releases only
- no Git LFS yet
- no artifact registry yet
- no S3 / federation storage layer yet

Minimal operational model:

- repo source + governance + HTML
- runtime bundles published as release assets
- Pages as the authoritative rendered surface

Workflow:

- build artifact
- upload release asset
- deploy Pages
- validate runtime

W000-W002 target:

- execution stability
- minimal operational burden
- clean repo hygiene
- gradual maturity increase

Explicit restraint for W000:

- no Kubernetes
- no databases
- no object storage
- no microservices
- no event buses
- no distributed telemetry backend

Stack focus:

- GitHub
- Pages
- Actions
- Plotly
- Python
- Markdown
- YAML
- HTML

---

# W003+ — Stage 1 (LATER): Controlled Growth

Introduce Git LFS only after measurable friction appears, such as:

- repeated large artifacts
- telemetry snapshots
- dashboards and image-heavy assets
- model/runtime datasets
- persistent binary governance assets

Activation trigger:

- measurable repository friction (not theoretical)
- expected around W003+ or first federation synchronization wave

---

# Target Hybrid Governance Topology (Mature State)

Layered responsibilities:

- Git: source + governance
- Releases: transient runtime bundles
- Git LFS: persistent heavy assets
- Pages: authoritative rendered surface
- Actions Artifacts: ephemeral CI outputs

Outcome:

- federated runtime governance storage topology without premature infrastructure complexity

---

# A6.1 — Renderer Enforcement Layer

Goals:

- renderer governance enforcement
- CI validation
- contrast validation direction
- deterministic render governance

Implemented:

- GitHub Actions workflow
- manifest validation
- kernel validation tests
- governance scanning hooks

Pending:

- contrast_lint.py
- overflow_lint.py
- spacing_lint.py
- navigation_lint.py

---

# A6.2 — Registry Layer

Goals:

- MASTER_SLIDE_REGISTRY.yaml
- MASTER_FIGURE_REGISTRY.yaml
- immutable lineage IDs
- render anchoring

---

# A6.3 — Snapshot Regression Layer

Goals:

- screenshot comparison
- HTML render diffs
- PDF regression checks
- GitHub Pages validation

---

# H5 — Helium Reference Kernels

Goals:

- helium_reference.py
- entropy realism
- density realism
- JT trend approximations
- low-temperature kernels

---

# H6 — Backend Convergence

Goals:

- CoolProp execution
- REFPROP comparison
- HEPAK comparison
- backend delta heatmaps
- validation residuals

---

# H7 — Saturation + He-II Review

Goals:

- saturation dome scaffolding
- low-temperature overlays
- He-II region preparation
- cryogenic publication review surfaces
