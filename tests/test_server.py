"""EcoWitt server tests."""

import pytest
from pytest_aiohttp import AiohttpClient

from aioecowitt import EcoWittSensorTypes, server

from .const import EASYWEATHER_DATA, GW2000A_DATA

# pylint: disable=redefined-outer-name


async def test_server_start(
    ecowitt_server: server.EcoWittListener, ecowitt_http: AiohttpClient
) -> None:
    """Test server start."""
    sensors = []

    def on_change(sensor: server.EcoWittSensor) -> None:
        """Test callback."""
        sensors.append(sensor)

    ecowitt_server.new_sensor_cb.append(on_change)

    resp = await ecowitt_http.post("/", data=GW2000A_DATA)
    assert resp.status == 200
    text = await resp.text()
    assert text == "OK"

    assert len(sensors) == 52
    assert len(ecowitt_server.sensors) == 52
    assert len(ecowitt_server.stations) == 1

    assert "PASSKEY" not in ecowitt_server.last_values[GW2000A_DATA["PASSKEY"]]


async def test_server_token(
    ecowitt_server: server.EcoWittListener, ecowitt_http: AiohttpClient
) -> None:
    """Test server start."""
    sensors = []
    path = "/test"
    ecowitt_server.path = path

    def on_change(sensor: server.EcoWittSensor) -> None:
        """Test callback."""
        sensors.append(sensor)

    ecowitt_server.new_sensor_cb.append(on_change)

    resp = await ecowitt_http.post("/", data=GW2000A_DATA)
    assert resp.status == 404

    resp = await ecowitt_http.post(path, data=GW2000A_DATA)
    assert resp.status == 200
    text = await resp.text()
    assert text == "OK"

    assert len(sensors) == 52
    assert len(ecowitt_server.sensors) == 52
    assert len(ecowitt_server.stations) == 1


async def test_server_multi_stations(
    ecowitt_server: server.EcoWittListener, ecowitt_http: AiohttpClient
) -> None:
    """Test server start and multiple stations."""
    sensors = []

    def on_change(sensor: server.EcoWittSensor) -> None:
        """Test callback."""
        sensors.append(sensor)

    ecowitt_server.new_sensor_cb.append(on_change)

    resp = await ecowitt_http.post("/", data=GW2000A_DATA)
    assert resp.status == 200
    text = await resp.text()
    assert text == "OK"

    resp = await ecowitt_http.post("/", data=EASYWEATHER_DATA)
    assert resp.status == 200
    text = await resp.text()
    assert text == "OK"

    assert len(sensors) == 91
    assert len(ecowitt_server.sensors) == 91
    assert len(ecowitt_server.stations) == 2


async def test_server_firmware_version(
    ecowitt_server: server.EcoWittListener,
    ecowitt_http: AiohttpClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the WS85 firmware version field is handled.

    ``ws85_ver`` is diagnostic information rather than a measurement, so it is
    mapped as INTERNAL instead of being reported as an unhandled sensor type.
    See #425.
    """
    data = {**GW2000A_DATA, "ws85_ver": "118"}
    resp = await ecowitt_http.post("/", data=data)
    assert resp.status == 200

    assert "Unhandled sensor type ws85_ver" not in caplog.text

    sensor = next(s for s in ecowitt_server.sensors.values() if s.key == "ws85_ver")
    assert sensor.stype is EcoWittSensorTypes.INTERNAL
    assert sensor.value == "118"
