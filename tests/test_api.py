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
    async def test_temperature_conversion(self, api):
        """Test temperature conversion methods."""
        # Test Celsius to Fahrenheit
        result = api._convert_temperature("20.0", "0")
        assert result == "68.0"
        
        # Test Celsius (no conversion)
        result = api._convert_temperature("20.0", "1")
        assert result == "20.0"
        
        # Test empty value
        result = api._convert_temperature("--", "0")
        assert result == "--"
        
        # Test invalid value
        result = api._convert_temperature("invalid", "0")
        assert result == ""

    @pytest.mark.asyncio
    async def test_battery_conversion(self, api):
        """Test battery level conversion."""
        # Test percentage conversion
        result = api._convert_battery("3", "", "1")
        assert result == "60%"
        
        # Test DC value
        result = api._convert_battery("6", "", "1")
        assert result == "DC"
        
        # Test binary battery
        result = api._convert_battery("0", "", "binary")
        assert result == "Normal"
        
        result = api._convert_battery("1", "", "binary")
        assert result == "Low"
        
        # Test empty value
        result = api._convert_battery("--", "", "1")
        assert result == "--"

    @pytest.mark.asyncio
    async def test_is_valid_float(self, api):
        """Test float validation."""
        assert api._is_valid_float("20.5") is True
        assert api._is_valid_float("20") is True
        assert api._is_valid_float("invalid") is False
        assert api._is_valid_float(None) is False
        assert api._is_valid_float("") is False

    @pytest.mark.asyncio
    async def test_get_all_data_structure(self, api):
        """Test that get_all_data returns properly structured data."""
        # Mock all required API endpoints
        mock_responses = {
            "get_version": {"version": "GW1100A_V1.7.0"},
            "get_device_info": {"apName": "Test Station"},
            "get_network_info": {"mac": "AA:BB:CC:DD:EE:FF"},
            "get_livedata_info": {
                "wh25": [{"intemp": "22.0", "inhumi": "45%", "rel": "1013.2", "abs": "1013.2"}],
                "common_list": [
                    {"id": "0x02", "val": "25.0"},
                    {"id": "0x07", "val": "60%"},
                ],
                "rain": [],
                "piezoRain": [],
                "console": [{"battery": "3"}],
                "co2": [],
                "lightning": [],
                "ch_pm25": [],
                "ch_leak": [],
                "ch_aisle": [],
                "ch_soil": [],
                "ch_temp": [],
                "ch_leaf": [],
                "ch_lds": [],
            },
            "get_units_info": {
                "temperature": "1",
                "pressure": "0", 
                "wind": "0",
                "rain": "0",
                "light": "0",
            },
            "get_sensors_info?page=1": [],
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
        
        # Check that weather data structure is populated
        assert data.weather_data.tempinf == "22.0"
        assert data.weather_data.humidityin == "45"
        assert data.weather_data.tempf == "25.0"
        assert data.weather_data.humidity == "60"
        
        # Check that all required data structures exist
        assert hasattr(data, "channel_sensors")
        assert hasattr(data, "sensor_diagnostics") 
        assert hasattr(data, "iot_devices")
        assert isinstance(data.iot_devices, list)
        
        # Test data model methods
        device_dict = data.device_info.to_dict()
        assert device_dict["version"] == "V1.7.0"
        
        # Test from_dict creation
        new_device = DeviceInfo.from_dict(device_dict)
        assert new_device.version == "V1.7.0"