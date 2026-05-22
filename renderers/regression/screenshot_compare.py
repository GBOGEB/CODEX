from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScreenshotDiffResult:
    baseline_image: str
    candidate_image: str
    similarity_score: float
    passed: bool


class ScreenshotComparator:
    """Screenshot regression comparison scaffold.

    Planned future implementation:
    - pixel diffing
    - semantic region detection
    - contrast regression checks
    - layout drift checks
    - navigation position checks
    """

    def compare(self, baseline_image: str, candidate_image: str) -> ScreenshotDiffResult:
        return ScreenshotDiffResult(
            baseline_image=baseline_image,
            candidate_image=candidate_image,
            similarity_score=1.0,
            passed=True,
        )


if __name__ == '__main__':
    print('screenshot regression scaffold active')
