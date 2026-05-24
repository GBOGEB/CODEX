#!/usr/bin/env python3
from textwrap import dedent

from src.abacus_render_pipeline.runtime_governance import RuntimeGovernanceA61


def test_a61_spacing_grid_conformance():
    governor = RuntimeGovernanceA61()

    compliant_html = """
    <style>.card{margin: 13px;}</style>
    <div style='margin: 16px 12px; margin-left: 8px; padding: 12px;'>Core Block</div>
    """
    non_compliant_html = "<div style='margin: 16px 13px;'>Misaligned Element</div>"

    assert governor.validate_spacing_matrix(compliant_html) is True
    assert governor.validate_spacing_matrix(non_compliant_html) is False


def test_pdf_anchor_parity_verification():
    governor = RuntimeGovernanceA61()
    sample_md = dedent(
        """\
        # Section 1
        <a name="section-1"></a>
        ## Section 2
        <a name="section-2"></a>
        """
    )

    results = governor.verify_pdf_anchor_integrity(sample_md)
    assert results["parity_verified"] is True
    assert results["total_headers"] == 2
    assert results["total_anchors"] == 2


def test_pdf_anchor_parity_detects_missing_and_unexpected():
    governor = RuntimeGovernanceA61()
    sample_md = dedent(
        """\
        # Section 1
        <a name="section-1"></a>
        ## Section 2
        <a name="other-anchor"></a>
        """
    )

    results = governor.verify_pdf_anchor_integrity(sample_md)
    assert results["parity_verified"] is False
    assert results["missing_anchors"] == ["section-2"]
    assert results["unexpected_anchors"] == ["other-anchor"]


def test_detect_layout_overflow_respects_threshold():
    strict_governor = RuntimeGovernanceA61()
    tolerant_governor = RuntimeGovernanceA61(allowed_overflow_threshold=2.0)

    assert strict_governor.detect_layout_overflow(100.0) is False
    assert strict_governor.detect_layout_overflow(100.1) is True
    assert tolerant_governor.detect_layout_overflow(101.5) is False
    assert tolerant_governor.detect_layout_overflow(102.1) is True
