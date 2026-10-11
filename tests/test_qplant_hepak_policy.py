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
    with pytest.raises(QplantHepakPolicyError, match="QPLANT_HEPAK_REQUIRED"):
        validate_governing_source(temperature_K=1.8, provider="CoolProp", authority_role="GOVERNING")


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
