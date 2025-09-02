"""Configuration."""

import pytest
from pytest_aiohttp import AiohttpClient, AiohttpRawServer

from aioecowitt import server


@pytest.fixture(name="ecowitt_server")
def ecowitt_server_fixture() -> server.EcoWittListener:
    """EcoWitt server fixture."""
    return server.EcoWittListener()


@pytest.fixture
async def ecowitt_http(
    aiohttp_raw_server: AiohttpRawServer,
    aiohttp_client: AiohttpClient,
    ecowitt_server: server.EcoWittListener,
) -> AiohttpClient:
    """EcoWitt HTTP fixture."""
    raw_server = await aiohttp_raw_server(ecowitt_server.handler)
    return await aiohttp_client(raw_server)
