"""Async EcoWitt API client."""

from __future__ import annotations

import logging
import re
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .errors import RequestError
from .models import (
    CO2Sensor,
    CommonSensor,
    ConsoleSensor,
    DeviceInfo,
    EcoWittDeviceData,
    IoTDevice,
    LDSSensor,
    LeafSensor,
    LeakSensor,
    LightningSensor,
    PM25Sensor,
    PiezoRainSensor,
    RainSensor,
    SensorInfo,
    SoilSensor,
    TempHumiditySensor,
    TempSensor,
    WH25Data,
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
    def _parse_value_and_unit(value_str: str) -> tuple[str, str | None]:
        """Parse value and unit from a string like '20.7 C' or '58%'."""
        if not value_str or value_str in ("--", "--.-", "---.-"):
            return value_str, None
        
        # Handle percentage
        if value_str.endswith("%"):
            return value_str[:-1], "%"
        
        # Handle values with units separated by space
        parts = value_str.split()
        if len(parts) == 2:
            return parts[0], parts[1]
        
        # Handle values with units attached (like mm/Hr)
        for unit in ["mm/Hr", "in/Hr", "W/m2", "hPa", "inHg", "mmHg", "kPa", "m/s", "mph", "km/h", "knots", "ft/s", "mm", "in", "ft", "°C", "°F", "V"]:
            if value_str.endswith(unit):
                return value_str[:-len(unit)], unit
        
        return value_str, None

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
            rssi_val = device_data.get(wfc_fields[0], "")
            if rssi_val and rssi_val != "--":
                try:
                    result["rssi"] = int(rssi_val)
                except (ValueError, TypeError):
                    pass
            
            if is_wfc and len(wfc_fields) > 4:
                battery = device_data.get(wfc_fields[4], "")
                result["iotbatt"] = battery  # Keep as string for now
            
            result["iot_running"] = device_data.get(RUN_MAP.get(iot_type, ""), "")
            run_time = device_data.get("run_time", 0)
            if run_time:
                try:
                    result["run_time"] = int(run_time)
                except (ValueError, TypeError):
                    pass
            
            if iot_type in FORMAT_DATA_MAP:
                format_fields = FORMAT_DATA_MAP[iot_type]
                if len(format_fields) > 2:
                    velocity = device_data.get(format_fields[2], "")
                    if velocity:
                        try:
                            result[format_fields[2]] = float(velocity)
                        except (ValueError, TypeError):
                            pass
                
                # Calculate total
                if len(format_fields) > 1:
                    try:
                        happen = float(device_data.get(format_fields[0], 0) or 0)
                        total = float(device_data.get(format_fields[1], 0) or 0)
                        result["velocity_total" if is_wfc else "elect_total"] = total - happen
                    except (ValueError, TypeError):
                        pass
                
                # Temperature data for water devices
                if is_wfc and len(format_fields) > 4 and format_fields[4] in device_data:
                    temp_val = device_data[format_fields[4]]
                    if temp_val:
                        try:
                            result["data_water_t"] = float(temp_val)
                        except (ValueError, TypeError):
                            pass
                
                # AC voltage for electric devices
                if not is_wfc and len(format_fields) > 4 and format_fields[4] in device_data:
                    voltage_val = device_data[format_fields[4]]
                    if voltage_val:
                        try:
                            result["data_ac_v"] = float(voltage_val)
                        except (ValueError, TypeError):
                            pass
        
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
        """Get all device data keeping original grouped structure."""
        # Get basic device info
        device_info = await self.get_device_info()
        
        # Get all data endpoints
        live_data = await self._request(GW11268_API_LIVEDATA)
        sensor_data_1 = await self._request(GW11268_API_SENID_1)
        sensor_data_2 = await self._request(GW11268_API_SENID_2)
        iot_list = await self._request(GW11268_API_IOTINFO)
        
        # Parse sensor info
        sensors = self._parse_sensor_info(sensor_data_1, sensor_data_2)
        
        # Parse live data keeping grouped structure
        parsed_data = self._parse_live_data(live_data, sensors)
        
        # Parse IoT devices
        iot_devices = await self._parse_iot_devices(iot_list)
        
        return EcoWittDeviceData(
            device_info=device_info,
            sensors=sensors,
            iot_devices=iot_devices,
            **parsed_data,
        )

    def _parse_sensor_info(
        self,
        sensor_data_1: dict[str, Any],
        sensor_data_2: dict[str, Any],
    ) -> list[SensorInfo]:
        """Parse sensor configuration information."""
        sensors = []
        
        # Combine sensor data
        all_sensor_data = []
        if isinstance(sensor_data_1, list):
            all_sensor_data.extend(sensor_data_1)
        if isinstance(sensor_data_2, list):
            all_sensor_data.extend(sensor_data_2)
        
        for sensor in all_sensor_data:
            # Skip unconfigured devices
            if sensor.get("id") == "FFFFFFFF":
                continue
            
            sensor_info = SensorInfo(
                img=sensor.get("img", ""),
                type=int(sensor.get("type", -1)),
                name=sensor.get("name", ""),
                id=sensor.get("id", ""),
                batt=self._safe_int(sensor.get("batt")),
                rssi=self._safe_int(sensor.get("rssi")),
                signal=self._safe_int(sensor.get("signal")),
                version=sensor.get("version"),
                idst=sensor.get("idst"),
            )
            sensors.append(sensor_info)
        
        return sensors

    def _parse_live_data(
        self,
        live_data: dict[str, Any],
        sensors: list[SensorInfo],
    ) -> dict[str, Any]:
        """Parse live data keeping original grouped structure."""
        parsed = {}
        
        # Create device ID mapping for LDS sensors
        lds_device_map = {}
        for sensor in sensors:
            if sensor.type in (66, 67, 68, 69):  # LDS sensor types
                channel = str(sensor.type - 65)  # Convert type to channel
                lds_device_map[channel] = sensor.id
        
        # Parse common_list
        if "common_list" in live_data:
            common_sensors = []
            for item in live_data["common_list"]:
                value, unit = self._parse_value_and_unit(item.get("val", ""))
                sensor = CommonSensor(
                    id=item.get("id", ""),
                    val=value,
                    unit=unit,
                )
                common_sensors.append(sensor)
            parsed["common_list"] = common_sensors
        else:
            parsed["common_list"] = []
        
        # Parse rain data
        if "rain" in live_data and live_data["rain"]:
            rain_sensors = []
            for item in live_data["rain"]:
                value, unit = self._parse_value_and_unit(item.get("val", ""))
                sensor = RainSensor(
                    id=item.get("id", ""),
                    val=value,
                    unit=unit,
                )
                rain_sensors.append(sensor)
            parsed["rain"] = rain_sensors
        
        # Parse piezo rain data
        if "piezoRain" in live_data and live_data["piezoRain"]:
            piezo_sensors = []
            for item in live_data["piezoRain"]:
                value, unit = self._parse_value_and_unit(item.get("val", ""))
                sensor = PiezoRainSensor(
                    id=item.get("id", ""),
                    val=value,
                    unit=unit,
                    battery=item.get("battery"),
                    voltage=item.get("voltage"),
                    ws90cap_volt=item.get("ws90cap_volt"),
                    ws90_ver=item.get("ws90_ver"),
                )
                piezo_sensors.append(sensor)
            parsed["piezoRain"] = piezo_sensors
        
        # Parse WH25 data
        if "wh25" in live_data and live_data["wh25"]:
            wh25_list = []
            for item in live_data["wh25"]:
                sensor = WH25Data(
                    intemp=item.get("intemp", ""),
                    unit=item.get("unit", ""),
                    inhumi=item.get("inhumi", ""),
                    abs=item.get("abs", ""),
                    rel=item.get("rel", ""),
                    CO2=item.get("CO2"),
                    CO2_24H=item.get("CO2_24H"),
                )
                wh25_list.append(sensor)
            parsed["wh25"] = wh25_list
        
        # Parse PM2.5 channels
        if "ch_pm25" in live_data and live_data["ch_pm25"]:
            pm25_sensors = []
            for item in live_data["ch_pm25"]:
                sensor = PM25Sensor(
                    channel=item.get("channel", ""),
                    PM25=item.get("PM25"),
                    PM25_24H=item.get("PM25_24H"),
                    PM25_RealAQI=item.get("PM25_RealAQI"),
                    battery=item.get("battery"),
                    rssi=item.get("rssi"),
                    signal=item.get("signal"),
                )
                pm25_sensors.append(sensor)
            parsed["ch_pm25"] = pm25_sensors
        
        # Parse leak sensors
        if "ch_leak" in live_data and live_data["ch_leak"]:
            leak_sensors = []
            for item in live_data["ch_leak"]:
                sensor = LeakSensor(
                    channel=item.get("channel", ""),
                    status=item.get("status", ""),
                    battery=item.get("battery"),
                    rssi=item.get("rssi"),
                    signal=item.get("signal"),
                )
                leak_sensors.append(sensor)
            parsed["ch_leak"] = leak_sensors
        
        # Parse temperature & humidity channels
        if "ch_aisle" in live_data and live_data["ch_aisle"]:
            aisle_sensors = []
            for item in live_data["ch_aisle"]:
                sensor = TempHumiditySensor(
                    channel=item.get("channel", ""),
                    temp=item.get("temp"),
                    humidity=item.get("humidity"),
                    unit=item.get("unit"),
                    battery=item.get("battery"),
                    rssi=item.get("rssi"),
                    signal=item.get("signal"),
                )
                aisle_sensors.append(sensor)
            parsed["ch_aisle"] = aisle_sensors
        
        # Parse soil sensors
        if "ch_soil" in live_data and live_data["ch_soil"]:
            soil_sensors = []
            for item in live_data["ch_soil"]:
                sensor = SoilSensor(
                    channel=item.get("channel", ""),
                    humidity=item.get("humidity"),
                    unit=item.get("unit"),
                    battery=item.get("battery"),
                    rssi=item.get("rssi"),
                    signal=item.get("signal"),
                )
                soil_sensors.append(sensor)
            parsed["ch_soil"] = soil_sensors
        
        # Parse temperature-only channels
        if "ch_temp" in live_data and live_data["ch_temp"]:
            temp_sensors = []
            for item in live_data["ch_temp"]:
                sensor = TempSensor(
                    channel=item.get("channel", ""),
                    temp=item.get("temp"),
                    unit=item.get("unit"),
                    battery=item.get("battery"),
                    rssi=item.get("rssi"),
                    signal=item.get("signal"),
                )
                temp_sensors.append(sensor)
            parsed["ch_temp"] = temp_sensors
        
        # Parse leaf wetness
        if "ch_leaf" in live_data and live_data["ch_leaf"]:
            leaf_sensors = []
            for item in live_data["ch_leaf"]:
                sensor = LeafSensor(
                    channel=item.get("channel", ""),
                    humidity=item.get("humidity"),
                    unit=item.get("unit"),
                    battery=item.get("battery"),
                    rssi=item.get("rssi"),
                    signal=item.get("signal"),
                )
                leaf_sensors.append(sensor)
            parsed["ch_leaf"] = leaf_sensors
        
        # Parse LDS sensors with device ID mapping
        if "ch_lds" in live_data and live_data["ch_lds"]:
            lds_sensors = []
            for item in live_data["ch_lds"]:
                channel = item.get("channel", "")
                device_id = lds_device_map.get(channel)
                
                sensor = LDSSensor(
                    channel=channel,
                    name=item.get("name", ""),
                    unit=item.get("unit", ""),
                    battery=item.get("battery", ""),
                    voltage=item.get("voltage", ""),
                    air=item.get("air", ""),
                    depth=item.get("depth", ""),
                    total_height=item.get("total_height", ""),
                    total_heat=item.get("total_heat", ""),
                    device_id=device_id,
                )
                lds_sensors.append(sensor)
            parsed["ch_lds"] = lds_sensors
        
        # Parse console data
        if "console" in live_data and live_data["console"]:
            console_list = []
            for item in live_data["console"]:
                sensor = ConsoleSensor(
                    battery=item.get("battery", ""),
                    console_batt_volt=item.get("console_batt_volt"),
                    console_ext_volt=item.get("console_ext_volt"),
                )
                console_list.append(sensor)
            parsed["console"] = console_list
        
        # Parse CO2 data
        if "co2" in live_data and live_data["co2"]:
            co2_list = []
            for item in live_data["co2"]:
                sensor = CO2Sensor(
                    CO2=item.get("CO2"),
                    CO2_24H=item.get("CO2_24H"),
                    PM25=item.get("PM25"),
                    PM25_24H=item.get("PM25_24H"),
                    PM10=item.get("PM10"),
                    PM10_24H=item.get("PM10_24H"),
                    PM10_RealAQI=item.get("PM10_RealAQI"),
                    PM25_RealAQI=item.get("PM25_RealAQI"),
                    temp=item.get("temp"),
                    humidity=item.get("humidity"),
                    unit=item.get("unit"),
                )
                co2_list.append(sensor)
            parsed["co2"] = co2_list
        
        # Parse lightning data
        if "lightning" in live_data and live_data["lightning"]:
            lightning_list = []
            for item in live_data["lightning"]:
                sensor = LightningSensor(
                    distance=item.get("distance", ""),
                    timestamp=item.get("timestamp"),
                    count=item.get("count"),
                    unit=item.get("unit"),
                )
                lightning_list.append(sensor)
            parsed["lightning"] = lightning_list
        
        return parsed

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
        base_data = {
            "id": device_data.get("id", 0),
            "model": device_data.get("model", 0),
            "nickname": device_data.get("nickname", ""),
            "rfnet_state": device_data.get("rfnet_state", 0),
        }
        
        if device_data.get("rfnet_state") == 0:
            return base_data
        
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
                base_data.update(extracted_data)
            
            return base_data
        except Exception as err:
            _LOGGER.debug("Failed to update device status: %s", err)
            return base_data

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