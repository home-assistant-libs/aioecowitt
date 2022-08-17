"""EcoWitt server tests."""

import pytest

from aioecowitt import server

from .const import GW2000A_DATA, EASYWEATHER_DATA

# pylint: disable=redefined-outer-name


@pytest.fixture
def ecowitt_server():
    """EcoWitt server fixture."""
    ecowitt_server = server.EcoWittListener()
    yield ecowitt_server


@pytest.fixture
def ecowitt_http(event_loop, aiohttp_raw_server, aiohttp_client, ecowitt_server):
    """EcoWitt HTTP fixture."""
    raw_server = event_loop.run_until_complete(
        aiohttp_raw_server(ecowitt_server.handler)
    )
    return event_loop.run_until_complete(aiohttp_client(raw_server))


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

    assert len(sensors) == 47
    assert len(ecowitt_server.sensors) == 47
    assert len(ecowitt_server.stations) == 1


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

    assert len(sensors) == 47
    assert len(ecowitt_server.sensors) == 47
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

    assert len(sensors) == 86
    assert len(ecowitt_server.sensors) == 86
    assert len(ecowitt_server.stations) == 2
