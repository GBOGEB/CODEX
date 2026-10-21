---
name: qps-house-style
description: Use for any QPS, cryoplant, CODEX or VCR deck, Word file or Claude Doc so it gets the corporate post-processing layer and passes the publish-to-corporate QA gate.
---

# QPS house style bridge

This skill sits on top of the standard docx, pptx and Claude Docs skills. Load the matching skill as usual, then apply the rules below. It augments the existing masters; it never edits the master files themselves.

## Kit
`tools/house_style/` in GBOGEB/CODEX (see its README):
- `templates/QPS_House_starter.docx` / `.dotx`: Word reference doc and template from `Full_VCR_Handover_master.docx`.
- `templates/QPS_House.pptx` / `.potx`: the SCK•CEN 2020 slide master from `QPS_MTBF_WCS_DMAIC_v7.pptx` (SHA-256 in the kit README). Not committed; build it with `build_templates.py` when missing.
- `qps_post.py`: the post-processing layer. `qps_qa.py`: the publish-to-corporate QA gate (check, fix).
- Front-matter structure comes from `MINERVA_Template_Enhanced.docx`.

## Always: run the post-processing layer last
Every Word file or deck delivered for this project goes through `qps_post.py` as the final step:
```
python3 tools/house_style/qps_post.py docx IN OUT.docx --title "..." [--subtitle --ref --version --classification --author --date] [--keep] [--pdf]
python3 tools/house_style/qps_post.py pptx IN OUT.pptx --title "..." [same options] [--pdf]
```
It adds the MINERVA front matter or the cover slide, the corporate header/footer (Word) or the corporate master with logo, reference, ISC and slide numbers (slides), and fills the name, reference, classification and date fields. Default classification is Restricted; ask only if the content suggests otherwise.

## Always: pass the QA gate before publishing
```
python3 tools/house_style/qps_qa.py check OUT          # exit 1 = not publishable
python3 tools/house_style/qps_qa.py fix IN OUT --title "..."   # re-host / re-flow, snap fonts and colours, re-check
```
Deliver only files that report PUBLISHABLE, and attach the QA report. Anything marked "Auto-fix: no" (placeholder text, empty reference) needs the author.

## Word
- Pandoc route (Markdown, HTML, ODT, exported docs): pass the source straight to `qps_post.py docx`; it runs pandoc with `--reference-doc QPS_House_starter.docx`.
- python-docx / docx-skill route: build on `QPS_House_starter.docx`, use only the master styles (Title, Heading 1-3, Normal, Table Caption, Table Grid), then run `qps_post.py docx --keep`.
- Do not write a title page yourself, and never type section numbers or "§" into heading text: headings auto-number.

## Slides
- Markdown route: `qps_post.py pptx deck.md` (pandoc, then re-hosted onto the corporate master).
- python-pptx / pptx-skill route: build on `templates/QPS_House.pptx` using its "Text Slide" and "Blank" layouts and theme colours only, no cover slide; or build in any tool and let `qps_post.py pptx` re-host the slides.
- Governed decks: reference or add the slide in GBOGEB/CODEX `MANIFEST/MASTER_SLIDE_REGISTRY.yaml` via a draft PR only.
- Render to images (`--pdf`, then pdftoppm) and look at every slide or page before delivering. On Windows without LibreOffice, `--pdf` exports through PowerPoint/Word (COM).

## Claude Docs
Claude Docs stay the editable source. Mirror the structure (title, date/author byline, VCR section order: Requirements (RTM); Quality & Test Planning; BOM snapshot; Vendor landscape; ADR/OCD tie-ins; captions above tables). When a Word or PDF deliverable is needed, export the doc to .docx or Markdown and run `qps_post.py docx` on it.

## Theme
SCK•CEN 2020: purple #562873 and pink #984A9C, with cyan #8ED8F8, navy #034694, greys #CACCD0 / #DFE0E2, text #515151, hyperlink #BC58AE. Word: Segoe UI body, Segoe UI Semibold headings. Slides: Segoe UI (theme heading and body font). Tints of palette colours are fine.

## Do not
- Modify the CODEX master files or golden_thread receipts.
- Add metrics, receipts or registry entries that are not sourced from the repositories.
