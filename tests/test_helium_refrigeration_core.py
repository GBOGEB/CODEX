from __future__ import annotations

import textwrap

import pytest

from physics.helium_refrigeration_core import (
    RuntimeGovernanceError,
    run_governance_assimilation,
    verify_mass_fractions,
)


def test_verify_mass_fractions_respects_four_decimal_contract() -> None:
    assert verify_mass_fractions([0.12344, 0.87655])


def test_verify_mass_fractions_rejects_invalid_total() -> None:
    assert not verify_mass_fractions([0.5000, 0.4998])


def test_run_governance_assimilation_returns_true_for_valid_payload(tmp_path) -> None:
    ssot_path = tmp_path / "ssot.yaml"
    ssot_path.write_text(
        textwrap.dedent(
            """
            ssot:
              components:
                - id: G10-TUPLE-HE-REF
                  modes:
                    2K-SB:
                      target_efficiency: 0.35
                    2K-OP:
                      nominal_flow_g_s: 11.5
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    assert run_governance_assimilation(
        ssot_path=str(ssot_path),
        active_flow=11.5,
        active_efficiency=0.35,
        mass_mix=[0.9995, 0.0005],
    )


def test_run_governance_assimilation_returns_false_when_gate_fails(tmp_path) -> None:
    ssot_path = tmp_path / "ssot.yaml"
    ssot_path.write_text(
        textwrap.dedent(
            """
            ssot:
              components:
                - id: G10-TUPLE-HE-REF
                  modes:
                    2K-SB:
                      target_efficiency: 0.35
                    2K-OP:
                      nominal_flow_g_s: 11.5
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    assert not run_governance_assimilation(
        ssot_path=str(ssot_path),
        active_flow=8.0,
        active_efficiency=0.20,
        mass_mix=[0.7, 0.2],
    )


def test_run_governance_assimilation_rejects_invalid_or_empty_payload(tmp_path) -> None:
    empty_ssot = tmp_path / "empty.yaml"
    empty_ssot.write_text("", encoding="utf-8")

    with pytest.raises(RuntimeGovernanceError, match="missing 'ssot' mapping"):
        run_governance_assimilation(
            ssot_path=str(empty_ssot),
            active_flow=11.5,
            active_efficiency=0.35,
            mass_mix=[0.9995, 0.0005],
        )

    list_ssot = tmp_path / "list.yaml"
    list_ssot.write_text("- bad\n", encoding="utf-8")

    with pytest.raises(RuntimeGovernanceError, match="top-level mapping"):
        run_governance_assimilation(
            ssot_path=str(list_ssot),
            active_flow=11.5,
            active_efficiency=0.35,
            mass_mix=[0.9995, 0.0005],
        )
