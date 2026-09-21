#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

VARIANTS = ["A_dark_exec", "B_dense_matrix", "C_landscape_appendix", "D_cards_dashboard", "E_plain_contract"]
FORMATS = ["html", "docx", "pdf", "pptx", "xlsx"]
EXPECTED_IDENTITY = {
    "source_repo": "GBOGEB/cryoplant-project",
    "source_issue": 1501,
    "source_pr": 1505,
    "source_merge": "b96b0db124d5db863313f85b575dc3ada41fec6f",
    "corpus_name": "QPS_VISUAL_RENDERING_CORPUS_SAMPLE_ONLY_v1_3",
    "corpus_zip_sha256": "4aacff3b425f8f2affbc25edbc70fd178cbe465b9504c685f99231b66674dc1e",
}


def validate(d):
    errors = []
    if d.get("schema") != "qps-visual-golden-sanitized/1.0":
        errors.append("schema")
    for key, expected in EXPECTED_IDENTITY.items():
        if d.get(key) != expected:
            errors.append(key)
    if d.get("variants") != VARIANTS:
        errors.append("variants")
    if d.get("required_formats") != FORMATS:
        errors.append("formats")
    if d.get("sample_only") is not True:
        errors.append("sample_only")
    if d.get("visual_binary_hashes_pairwise_distinct") is not True:
        errors.append("binary_divergence")
    if d.get("representative_render_hashes_pairwise_distinct") is not True:
        errors.append("render_divergence")
    if d.get("semantic_authority") != "EXTERNAL_CHILD_QPS_ONLY":
        errors.append("authority_inversion")
    if d.get("contains_qps_engineering_content") is not False:
        errors.append("content_leak")
    if d.get("formal_credit_delta") != 0:
        errors.append("formal_credit")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    data = json.loads(args.path.read_text(encoding="utf-8"))
    errors = validate(data)
    print(json.dumps({"passed": not errors, "errors": errors}, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
