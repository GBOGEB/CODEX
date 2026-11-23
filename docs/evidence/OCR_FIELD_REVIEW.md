# OCR field review and crop receipts

`src/evidence/ocr_field_review_v1.py` extends the existing subordinate OCR
runtime with source-bound regions, replayable crop recipes, attributed
transcription references and per-configuration comparisons.

## Why a field layer is needed

A full-page OCR score does not establish a particular date or identifier.
Small differences in segmentation can replace one digit with another, add a
table border as punctuation, or mistake a letter for a number. An unchanged
cached result is historical evidence, not a new recognition job.

The field layer keeps the original document and raster primary. It records
the exact source SHA256, physical page, parent raster file SHA256 and pixel
rectangle. Two pixel-identical copies retain distinct source occurrences.
An executor must verify the PDF-to-parent-raster association by rendering the
pinned source; the generic crop function makes no independent PDF claim.

## Supported operations

1. `make_region` validates a physical occurrence and creates its content hash.
2. `crop_region` reads immutable parent bytes, checks their digest, rejects
   out-of-bounds or multiframe inputs and derives a PNG. Supported transforms
   are integer scale 1-8 with Pillow Lanczos, a white border and optional
   grayscale autocontrast. The recipe records the Pillow version and output
   bytes. It never overwrites its input.
3. An executor runs OCR, retains raw output and actual command/version/model
   identities, and calls the existing `record_execution` and `build_lineage`.
4. `bind_observation` validates that execution fingerprint and binds its
   source, page, crop and complete result text to the region. A caller-created
   receipt cannot authenticate an executor. Raw logs and source-render replay
   are still required for an execution claim.
5. `make_reference` attributes an assistant visual or owner-supplied
   transcription to the same region. Neither reference type is an approval.
6. `qualify_field` compares the complete region text after NFC and whitespace
   normalization only. It rejects duplicate execution keys and altered
   references. Digits, diacritics, punctuation and date formats are preserved.

The states are `NOT_EXECUTED`, `ALL_CONFIGURATIONS_MATCH`,
`CONFIGURATION_DEPENDENT_MATCH` and `NO_CONFIGURATION_MATCH`. Every result
retains `authority_effect=NONE`, `automatic_source_rewrite=false` and
`independent_engine_corroboration=false`. Several Tesseract configurations are
configuration diversity, not several independent OCR engines.

## Evaluation contract

Freeze the reference cohort and configuration choices before a qualification
run. Identify fields already used to tune a pilot. Record sample strata and
the scope of any exhaustive subtable; a purposive reference bank does not
estimate corpus-wide accuracy. Report the primary configuration separately
from the union of matches across configurations. Preserve all disagreements.

Keep reference authorship and review limits explicit. A second assistant
reading can corroborate a transcription, but it is not human signoff or
contractual effectiveness. Recognition failures remain failures even when
a reviewer can read the source character. Field review never changes the
source's own control identity, registered date, revision, approval or role.

## Verification

Run `python -m pytest -q tests/test_ocr_field_review_v1.py` from the repository
root. The tests use generic fixtures and check wrong-source/region rejection,
parent replacement, exact replay, cache duplication, fingerprint tampering,
whole-field matching and the absence of authority promotion. Recognition
quality must be evaluated separately on retained, access-controlled inputs.

Pillow is an explicit dependency in `requirements.txt`. This engine uses its
supported public image APIs; it does not modify a managed artifact package.
