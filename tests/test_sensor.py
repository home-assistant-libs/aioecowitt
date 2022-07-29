"""Test ecowitt sensor module."""

from aioecowitt import sensor


def test_update_listener() -> None:
    """Test on change get updates from callback."""
    ecowit_sensor = sensor.EcoWittSensor(
        "test", "test", sensor.EcoWittSensorTypes.TEMPERATURE_C, "test"
    )

    called = False

    def on_change() -> None:
        """Test callback."""
        nonlocal called
        called = True

    ecowit_sensor.update_cb.append(on_change)

    ecowit_sensor.update_value(10, 0, 0)
    assert called

    called = False
    ecowit_sensor.update_value(10, 0, 0)
    assert not called

    ecowit_sensor.update_value(11, 0, 0)
    assert called
