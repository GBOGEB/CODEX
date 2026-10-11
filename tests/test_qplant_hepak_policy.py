import pytest

from gistau_ch15.properties.qplant_hepak_policy import (
    ChildArtifactPin,
    QplantHepakPolicyError,
    fail_closed_receipt_status,
    governing_provider_for_temperature,
    validate_governing_source,
)


def test_qplant_hepak_band_inclusive():
    assert governing_provider_for_temperature(2.0) == "HEPAK"
    assert governing_provider_for_temperature(4.5) == "HEPAK"
    assert governing_provider_for_temperature(4.500001) == "COOLPROP"


def test_hepak_governs_he_ii_below_lambda():
    # He-II (below 2.177 K) is HEPAK territory; CoolProp is not rigorous there.
    for t in (1.8, 1.99, 2.177):
        assert governing_provider_for_temperature(t) == "HEPAK"


def test_rejects_coolprop_as_governing_in_he_ii():
    # Below the EOS limit the stricter out-of-range rule fires first.
    with pytest.raises(QplantHepakPolicyError, match="COOLPROP_OUT_OF_RANGE"):
        validate_governing_source(temperature_K=1.8, provider="CoolProp", authority_role="GOVERNING")
    # Just above lambda CoolProp is in range but still cannot govern.
    with pytest.raises(QplantHepakPolicyError, match="QPLANT_HEPAK_REQUIRED"):
        validate_governing_source(temperature_K=2.2, provider="CoolProp", authority_role="GOVERNING")


@pytest.mark.parametrize("t", [0.0, -1.0, float("nan")])
def test_rejects_non_positive_temperature(t):
    with pytest.raises(QplantHepakPolicyError, match="QPLANT_INVALID_TEMPERATURE"):
        governing_provider_for_temperature(t)


def test_rejects_coolprop_as_governing_in_band():
    with pytest.raises(QplantHepakPolicyError, match="QPLANT_HEPAK_REQUIRED"):
        validate_governing_source(temperature_K=3.8, provider="CoolProp", authority_role="GOVERNING")


def test_rejects_nist_as_governing():
    with pytest.raises(QplantHepakPolicyError):
        validate_governing_source(temperature_K=4.5, provider="NIST", authority_role="GOVERNING")


def test_missing_receipt_is_blocking_not_defer():
    assert fail_closed_receipt_status(False) == "BLOCKING_MUST_EXECUTE"


def test_exact_child_artifact_pin_requires_blob_and_sha256():
    pin = ChildArtifactPin(
        repository="GBOGEB/cryoplant-project",
        pr_number=583,
        head_sha="a" * 40,
        artifact_path="receipts/he_reference_hepak_lowT_grid.csv",
        artifact_blob_sha="b" * 40,
        artifact_sha256="c" * 64,
    )
    pin.validate()

    with pytest.raises(QplantHepakPolicyError, match="SHA256"):
        ChildArtifactPin(
            repository="GBOGEB/cryoplant-project",
            pr_number=583,
            head_sha="a" * 40,
            artifact_path="receipts/he_reference_hepak_lowT_grid.csv",
            artifact_blob_sha="b" * 40,
            artifact_sha256="short",
        ).validate()


@pytest.mark.parametrize("role", ["GOVERNING", "ADVISORY", "COMPARISON"])
def test_coolprop_out_of_range_below_lambda_in_any_role(role):
    with pytest.raises(QplantHepakPolicyError, match="COOLPROP_OUT_OF_RANGE"):
        validate_governing_source(temperature_K=1.8, provider="CoolProp", authority_role=role)


def test_coolprop_advisory_is_non_blocking_inside_eos_range():
    # In range (>= 2.1768 K) CoolProp may be advisory under HEPAK governance,
    # and governs outright above 4.5 K incl. supercritical (> 5.1953 K).
    validate_governing_source(temperature_K=2.1768, provider="CoolProp", authority_role="ADVISORY")
    validate_governing_source(temperature_K=3.8, provider="CoolProp", authority_role="ADVISORY")
    validate_governing_source(temperature_K=6.0, provider="CoolProp", authority_role="GOVERNING")
