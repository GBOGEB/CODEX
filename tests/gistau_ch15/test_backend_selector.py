from gistau_ch15.properties.backend_selector import (
    availability_report_rows,
    select_available_backends,
)


def test_fallback_backend_always_available():
    backends, availability = select_available_backends()

    assert 'fallback' in backends
    assert any(item.name == 'fallback' and item.available for item in availability)


def test_availability_rows_serializable():
    rows = availability_report_rows()

    assert isinstance(rows, list)
    assert rows
    assert 'name' in rows[0]
    assert 'tier' in rows[0]
    assert 'available' in rows[0]
