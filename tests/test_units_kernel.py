from gistau_ch15.kernels.units import (
    bar_to_pa,
    celsius_to_kelvin,
    kpa_to_pa,
    mbar_to_pa,
    pa_to_bar,
)


def test_bar_to_pa() -> None:
    assert bar_to_pa(1.0) == 100000.0


def test_mbar_to_pa() -> None:
    assert mbar_to_pa(26.0) == 2600.0


def test_kpa_to_pa() -> None:
    assert kpa_to_pa(101.325) == 101325.0


def test_pa_to_bar() -> None:
    assert pa_to_bar(300000.0) == 3.0


def test_celsius_to_kelvin() -> None:
    assert celsius_to_kelvin(0.0) == 273.15
