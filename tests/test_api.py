"""Test the EcoWitt API client."""

from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientError

from aioecowitt.api import EcoWittApi
from aioecowitt.errors import RequestError
from aioecowitt.models import DeviceInfo, EcoWittDeviceData


class TestEcoWittApi:
    """Test EcoWittApi class."""

    @pytest.fixture
    def api(self):
        """Create API instance for testing."""
        return EcoWittApi("192.168.1.100")

    @pytest.mark.asyncio
    async def test_init(self, api):
        """Test API initialization."""
        assert api._host == "192.168.1.100"
        assert api._timeout == 20
        assert api._session is None

    @pytest.mark.asyncio
    async def test_request_success(self, api):
        """Test successful API request."""
        mock_response = {"version": "GW1100A_V1.7.0", "api": "1.0"}
        
        with patch("aioecowitt.api.ClientSession") as mock_session:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status.return_value = None
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_resp
            
            result = await api._request("get_version")
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_request_error(self, api):
        """Test API request error handling."""
        with patch("aioecowitt.api.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = ClientError("Connection failed")
            
            with pytest.raises(RequestError, match="Error requesting data"):
                await api._request("get_version")

    @pytest.mark.asyncio
    async def test_request_ignored_error(self, api):
        """Test API request with ignored error codes."""
        with patch("aioecowitt.api.ClientSession") as mock_session:
            error = ClientError("Not found")
            error.status = 404
            mock_session.return_value.__aenter__.return_value.get.side_effect = error
            
            result = await api._request("get_version", ignore_errors=(404,))
            assert result == {}

    @pytest.mark.asyncio
    async def test_get_device_info(self, api):
        """Test getting device info."""
        mock_responses = {
            "get_version": {"version": "GW1100A_V1.7.0"},
            "get_device_info": {"apName": "My Weather Station"},
            "get_network_info": {"mac": "AA:BB:CC:DD:EE:FF"},
        }
        
        async def mock_request(endpoint, **kwargs):
            return mock_responses.get(endpoint, {})
        
        api._request = AsyncMock(side_effect=mock_request)
        
        device_info = await api.get_device_info()
        
        assert isinstance(device_info, DeviceInfo)
        assert device_info.version == "V1.7.0"
        assert device_info.dev_name == "My Weather Station"
        assert device_info.mac == "AA:BB:CC:DD:EE:FF"

    @pytest.mark.asyncio
    async def test_parse_value_and_unit(self, api):
        """Test value and unit parsing."""
        # Test temperature with space
        value, unit = api._parse_value_and_unit("20.7 C")
        assert value == "20.7"
        assert unit == "C"
        
        # Test percentage
        value, unit = api._parse_value_and_unit("58%")
        assert value == "58"
        assert unit == "%"
        
        # Test rain rate
        value, unit = api._parse_value_and_unit("0.0 mm/Hr")
        assert value == "0.0"
        assert unit == "mm/Hr"
        
        # Test pressure
        value, unit = api._parse_value_and_unit("1013.2hPa")
        assert value == "1013.2"
        assert unit == "hPa"
        
        # Test empty/invalid
        value, unit = api._parse_value_and_unit("--")
        assert value == "--"
        assert unit is None

    @pytest.mark.asyncio
    async def test_safe_conversions(self, api):
        """Test safe conversion methods."""
        # Test safe_int
        assert api._safe_int("20") == 20
        assert api._safe_int("20.5") == 20
        assert api._safe_int("--") is None
        assert api._safe_int("invalid") is None

    @pytest.mark.asyncio
    async def test_get_all_data_structure(self, api):
        """Test that get_all_data returns properly structured data."""
        # Mock all required API endpoints
        mock_responses = {
            "get_version": {"version": "GW1100A_V1.7.0"},
            "get_device_info": {"apName": "Test Station"},
            "get_network_info": {"mac": "AA:BB:CC:DD:EE:FF"},
            "get_livedata_info": {
                "common_list": [
                    {"id": "0x02", "val": "20.7 C"},
                    {"id": "0x07", "val": "58%"},
                ],
                "wh25": [{"intemp": "22.0", "unit": "C", "inhumi": "45%", "rel": "1013.2 hPa", "abs": "1013.2 hPa"}],
                "piezoRain": [
                    {"id": "0x0D", "val": "0.0 mm"},
                    {"id": "0x0E", "val": "0.0 mm/Hr"},
                ],
                "ch_lds": [
                    {
                        "channel": "1",
                        "name": "",
                        "unit": "mm", 
                        "battery": "5",
                        "voltage": "3.28",
                        "air": "1565 mm",
                        "depth": "--.-",
                        "total_height": "0",
                        "total_heat": "15"
                    }
                ]
            },
            "get_sensors_info?page=1": [
                {
                    "img": "wh54",
                    "type": "66",
                    "name": "Lds CH1",
                    "id": "2B77",
                    "batt": "5",
                    "rssi": "-62",
                    "signal": "4",
                    "idst": "1"
                }
            ],
            "get_sensors_info?page=2": [],
            "get_iot_device_list": {"command": []},
        }
        
        async def mock_request(endpoint, **kwargs):
            return mock_responses.get(endpoint, {})
        
        api._request = AsyncMock(side_effect=mock_request)
        
        data = await api.get_all_data()
        
        assert isinstance(data, EcoWittDeviceData)
        assert isinstance(data.device_info, DeviceInfo)
        assert data.device_info.version == "V1.7.0"
        assert data.device_info.dev_name == "Test Station"
        assert data.device_info.mac == "AA:BB:CC:DD:EE:FF"
        
        # Check that grouped structure is maintained
        assert hasattr(data, "common_list")
        assert hasattr(data, "wh25")
        assert hasattr(data, "piezoRain")
        assert hasattr(data, "ch_lds")
        assert hasattr(data, "sensors")
        assert isinstance(data.iot_devices, list)
        
        # Test that values and units are parsed correctly
        assert len(data.common_list) == 2
        assert data.common_list[0].id == "0x02"
        assert data.common_list[0].val == "20.7"
        assert data.common_list[0].unit == "C"
        assert data.common_list[1].val == "58"
        assert data.common_list[1].unit == "%"
        
        # Test WH25 data
        assert len(data.wh25) == 1
        assert data.wh25[0].intemp == "22.0"
        assert data.wh25[0].unit == "C"
        
        # Test LDS data with device ID mapping
        assert len(data.ch_lds) == 1
        assert data.ch_lds[0].channel == "1"
        assert data.ch_lds[0].device_id == "2B77"  # Mapped from sensor info
        
        # Test sensor filtering (configured sensors only)
        assert len(data.sensors) == 1
        assert data.sensors[0].id == "2B77"
        assert data.sensors[0].type == 66
        
        # Test mashumaro functionality
        device_dict = data.device_info.to_dict()
        assert device_dict["version"] == "V1.7.0"
        
        # Test from_dict creation
        new_device = DeviceInfo.from_dict(device_dict)
        assert new_device.version == "V1.7.0"