import pytest

from aioecowitt import server


@pytest.fixture
def ecowitt_server():
    """EcoWitt server fixture."""
    ecowitt_server = server.EcoWittListener()
    yield ecowitt_server


@pytest.fixture
async def ecowitt_http(aiohttp_raw_server, aiohttp_client, ecowitt_server):
    """EcoWitt HTTP fixture."""
    raw_server = await aiohttp_raw_server(ecowitt_server.handler)
    return await aiohttp_client(raw_server)
