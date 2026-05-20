from __future__ import annotations

BAR_TO_PA = 100000.0
MBAR_TO_PA = 100.0
KPA_TO_PA = 1000.0


def bar_to_pa(value_bar: float) -> float:
    return value_bar * BAR_TO_PA


def mbar_to_pa(value_mbar: float) -> float:
    return value_mbar * MBAR_TO_PA


def kpa_to_pa(value_kpa: float) -> float:
    return value_kpa * KPA_TO_PA


def pa_to_bar(value_pa: float) -> float:
    return value_pa / BAR_TO_PA


def celsius_to_kelvin(value_c: float) -> float:
    return value_c + 273.15
