from __future__ import annotations

from scripts import validate_all


def test_current_execution_report_contract_is_accepted() -> None:
    validate_all.validate_report()

