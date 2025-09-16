"""Async EcoWitt API client."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .errors import RequestError
from .models import (
    ChannelSensors,
    DeviceInfo,
    EcoWittDeviceData,
    IoTDevice,
    SensorDiagnostics,
    WeatherData,
    WittiotDataTypes,
)

_LOGGER = logging.getLogger(__name__)

# API endpoints
GW11268_API_LIVEDATA = "get_livedata_info"
GW11268_API_UNIT = "get_units_info"
GW11268_API_VER = "get_version"
GW11268_API_SENID_1 = "get_sensors_info?page=1"
GW11268_API_SENID_2 = "get_sensors_info?page=2"
GW11268_API_SYS = "get_device_info"
GW11268_API_MAC = "get_network_info"
GW11268_API_IOTINFO = "get_iot_device_list"
GW11268_API_READIOT = "parse_quick_cmd_iot"

DEFAULT_TIMEOUT = 20

# Sensor type mappings
IOT_MAP = {
    1: "WFC01",
    2: "AC1100", 
    3: "WFC02",
}

RUN_MAP = {
    "WFC01": "water_running",
    "WFC02": "water_running", 
    "AC1100": "ac_running",
}

FORMAT_DATA_MAP = {
    "WFC01": ["happen_water", "water_total", "flow_velocity", "water_action", "water_temp"],
    "WFC02": ["happen_water", "wfc02_total", "wfc02_flow_velocity", "water_action", "water_temp"],
    "AC1100": ["happen_elect", "elect_total", "realtime_power", "ac_action", "ac_voltage"],
}

WFC_MAP = {
    "WFC01": ["rssi", "flow_velocity", "water_status", "water_total", "wfc01batt"],
    "WFC02": ["wfc02rssi", "wfc02_flow_velocity", "wfc02_status", "wfc02_total", "wfc02batt"],
    "AC1100": ["rssi"],
}


class EcoWittApi:
    """Async EcoWitt API client."""

    def __init__(
        self,
        host: str,
        *,
        session: ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the API client."""
        self._host = host
        self._session = session
        self._timeout = timeout
        self._unit_temp = "0"  # Default to Celsius

    async def _request(
        self,
        endpoint: str,
        ignore_errors: tuple[int, ...] = (404, 405),
    ) -> dict[str, Any]:
        """Make a GET request to the API."""
        url = f"http://{self._host}/{endpoint}"
        
        if self._session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=self._timeout))

        try:
            async with session.get(url) as resp:
                if resp.status in ignore_errors:
                    _LOGGER.debug("Endpoint not available (ignored): %s", url)
                    return {}
                resp.raise_for_status()
                data = await resp.json(content_type=None)
                _LOGGER.debug("Received data from %s: %s", url, data)
                return data
        except ClientError as err:
            if hasattr(err, "status") and err.status in ignore_errors:
                _LOGGER.debug("Endpoint not available (ignored): %s", url)
                return {}
            raise RequestError(f"Error requesting data from {url}: {err}") from err
        finally:
            if not self._session:
                await session.close()

    async def _post_request(
        self,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request to the API."""
        url = f"http://{self._host}/{endpoint}"
        
        if self._session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=self._timeout))

        try:
            kwargs = {}
            if payload:
                kwargs["json"] = payload
            if params:
                kwargs["params"] = params

            async with session.post(url, **kwargs) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
                _LOGGER.debug("POST response from %s: %s", url, data)
                return data
        except ClientError as err:
            error_msg = f"Error POSTing data to {url}: {err}"
            _LOGGER.error(error_msg)
            raise RequestError(error_msg) from err
        finally:
            if not self._session:
                await session.close()

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        """Safely convert value to float."""
        if value is None or value == "" or value == "--" or value == "--.-":
            return None
        try:
            # Remove common units and suffixes
            if isinstance(value, str):
                cleaned = (value.replace("%", "").replace("°", "").replace("V", "")
                          .replace("hPa", "").replace("inHg", "").replace("mmHg", "")
                          .replace("mm", "").replace("in", "").replace("mph", "")
                          .replace("m/s", "").replace("km/h", "").replace("W/m2", ""))
                if cleaned.strip() == "" or cleaned.strip() in ("--", "--.-", "---.-"):
                    return None
                return float(cleaned)
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_int(value: Any) -> int | None:
        """Safely convert value to int."""
        if value is None or value == "" or value == "--" or value == "--.-":
            return None
        try:
            if isinstance(value, str):
                cleaned = value.replace("°", "").strip()
                if cleaned == "" or cleaned in ("--", "--.-", "---.-"):
                    return None
                return int(float(cleaned))
            return int(value)
        except (ValueError, TypeError):
            return None

    def _extract_iot_device_data(self, response: dict[str, Any], rfnet_state: int) -> dict[str, Any] | None:
        """Extract IoT device data from response."""
        if "command" not in response or not response["command"]:
            return None
        
        device_data = response["command"][0]
        result = {"nickname": device_data.get("nickname", "")}
        
        if rfnet_state == 0:
            return result
        
        iot_type = IOT_MAP.get(device_data["model"], "")
        is_wfc = device_data["model"] != 2
        
        if iot_type and iot_type in WFC_MAP:
            wfc_fields = WFC_MAP[iot_type]
            result["rssi"] = self._safe_int(device_data.get(wfc_fields[0], ""))
            
            if is_wfc and len(wfc_fields) > 4:
                battery = device_data.get(wfc_fields[4], "")
                result["iotbatt"] = battery  # Keep as string for now
            
            result["iot_running"] = device_data.get(RUN_MAP.get(iot_type, ""), "")
            result["run_time"] = self._safe_int(device_data.get("run_time", 0))
            
            if iot_type in FORMAT_DATA_MAP:
                format_fields = FORMAT_DATA_MAP[iot_type]
                if len(format_fields) > 2:
                    result[format_fields[2]] = self._safe_float(device_data.get(format_fields[2], ""))
                
                # Calculate total
                if len(format_fields) > 1:
                    happen = self._safe_float(device_data.get(format_fields[0], 0)) or 0
                    total = self._safe_float(device_data.get(format_fields[1], 0)) or 0
                    result["velocity_total" if is_wfc else "elect_total"] = total - happen
                
                # Temperature data for water devices
                if is_wfc and len(format_fields) > 4 and format_fields[4] in device_data:
                    result["data_water_t"] = self._safe_float(device_data[format_fields[4]])
                
                # AC voltage for electric devices
                if not is_wfc and len(format_fields) > 4 and format_fields[4] in device_data:
                    result["data_ac_v"] = self._safe_float(device_data[format_fields[4]])
        
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}

    async def get_device_info(self) -> DeviceInfo:
        """Get device information."""
        version_data = await self._request(GW11268_API_VER)
        system_data = await self._request(GW11268_API_SYS)
        network_data = await self._request(GW11268_API_MAC)
        
        return DeviceInfo(
            version=version_data.get("version", "")[9:],  # Remove prefix
            dev_name=system_data.get("apName", ""),
            mac=network_data.get("mac", ""),
        )

    async def get_all_data(self) -> EcoWittDeviceData:
        """Get all device data grouped for Home Assistant."""
        # Get basic device info
        device_info = await self.get_device_info()
        
        # Get all data endpoints
        live_data = await self._request(GW11268_API_LIVEDATA)
        unit_data = await self._request(GW11268_API_UNIT)
        sensor_data_1 = await self._request(GW11268_API_SENID_1)
        sensor_data_2 = await self._request(GW11268_API_SENID_2)
        iot_list = await self._request(GW11268_API_IOTINFO)
        
        # Parse data directly into structured models
        weather_data = self._parse_weather_data(live_data, device_info)
        channel_sensors = self._parse_channel_sensors(live_data)
        sensor_diagnostics = self._parse_sensor_diagnostics(sensor_data_1, sensor_data_2)
        iot_devices = await self._parse_iot_devices(iot_list)
        
        return EcoWittDeviceData(
            device_info=device_info,
            weather_data=weather_data,
            channel_sensors=channel_sensors,
            sensor_diagnostics=sensor_diagnostics,
            iot_devices=iot_devices,
        )

    def _parse_weather_data(
        self,
        live_data: dict[str, Any],
        device_info: DeviceInfo,
    ) -> WeatherData:
        """Parse weather data from live data response."""
        weather = WeatherData()
        
        # Set device info
        weather.ver = device_info.version
        weather.devname = device_info.dev_name
        weather.mac = device_info.mac
        
        # Parse WH25 (indoor) data
        if "wh25" in live_data and live_data["wh25"]:
            wh25_data = live_data["wh25"][0]
            weather.tempinf = self._safe_float(wh25_data.get("intemp"))
            weather.humidityin = self._safe_float(wh25_data.get("inhumi"))
            weather.baromrelin = self._safe_float(wh25_data.get("rel"))
            weather.baromabsin = self._safe_float(wh25_data.get("abs"))
            weather.co2in = self._safe_int(wh25_data.get("CO2"))
            weather.co2in_24h = self._safe_int(wh25_data.get("CO2_24H"))
        
        # Parse common outdoor sensors
        if "common_list" in live_data:
            for item in live_data["common_list"]:
                sensor_id = item.get("id")
                value = item.get("val")
                
                if sensor_id == "0x02":
                    weather.tempf = self._safe_float(value)
                elif sensor_id == "0x07":
                    weather.humidity = self._safe_float(value)
                elif sensor_id == "0x03":
                    weather.dewpoint = self._safe_float(value)
                elif sensor_id == "0x0A":
                    weather.winddir = self._safe_int(value)
                elif sensor_id == "0x0B":
                    weather.windspeedmph = self._safe_float(value)
                elif sensor_id == "0x0C":
                    weather.windgustmph = self._safe_float(value)
                elif sensor_id == "0x15":
                    weather.solarradiation = self._safe_float(value)
                elif sensor_id == "0x17":
                    weather.uv = self._safe_float(value)
                elif sensor_id == "0x19":
                    weather.daywindmax = self._safe_float(value)
                elif sensor_id == "3":
                    weather.feellike = self._safe_float(value)
                elif sensor_id == "0x6D":
                    weather.winddir10 = self._safe_int(value)
                elif sensor_id == "4":
                    weather.apparent = self._safe_float(value)
                elif sensor_id == "5":
                    weather.vpd = self._safe_float(value)
        
        # Parse rain data
        if "rain" in live_data:
            for item in live_data["rain"]:
                sensor_id = item.get("id")
                value = item.get("val")
                
                if sensor_id == "0x0D":
                    weather.eventrainin = self._safe_float(value)
                elif sensor_id == "0x0E":
                    weather.rainratein = self._safe_float(value)
                elif sensor_id == "0x10":
                    weather.dailyrainin = self._safe_float(value)
                elif sensor_id == "0x11":
                    weather.weeklyrainin = self._safe_float(value)
                elif sensor_id == "0x12":
                    weather.monthlyrainin = self._safe_float(value)
                elif sensor_id == "0x13":
                    weather.yearlyrainin = self._safe_float(value)
                elif sensor_id == "0x14":
                    weather.totalrainin = self._safe_float(value)
                elif sensor_id == "0x7C":
                    weather.h24rainin = self._safe_float(value)
        
        # Parse piezo rain data
        if "piezoRain" in live_data:
            for item in live_data["piezoRain"]:
                sensor_id = item.get("id")
                value = item.get("val")
                
                if sensor_id == "0x0D":
                    weather.erain_piezo = self._safe_float(value)
                elif sensor_id == "0x0E":
                    weather.rrain_piezo = self._safe_float(value)
                elif sensor_id == "0x10":
                    weather.drain_piezo = self._safe_float(value)
                elif sensor_id == "0x11":
                    weather.wrain_piezo = self._safe_float(value)
                elif sensor_id == "0x12":
                    weather.mrain_piezo = self._safe_float(value)
                elif sensor_id == "0x13":
                    weather.yrain_piezo = self._safe_float(value)
                    weather.piezora_batt = self._safe_int(item.get("battery"))
                elif sensor_id == "0x14":
                    weather.train_piezo = self._safe_float(value)
                elif sensor_id == "0x7C":
                    weather.h24rain_piezo = self._safe_float(value)
                elif sensor_id == "srain_piezo":
                    weather.srain_piezo = "Raining" if value and str(value) != "0" else "No rain"
        
        # Parse console data
        if "console" in live_data and live_data["console"]:
            console_data = live_data["console"][0]
            weather.con_batt = self._safe_int(console_data.get("battery"))
            weather.con_batt_volt = self._safe_float(console_data.get("console_batt_volt"))
            weather.con_ext_volt = self._safe_float(console_data.get("console_ext_volt"))
        
        # Parse CO2 data
        if "co2" in live_data and live_data["co2"]:
            co2_data = live_data["co2"][0]
            weather.co2 = self._safe_int(co2_data.get("CO2"))
            weather.co2_24h = self._safe_int(co2_data.get("CO2_24H"))
            weather.pm25_co2 = self._safe_float(co2_data.get("PM25"))
            weather.pm25_24h_co2 = self._safe_float(co2_data.get("PM25_24H"))
            weather.pm10_co2 = self._safe_float(co2_data.get("PM10"))
            weather.pm10_24h_co2 = self._safe_float(co2_data.get("PM10_24H"))
            weather.pm10_aqi_co2 = self._safe_int(co2_data.get("PM10_RealAQI"))
            weather.pm25_aqi_co2 = self._safe_int(co2_data.get("PM25_RealAQI"))
            weather.tf_co2 = self._safe_float(co2_data.get("temp"))
            weather.humi_co2 = self._safe_float(co2_data.get("humidity"))
        
        # Parse lightning data
        if "lightning" in live_data and live_data["lightning"]:
            lightning_data = live_data["lightning"][0]
            weather.lightning = self._safe_float(lightning_data.get("distance"))
            weather.lightning_time = lightning_data.get("timestamp")
            weather.lightning_num = self._safe_int(lightning_data.get("count"))
        
        return weather

    def _convert_solar_radiation(self, val: str | None, unit: str) -> str | None:
        """Convert solar radiation based on unit."""
        if not val or val in ("", "--", "--.-", "---.-"):
            return val
        
        cleaned = val.replace("W/m2", "").replace("Kfc", "").replace("Klux", "")
        if not self._is_valid_float(cleaned):
            return ""
        
        val_float = float(cleaned)
        if unit == "0":
            return str(round(val_float * 1000 / 126.7, 2))
        elif unit == "1":
            return cleaned
        else:
            return str(round(val_float * 1000 * 10.76391 / 126.7, 2))

    def _convert_lightning_distance(self, val: str | None, unit: str) -> str | None:
        """Convert lightning distance based on unit."""
        if not val or val in ("", "--", "--.-", "---.-"):
            return val
        
        cleaned = val.replace("km", "").replace("nmi", "").replace("mi", "")
        if not self._is_valid_float(cleaned):
            return ""
        
        val_float = float(cleaned)
        if unit in ("0", "1", "2"):
            return str(round(val_float * 0.62137, 1))
        else:
            return str(round(val_float / 0.53996 * 0.62137, 1))

    def _parse_channel_sensors(self, live_data: dict[str, Any]) -> ChannelSensors:
        """Parse channel-based sensors from live data."""
        sensors = ChannelSensors()
        
        # Parse PM2.5 channels
        if "ch_pm25" in live_data:
            for item in live_data["ch_pm25"]:
                channel = item.get("channel")
                if channel == "1":
                    sensors.pm25_ch1 = self._safe_float(item.get("PM25"))
                    sensors.pm25_24h_ch1 = self._safe_float(item.get("PM25_24H"))
                    sensors.pm25_aqi_ch1 = self._safe_int(item.get("PM25_RealAQI"))
                elif channel == "2":
                    sensors.pm25_ch2 = self._safe_float(item.get("PM25"))
                    sensors.pm25_24h_ch2 = self._safe_float(item.get("PM25_24H"))
                    sensors.pm25_aqi_ch2 = self._safe_int(item.get("PM25_RealAQI"))
                elif channel == "3":
                    sensors.pm25_ch3 = self._safe_float(item.get("PM25"))
                    sensors.pm25_24h_ch3 = self._safe_float(item.get("PM25_24H"))
                    sensors.pm25_aqi_ch3 = self._safe_int(item.get("PM25_RealAQI"))
                elif channel == "4":
                    sensors.pm25_ch4 = self._safe_float(item.get("PM25"))
                    sensors.pm25_24h_ch4 = self._safe_float(item.get("PM25_24H"))
                    sensors.pm25_aqi_ch4 = self._safe_int(item.get("PM25_RealAQI"))
        
        # Parse leak sensors
        if "ch_leak" in live_data:
            for item in live_data["ch_leak"]:
                channel = item.get("channel")
                status = item.get("status")
                if channel == "1":
                    sensors.leak_ch1 = status
                elif channel == "2":
                    sensors.leak_ch2 = status
                elif channel == "3":
                    sensors.leak_ch3 = status
                elif channel == "4":
                    sensors.leak_ch4 = status
        
        # Parse temperature & humidity channels
        if "ch_aisle" in live_data:
            for item in live_data["ch_aisle"]:
                channel = int(item.get("channel", 0))
                temp = self._safe_float(item.get("temp"))
                humidity = self._safe_float(item.get("humidity"))
                
                if channel == 1:
                    sensors.temp_ch1 = temp
                    sensors.humidity_ch1 = humidity
                elif channel == 2:
                    sensors.temp_ch2 = temp
                    sensors.humidity_ch2 = humidity
                elif channel == 3:
                    sensors.temp_ch3 = temp
                    sensors.humidity_ch3 = humidity
                elif channel == 4:
                    sensors.temp_ch4 = temp
                    sensors.humidity_ch4 = humidity
                elif channel == 5:
                    sensors.temp_ch5 = temp
                    sensors.humidity_ch5 = humidity
                elif channel == 6:
                    sensors.temp_ch6 = temp
                    sensors.humidity_ch6 = humidity
                elif channel == 7:
                    sensors.temp_ch7 = temp
                    sensors.humidity_ch7 = humidity
                elif channel == 8:
                    sensors.temp_ch8 = temp
                    sensors.humidity_ch8 = humidity
        
        # Parse soil moisture
        if "ch_soil" in live_data:
            for item in live_data["ch_soil"]:
                channel = int(item.get("channel", 0))
                humidity = self._safe_float(item.get("humidity"))
                
                if channel == 1:
                    sensors.soilmoisture_ch1 = humidity
                elif channel == 2:
                    sensors.soilmoisture_ch2 = humidity
                elif channel == 3:
                    sensors.soilmoisture_ch3 = humidity
                elif channel == 4:
                    sensors.soilmoisture_ch4 = humidity
                elif channel == 5:
                    sensors.soilmoisture_ch5 = humidity
                elif channel == 6:
                    sensors.soilmoisture_ch6 = humidity
                elif channel == 7:
                    sensors.soilmoisture_ch7 = humidity
                elif channel == 8:
                    sensors.soilmoisture_ch8 = humidity
                elif channel == 9:
                    sensors.soilmoisture_ch9 = humidity
                elif channel == 10:
                    sensors.soilmoisture_ch10 = humidity
                elif channel == 11:
                    sensors.soilmoisture_ch11 = humidity
                elif channel == 12:
                    sensors.soilmoisture_ch12 = humidity
                elif channel == 13:
                    sensors.soilmoisture_ch13 = humidity
                elif channel == 14:
                    sensors.soilmoisture_ch14 = humidity
                elif channel == 15:
                    sensors.soilmoisture_ch15 = humidity
                elif channel == 16:
                    sensors.soilmoisture_ch16 = humidity
        
        # Parse temperature-only channels
        if "ch_temp" in live_data:
            for item in live_data["ch_temp"]:
                channel = int(item.get("channel", 0))
                temp = self._safe_float(item.get("temp"))
                
                if channel == 1:
                    sensors.tf_ch1 = temp
                elif channel == 2:
                    sensors.tf_ch2 = temp
                elif channel == 3:
                    sensors.tf_ch3 = temp
                elif channel == 4:
                    sensors.tf_ch4 = temp
                elif channel == 5:
                    sensors.tf_ch5 = temp
                elif channel == 6:
                    sensors.tf_ch6 = temp
                elif channel == 7:
                    sensors.tf_ch7 = temp
                elif channel == 8:
                    sensors.tf_ch8 = temp
        
        # Parse leaf wetness
        if "ch_leaf" in live_data:
            for item in live_data["ch_leaf"]:
                channel = int(item.get("channel", 0))
                humidity = self._safe_float(item.get("humidity"))
                
                if channel == 1:
                    sensors.leaf_ch1 = humidity
                elif channel == 2:
                    sensors.leaf_ch2 = humidity
                elif channel == 3:
                    sensors.leaf_ch3 = humidity
                elif channel == 4:
                    sensors.leaf_ch4 = humidity
                elif channel == 5:
                    sensors.leaf_ch5 = humidity
                elif channel == 6:
                    sensors.leaf_ch6 = humidity
                elif channel == 7:
                    sensors.leaf_ch7 = humidity
                elif channel == 8:
                    sensors.leaf_ch8 = humidity
        
        # Parse LDS sensors
        if "ch_lds" in live_data:
            for item in live_data["ch_lds"]:
                channel = int(item.get("channel", 0))
                air = self._safe_float(item.get("air"))
                depth = self._safe_float(item.get("depth"))
                heat = self._safe_int(item.get("total_heat"))
                height = self._safe_float(item.get("total_height"))
                
                if channel == 1:
                    sensors.lds_air_ch1 = air
                    sensors.lds_depth_ch1 = depth
                    sensors.lds_heat_ch1 = heat
                    sensors.lds_height_ch1 = height
                elif channel == 2:
                    sensors.lds_air_ch2 = air
                    sensors.lds_depth_ch2 = depth
                    sensors.lds_heat_ch2 = heat
                    sensors.lds_height_ch2 = height
                elif channel == 3:
                    sensors.lds_air_ch3 = air
                    sensors.lds_depth_ch3 = depth
                    sensors.lds_heat_ch3 = heat
                    sensors.lds_height_ch3 = height
                elif channel == 4:
                    sensors.lds_air_ch4 = air
                    sensors.lds_depth_ch4 = depth
                    sensors.lds_heat_ch4 = heat
                    sensors.lds_height_ch4 = height
        
        return sensors

    def _convert_distance(self, val: str | None, unit: str) -> str | None:
        """Convert distance measurement."""
        if not val or val in ("", "--", "--.-", "---.-"):
            return val
        
        cleaned = val.replace("mm", "").replace("ft", "")
        if not self._is_valid_float(cleaned):
            return ""
        
        val_float = float(cleaned)
        if unit == "0":  # Convert to feet
            return str(round(val_float / 304.8, 2))
        return cleaned

    def _parse_sensor_diagnostics(
        self,
        sensor_data_1: dict[str, Any],
        sensor_data_2: dict[str, Any],
    ) -> SensorDiagnostics:
        """Parse sensor diagnostic data."""
        diagnostics = SensorDiagnostics()
        
        # Combine sensor data
        all_sensor_data = []
        if isinstance(sensor_data_1, list):
            all_sensor_data.extend(sensor_data_1)
        if isinstance(sensor_data_2, list):
            all_sensor_data.extend(sensor_data_2)
        
        # Map sensor types to diagnostic fields
        sensor_mapping = {
            22: "pm25_ch1", 23: "pm25_ch2", 24: "pm25_ch3", 25: "pm25_ch4",
            27: "leak_ch1", 28: "leak_ch2", 29: "leak_ch3", 30: "leak_ch4",
            49: "wh85", 48: "wh90", 0: "wh69", 1: "wh68", 3: "wh40",
            4: "wh25", 5: "wh26", 2: "wh80", 26: "wh57", 39: "wh45",
        }
        
        for sensor in all_sensor_data:
            sensor_type = int(sensor.get("type", -1))
            if sensor_type in sensor_mapping:
                base_name = sensor_mapping[sensor_type]
                
                # Skip invalid sensors
                if sensor.get("id") in ("FFFFFFFF", "FFFFFFFE"):
                    continue
                
                # Set battery, RSSI, and signal
                setattr(diagnostics, f"{base_name}_batt", self._safe_int(sensor.get("batt")))
                setattr(diagnostics, f"{base_name}_rssi", self._safe_int(sensor.get("rssi")))
                setattr(diagnostics, f"{base_name}_signal", self._safe_int(sensor.get("signal")))
        
        return diagnostics

    async def _parse_iot_devices(self, iot_list: dict[str, Any]) -> list[IoTDevice]:
        """Parse IoT devices from the list."""
        devices = []
        
        if not iot_list or "command" not in iot_list:
            return devices
        
        for device_data in iot_list["command"]:
            # Update device with current status
            updated_device = await self._update_iot_device(device_data)
            if updated_device:
                devices.append(IoTDevice.from_dict(updated_device))
        
        return devices

    async def _update_iot_device(self, device_data: dict[str, Any]) -> dict[str, Any] | None:
        """Update IoT device with current status."""
        if device_data.get("rfnet_state") == 0:
            return {
                "id": device_data.get("id", 0),
                "model": device_data.get("model", 0),
                "nickname": device_data.get("nickname", ""),
                "rfnet_state": 0,
            }
        
        # Get current device status
        payload = {
            "command": [{
                "cmd": "read_device",
                "id": device_data["id"],
                "model": device_data["model"],
            }]
        }
        
        try:
            response = await self._post_request(GW11268_API_READIOT, payload=payload)
            extracted_data = self._extract_iot_device_data(response, device_data["rfnet_state"])
            
            if extracted_data:
                # Merge with original device data
                result = {
                    "id": device_data.get("id", 0),
                    "model": device_data.get("model", 0),
                    "rfnet_state": device_data.get("rfnet_state", 0),
                }
                result.update(extracted_data)
                return result
        except Exception as err:
            _LOGGER.debug("Failed to update device status: %s", err)
        
        return None

    async def control_iot_device(self, device_id: int, model: int, switch_on: bool) -> dict[str, Any] | None:
        """Control an IoT device (turn on/off)."""
        if switch_on:
            if model == 3:  # WFC02
                cmd = {
                    "position": 100,
                    "always_on": 1,
                    "val_type": 1,
                    "val": 0,
                    "cmd": "quick_run",
                    "id": device_id,
                    "model": model,
                }
            else:
                cmd = {
                    "on_type": 0,
                    "off_type": 0,
                    "always_on": 1,
                    "on_time": 0,
                    "off_time": 0,
                    "val_type": 1,
                    "val": 0,
                    "cmd": "quick_run",
                    "id": device_id,
                    "model": model,
                }
        else:
            cmd = {
                "cmd": "quick_stop",
                "id": device_id,
                "model": model,
            }
        
        payload = {"command": [cmd]}
        
        try:
            return await self._post_request(GW11268_API_READIOT, payload=payload)
        except Exception as err:
            _LOGGER.debug("Failed to control device: %s", err)
            return None