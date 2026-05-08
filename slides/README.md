# PPTX Template and Deck Builder Guidance

This guide explains how the presentation tooling integrates with the CODEX pipeline, including the DOW orchestration layer, KEB conversion utilities, and the GBOGEB governance checks. It covers day-to-day usage, advanced customization, troubleshooting, and CI/CD automation so that the `ppt_engine` delivers consistent output across PPTX, PDF, and HTML.

> **Scope**
> - Authoring: Markdown or reStructuredText source files.
> - Conversion: Pandoc-based transforms invoked through KEB helpers.
> - Rendering: PowerPoint templates enriched with the QPLANT/SCKCEN corporate branding.
> - Governance: Artifact validation, version control hygiene, and metadata capture enforced by DOW jobs and GBOGEB rules.

## Quick start

1. Install the Python dependencies in an isolated environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Place your Markdown source in `slides/src/` and reference assets in `slides/assets/`.
3. Run the one-liner to generate a full deck (PPTX + PDF + HTML):
   ```bash
   python -m slides.qplant_sckcen_template build --source slides/src/demo.md --output-dir output/slides
   ```
4. Open the generated `output/slides/demo.pptx` in PowerPoint, or share `demo.html` for a quick review.
5. Commit only the source files and the metadata report; generated PPTX/PDF/HTML artifacts stay out of Git but are uploaded by DOW as pipeline artifacts.

## What the template provides

- **Branding fidelity**: SCKCEN color palette, typography, and logo positioning encoded in the base template, with overridable placeholders for partner branding.
- **Slide primitives**: Title, section, statement + evidence, tabular comparisons, KPI scorecards, and appendix pages exposed as reusable blocks via helper functions in `qplant_sckcen_template.py`.
- **Metadata-first**: Author, revision, sensitivity, and hyperlink manifests captured for every render, keeping GBOGEB checks auditable.
- **Multiformat parity**: Markdown → PPTX/PDF/HTML transformations share the same content map so text, hyperlinks, and speaker notes stay aligned.

## DOW, KEB, and GBOGEB integration

| Component | Purpose | Integration point |
|-----------|---------|-------------------|
| **DOW** | Pipeline scheduler that runs lint → render → publish | `slides.qplant_sckcen_template.build_deck` is called from the DOW `ppt` stage; artifacts are uploaded to the run summary. |
| **KEB** | Pandoc + conversion helpers for Markdown → PPTX/PDF/HTML | `convert_markdown_bundle` wraps KEB to keep CLI flags consistent. |
| **GBOGEB** | Governance checks (naming, hyperlink safety, metadata completeness) | `validate_deck_metadata` returns a machine-readable report consumed by GBOGEB. |

## Directory layout

```
slides/
├── README.md                  # This guide
├── qplant_sckcen_template.py  # PPT engine helpers and CLI wrapper
├── assets/                    # Logos, favicons, background images
└── src/                       # Markdown/RST slide sources and YAML manifests
```

> Tip: Keep image assets below 2 MB to avoid bloating the pipeline artifacts and to speed up Pandoc conversions.

## Template customization

1. **Update the base template**: Replace `assets/base_template.pptx` with an approved master slide. Maintain placeholder names (`BODY`, `TITLE`, `FOOTER`, `LOGO`) so automated layout binding stays intact.
2. **Override theme colors**: Edit the `THEME_COLORS` dictionary in `qplant_sckcen_template.py` to map semantic roles (primary, accent, warning) to RGB hex values.
3. **Inject partner branding**: Supply `--partner-logo` on the CLI to overlay a partner logo onto the title and section slides.
4. **Per-slide overrides**: Use fenced code blocks in Markdown with `slide-type: statement` or `layout: appendix` metadata to select specialized layouts.

## Rendering workflows

### Build a single source file
```bash
python -m slides.qplant_sckcen_template build \
  --source slides/src/strategy.md \
  --output-dir output/slides \
  --partner-logo slides/assets/partner.svg \
  --format pptx pdf html
```

### Batch build all manifests
```bash
python -m slides.qplant_sckcen_template batch \
  --manifest-dir slides/src/manifests \
  --output-dir output/slides \
  --format pptx pdf html
```

### Preserve hyperlinks
All formats keep hyperlink targets by default. Ensure your Markdown links use absolute URLs or repository-relative paths so they remain valid when rendered to PDF and HTML. The builder logs broken links and fails the GBOGEB check when `--strict-links` is enabled.

## Pandoc and format parity

- **Markdown → PPTX**: Uses the base template for layout binding; bullet indentation and table styling mirror the HTML output for parity.
- **Markdown → HTML**: Adds anchor links for headings, a floating table of contents, and slide-level navigation buttons.
- **Markdown → PDF**: Uses the same HTML theme as an intermediate step to keep typography and hyperlinks intact.
- **Speaker notes**: Add a `::: notes` block in Markdown; notes propagate to PPTX speaker notes and appear as collapsible sections in HTML.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Missing fonts in PPTX | Host lacks SCKCEN font pack | Install fonts locally. |
| HTML images broken | Asset path not copied | Place images in `slides/assets`. |
| Pandoc not found | Pandoc not installed or not on PATH | Install Pandoc 3.x and retry; the CLI checks and reports the detected version. |
| Broken hyperlinks in PDF | Relative links resolve incorrectly | Use absolute URLs or set `--base-url` so HTML → PDF conversion can rewrite links. |
| Deck rejected by GBOGEB | Missing metadata fields | Ensure required metadata fields (author, revision, sensitivity) are present in your source or configuration. |

