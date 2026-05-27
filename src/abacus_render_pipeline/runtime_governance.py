from collections import Counter
import re


class RuntimeGovernanceA61:
    """
    G5 Post-Commissioning Layout & Structural QA Validator Engine.
    Handles overflow warnings, layout spacing, and formatting parity.

    TODO:
    - Integrate this validator into the render pipeline execution loop.
    - Extend spacing validation to stylesheet blocks if governance scope expands beyond inline styles.
    """
    FLOAT_EPSILON = 1e-9

    def __init__(self, spacing_standard_px: int = 4, allowed_overflow_threshold: float = 0.0):
        if spacing_standard_px <= 0:
            raise ValueError("spacing_standard_px must be greater than zero")
        self.spacing_standard_px = spacing_standard_px
        self.allowed_overflow_threshold = allowed_overflow_threshold

    def validate_spacing_matrix(self, html_content: str) -> bool:
        """Verifies that element margins adhere to the semantic structural grid."""
        style_blocks = re.findall(r"""style\s*=\s*(['"])(.*?)\1""", html_content, flags=re.IGNORECASE | re.DOTALL)
        for _, style_content in style_blocks:
            margin_declarations = re.findall(
                r"margin(?:-(?:top|right|bottom|left))?\s*:\s*([^;]+)",
                style_content,
                flags=re.IGNORECASE,
            )
            for declaration in margin_declarations:
                for px_value in re.findall(r"(-?\d+(?:\.\d+)?)px\b", declaration, flags=re.IGNORECASE):
                    margin = float(px_value)
                    remainder = abs(margin) % self.spacing_standard_px
                    distance_to_grid = min(remainder, self.spacing_standard_px - remainder)
                    if distance_to_grid > self.FLOAT_EPSILON:
                        return False
        return True

    def verify_pdf_anchor_integrity(self, markdown_content: str) -> dict:
        """Guarantees that all document header elements contain matching HTML reference anchors."""
        headers = re.findall(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", markdown_content, re.MULTILINE)
        anchors = re.findall(r'<a\s+name="([^"]+)">', markdown_content, flags=re.IGNORECASE)

        expected_anchors = [self._slugify_header(header) for header in headers]
        expected_counts = Counter(expected_anchors)
        actual_counts = Counter(anchors)
        missing_anchors = list((expected_counts - actual_counts).elements())
        unexpected_anchors = list((actual_counts - expected_counts).elements())
        is_consistent = not missing_anchors and not unexpected_anchors
        return {
            "total_headers": len(headers),
            "total_anchors": len(anchors),
            "parity_verified": is_consistent,
            "missing_anchors": missing_anchors,
            "unexpected_anchors": unexpected_anchors,
        }

    def detect_layout_overflow(self, element_width_pct: float) -> bool:
        """Flag potential container viewport overflows during HTML rendering sweeps."""
        return element_width_pct > (100.0 + self.allowed_overflow_threshold)

    @staticmethod
    def _slugify_header(header: str) -> str:
        """Normalize a Markdown header into a lowercase dash-separated anchor slug."""
        normalized = header.strip().lower()
        normalized = re.sub(r"[^a-z0-9\s-]", "", normalized)
        normalized = re.sub(r"[\s_]+", "-", normalized)
        normalized = re.sub(r"-+", "-", normalized)
        return normalized.strip("-")
