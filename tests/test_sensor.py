"""Test ecowitt sensor module."""
import pytest

from aioecowitt import server

from .const import GW2000A_V3_DATA
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


@pytest.mark.asyncio
async def test_heap_field(ecowitt_server, ecowitt_http) -> None:
    """Test handling of heap field."""
    heap_sensor = None

    def on_change(sensor: server.EcoWittSensor) -> None:
        """Test callback."""
        if sensor.key == "heap":
            nonlocal heap_sensor
            heap_sensor = sensor

    ecowitt_server.new_sensor_cb.append(on_change)

    resp = await ecowitt_http.post("/", data=GW2000A_V3_DATA)
    assert resp.status == 200
    text = await resp.text()
    assert text == "OK"

    assert heap_sensor
    assert heap_sensor.value == GW2000A_V3_DATA["heap"]
