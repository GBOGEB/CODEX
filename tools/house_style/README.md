# House style and publish-to-corporate QA

An always-on post-processing layer and a QA gate that bring Word files and decks from any tool
(pandoc, python-docx, python-pptx, Claude's docs and slide skills, Google Slides exports) into the
SCK CEN corporate style before they are published.

## Authoritative references

| Output | Look and feel | Structure |
|---|---|---|
| Word | `Full_VCR_Handover_master.docx` (repo root): Segoe UI, purple/pink headings, A4, auto-numbered headings, SCK CEN footer with name, reference and ISC fields | `MINERVA_Template_Enhanced.docx`: title block, Copyright Rules, Configuration Control (Document History, Approval, Distribution List), Table of Contents, Abbreviations |
| Slides | `QPS_MTBF_WCS_DMAIC_v7.pptx`: the "SCK•CEN 2020" master (Titel Slide, Text Slide, Blank and 30+ layouts, logo, reference, ISC, slide number) | Cover on "Titel Slide 1", numbered content slides |

Theme: purple `#562873` and pink `#984A9C`, with cyan `#8ED8F8`, navy `#034694`, greys `#CACCD0`/`#DFE0E2`, text `#515151`, hyperlink `#BC58AE`.
Fonts: **Segoe UI** for headings and body in both the Word master and the slide theme (`theme1.xml`
major and minor font); Segoe UI Semibold for Word headings. Arial is accepted by the QA gate but is not
the theme font.

### Slide master source deck

| Deck | Bytes | SHA-256 |
|---|---|---|
| `QPS_MTBF_WCS_DMAIC_v7.pptx` (16:9, 4 slide masters, 38 slides) | 6,337,683 | `c31553f29d7c590c748165cd3d5b882e9cb69f849c372aa6d2078c786b1a4556` |

The v10 deck named in earlier versions of this README was not found; v7 is the latest copy on record.
`build_templates.py` writes `templates/QPS_House.source.txt` (deck name, size, SHA-256, build time) next
to the local master and warns when the deck it was given is not the one recorded above.

## Templates

`templates/QPS_House_starter.docx` and `.dotx` are built from the Word master and committed.
The slide master is **not** committed (corporate branding stays out of the public repo). Build it
locally from the authoritative deck:

```bash
python3 tools/house_style/build_templates.py Full_VCR_Handover_master.docx /path/to/QPS_MTBF_WCS_DMAIC_v7.pptx
```

The template keeps the deck's masters and layouts only. Its document identity is dropped:
the ECM properties in `docProps/custom.xml` (ID, Name, HyperLink, AlexandriaPath, CreateDate, reference
numbers, author) are blanked, `docProps/app.xml` is rewritten (no slide titles or counts of the source
deck), the core author/title are cleared, and the reference box on every master reads `SCK CEN/` until
`qps_post.py` fills it.

## Post-processing layer (`qps_post.py`)

```bash
python3 tools/house_style/qps_post.py docx IN.(md|html|odt|docx) OUT.docx --title "…" [--ref "SCK CEN/…"] [--pdf]
python3 tools/house_style/qps_post.py pptx IN.(md|pptx) OUT.pptx --title "…" [--ref "SCK CEN/…"] [--pdf]
```

`--pdf` uses LibreOffice (`soffice`) when it is on PATH; on Windows without it, Microsoft PowerPoint or
Word over COM (`office_pdf.ps1`). `--pdf-engine soffice|office` forces one.

* **Word:** pandoc with the house reference doc (headers and footers carry over), MINERVA front matter
  in its own sections, footer fields filled (name, reference, classification, save date), custom
  properties set, tables mapped to the house grid with a purple header row. `--keep` skips pandoc for
  a `.docx` already built on the starter; `--short` gives a title block only.
* **Slides:** decks on another master are re-hosted slide by slide onto the corporate master (title
  into the layout title, single body text into the layout body, other shapes fitted into the content
  area, notes kept); a cover goes on "Titel Slide 1"; slide numbers on every content slide; the
  reference, ISC and footer text are filled on **every** slide master and layout (the master has four);
  the document properties get this deck's name, reference, author and classification, and `app.xml`
  its own slide count. Layout names resolve case-insensitively (`BLANK` finds `Blank`, then `Blank 1`).

## QA gate (`qps_qa.py`)

```bash
python3 tools/house_style/qps_qa.py check FILE [--md report.md] [--json report.json]   # exit 1 when not publishable
python3 tools/house_style/qps_qa.py fix FILE OUT --title "…" [--pdf]                    # fix, then re-check OUT
```

| Area | Slides | Word |
|---|---|---|
| Theme | FAIL if the theme is not SCK•CEN 2020; WARN per off-palette colour (tints of palette colours and neutrals pass) | WARN per off-palette direct colour |
| Format | FAIL if not 16:9; FAIL per slide on a non-corporate layout | FAIL if not A4 portrait; WARN for styles not in the master |
| Fonts | FAIL for fonts other than Arial/Segoe UI (e.g. Google's Quattrocento Sans substitution) | FAIL for direct off-standard fonts |
| Corporate furniture | FAIL if the first slide is not a corporate title slide; FAIL per slide without a slide number; FAIL if the masters show different references; WARN if the reference is empty | FAIL if the corporate footer fields are missing or still show the master's document name |
| Identity | FAIL if `docProps/custom.xml` carries an ECM document ID that is not the footer reference | Custom properties are rewritten by `qps_post.py` |
| Basic content | WARN for untitled content slides; FAIL for template placeholder text; FAIL for `TODO`/`TBD`/`XXX` in a title or body placeholder (not in text boxes, tables, quotes or `status:` fields); WARN for likely text overflow | FAIL without a title or MINERVA front matter; FAIL for template placeholder text and for `TODO`/`TBD`/`XXX` outside quotes and `status:` fields; WARN for typed numbers in auto-numbered headings or no headings |

`fix` re-hosts or re-flows where the structure is wrong, then strips off-standard fonts back to the
theme font, snaps off-palette colours to the nearest palette colour, sets shrink-to-fit on overflowing
text and removes typed heading numbers. It never touches the source file.

Tooling success here is a style check only; it carries no engineering, compliance or acceptance
authority.