## CI/CD guidance

- Add the following DOW stage to render decks on every merge:
  ```yaml
  stages:
    - name: ppt
      uses: slides.qplant_sckcen_template.build_deck
      inputs:
        source_dir: slides/src
        output_dir: output/slides
        formats: [pptx, pdf, html]
      # The build_deck function is called with source, output_dir, settings, and formats parameters.
      # DOW should invoke it for each source file found in source_dir.
  ```
- Upload `output/slides/*.pptx`, `*.pdf`, and `*.html` as pipeline artifacts; do **not** commit them to Git.
- Publish the metadata report (`output/slides/metadata.json`) so downstream consumers can reuse hyperlinks and authorship data.

## Frequently asked questions

### How do I reuse slides across decks?
The builder processes each Markdown source file independently. To reuse content, extract common slides into separate Markdown files and reference them in your main source.

### How can I preview HTML locally?
Run a lightweight web server:
```bash
python -m http.server --directory output/slides
```
Open `http://localhost:8000/demo.html` in your browser for navigation, search, and link verification.

### How do I add custom layouts?
1. Duplicate a master slide in `assets/base_template.pptx` and give it a unique name (e.g., `ComparisonGrid`).
2. Reference it from Markdown frontmatter: `layout: ComparisonGrid`.
3. Update `LAYOUT_ALIASES` in `qplant_sckcen_template.py` so the builder maps semantic names to the template layout.

### Can I embed data-driven charts?
Yes. Export charts as SVG or PNG and reference them in Markdown. When KEB converts to PPTX, images are anchored to the chart placeholder, preserving aspect ratio and captions.

## Style and accessibility checklist

- Prefer short bullet sentences; avoid dense paragraphs.
- Use a maximum of four colors per slide (primary, accent, success, warning).
- Provide alt text for every image: `![Caption](path "Alt text")`.
- Ensure contrast ratios meet WCAG AA for text over backgrounds.
- Keep header levels consistent so HTML navigation and PDF bookmarks stay meaningful.

## Governance and artifact hygiene

- Generated PPTX/PDF/HTML artifacts are excluded from Git via `.gitignore` but uploaded by the DOW pipeline for traceability.
- Every render writes `metadata.json` summarizing authorship, revision, sensitivity, slide count, link status, and template checksum.
- (Planned) A future `--freeze` flag will embed a SHA256 of the template and Markdown source into the deck notes so reviewers can verify provenance offline.

## Regulatory gatekeeper context (CE/ISO validation)

For regulated deliveries, the review body validating datasets and verification evidence is often an accredited conformity assessment organization rather than the software contractor itself.

- **BSI (British Standards Institution)**: standards body and certification provider active in ISO-aligned management system certification.
- **TÜV organizations (e.g., TÜV SÜD, TÜV Rheinland)**: independent testing/inspection/certification bodies frequently used for technical files, safety cases, and process audits.
- **Belgium context**: Belgian projects commonly use a notified body or accredited auditor selected by the prime contractor; subcontracted assessment by TÜV SÜD (or equivalent) is possible when contractually delegated.

### Corrigendum note (parked for next release)

- **CORR-REG-0001 (planned)**: The contractor **shall** ensure that any subcontracted gatekeeper (including TÜV entities) abides by the governing CE/ISO code item once the exact clause identifier is finalized in the contract annex.

## Delivery depth, intent, and handover checklist

Use this checklist to capture the total structure/gist of each deck-build change set and support clean handover:

1. **Content depth**
   - Source manifests included (`slides/src/**`), with revision labels.
   - Evidence references and hyperlink inventories recorded in metadata.
2. **Style depth**
   - Template lineage tracked (`template_path`, checksum, theme colors).
   - Partner-branding options documented (`--partner-logo`, `--base-url`).
3. **Structure depth**
   - Output parity across PPTX/PDF/HTML confirmed from one source.
   - Layout alias mapping validated for any custom slide masters.
4. **Intent and outcome**
   - Business objective and target audience recorded in deck metadata/frontmatter.
   - Governance report reviewed for required fields before release.
5. **Versioning and cross-references**
   - Tag metadata revision (`DECK_REVISION`) to match release identifier.
   - Link DOW run ID, artifact bundle path, and PR number in release notes.

### TODO (next steps)

- Finalize the contractual CE/ISO clause code and replace `CORR-REG-0001` placeholder.
- Add a CI check that fails if regulatory handover fields are missing from metadata.
- Extend changelog entries to include contractor/notified-body assignment per release.

## Change log

- **2025-02-17**: Added multi-format parity guidance, hyperlink preservation, and DOW/KEB integration examples.
- **2025-02-10**: Documented template customization and batch building workflows.
- **2025-02-03**: Documented metadata reporting for GBOGEB governance checks.
