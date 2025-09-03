"""Test ecowitt sensor module."""

from typing import Any

import pytest
from pytest_aiohttp import AiohttpClient

from aioecowitt.sensor import EcoWittSensor, EcoWittSensorTypes
from aioecowitt.server import EcoWittListener

from .const import GW2000A_V3_DATA


def test_update_listener() -> None:
    """Test on change get updates from callback."""
    ecowit_sensor = EcoWittSensor(
        "test", "test", EcoWittSensorTypes.TEMPERATURE_C, "test"
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


@pytest.mark.parametrize(
    ("sensor_key", "expected_value", "request_data"),
    [
        ("heap", GW2000A_V3_DATA["heap"], GW2000A_V3_DATA),
        ("vpd", 0.091, {**GW2000A_V3_DATA, "vpd": "0.091"}),
    ],
)
async def test_sensor(
    ecowitt_server: EcoWittListener,
    ecowitt_http: AiohttpClient,
    sensor_key: str,
    expected_value: Any,
    request_data: dict[str, Any],
) -> None:
    """Test sensor is correct handled."""
    target_sensor = None

    def on_change(sensor: EcoWittSensor) -> None:
        """Test callback."""
        if sensor.key == sensor_key:
            nonlocal target_sensor
            target_sensor = sensor

    ecowitt_server.new_sensor_cb.append(on_change)

    resp = await ecowitt_http.post("/", data=request_data)
    assert resp.status == 200
    text = await resp.text()
    assert text == "OK"

    assert target_sensor
    assert target_sensor.value == expected_value
