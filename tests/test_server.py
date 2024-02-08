"""EcoWitt server tests."""

import pytest

from aioecowitt import server

from .const import GW2000A_DATA, EASYWEATHER_DATA

# pylint: disable=redefined-outer-name


@pytest.mark.asyncio
async def test_server_start(ecowitt_server, ecowitt_http) -> None:
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

    assert len(sensors) == 51
    assert len(ecowitt_server.sensors) == 51
    assert len(ecowitt_server.stations) == 1

    assert "PASSKEY" not in ecowitt_server.last_values[GW2000A_DATA["PASSKEY"]]


@pytest.mark.asyncio
async def test_server_token(ecowitt_server, ecowitt_http) -> None:
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

    assert len(sensors) == 51
    assert len(ecowitt_server.sensors) == 51
    assert len(ecowitt_server.stations) == 1


@pytest.mark.asyncio
async def test_server_multi_stations(ecowitt_server, ecowitt_http) -> None:
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

    assert len(sensors) == 90
    assert len(ecowitt_server.sensors) == 90
    assert len(ecowitt_server.stations) == 2
