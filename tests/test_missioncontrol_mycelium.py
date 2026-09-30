from scripts.validate_missioncontrol_mycelium import validate


def test_missioncontrol_mycelium_contract() -> None:
    assert validate() == []
