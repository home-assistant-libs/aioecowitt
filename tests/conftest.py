import pytest

from aioecowitt import server


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
