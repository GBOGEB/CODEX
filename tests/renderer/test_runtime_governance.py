#!/usr/bin/env python3
from src.abacus_render_pipeline.runtime_governance import RuntimeGovernanceA61


def test_a61_spacing_grid_conformance():
    governor = RuntimeGovernanceA61()

    compliant_html = "<div style='margin: 16px; padding: 12px;'>Core Block</div>"
    non_compliant_html = "<div style='margin: 13px;'>Misaligned Element</div>"

    assert governor.validate_spacing_matrix(compliant_html) is True
    assert governor.validate_spacing_matrix(non_compliant_html) is False


def test_pdf_anchor_parity_verification():
    governor = RuntimeGovernanceA61()
    sample_md = """# Section 1
    <a name=\"section1\"></a>
    ## Section 2
    <a name=\"section2\"></a>"""

    results = governor.verify_pdf_anchor_integrity(sample_md)
    assert results["parity_verified"] is True
