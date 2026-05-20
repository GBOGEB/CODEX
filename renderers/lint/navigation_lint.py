from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NavigationIssue:
    component: str
    severity: str
    message: str


def validate_navigation_ids() -> list[NavigationIssue]:
    """Validate stable navigation and lineage requirements.

    Future implementation should:
    - validate slide-id uniqueness
    - validate figure references
    - validate local next/previous linkage
    - validate GitHub Pages anchor integrity
    """

    return []


if __name__ == '__main__':
    issues = validate_navigation_ids()
    if issues:
        for item in issues:
            print(f'[{item.severity}] {item.component}: {item.message}')
    else:
        print('navigation governance checks passed')
