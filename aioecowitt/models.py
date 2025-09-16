"""Data models for EcoWitt devices and sensors."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from mashumaro import DataClassDictMixin


class WittiotDataTypes(Enum):
    """Wittiot Data types."""

    TEMPERATURE = 1
    HUMIDITY = 2
    PM25 = 3
    AQI = 4
    LEAK = 5
    BATTERY = 6
    DISTANCE = 7
    HEAT = 8
    BATTERY_BINARY = 9
    SIGNAL = 10
    RSSI = 11


@dataclass
class DeviceInfo(DataClassDictMixin):
    """Device information."""

    version: str
    dev_name: str
    mac: str


@dataclass
class SensorInfo(DataClassDictMixin):
    """Sensor information."""

    dev_type: str
    name: str
    data_type: WittiotDataTypes


@dataclass
class IoTDevice(DataClassDictMixin):
    """IoT device data."""

    id: int
    model: int
    nickname: str
    rfnet_state: int
    rssi: int | None = None
    iotbatt: str | None = None
    iot_running: str | None = None
    run_time: int | None = None
    velocity_total: float | None = None
    elect_total: float | None = None
    data_water_t: float | None = None
    data_ac_v: float | None = None
    wfc02_position: int | None = None


@dataclass
class WeatherData(DataClassDictMixin):
    """Weather station data grouped by device."""

    # Main console data
    tempinf: float | None = None
    humidityin: float | None = None
    baromrelin: float | None = None
    baromabsin: float | None = None
    tempf: float | None = None
    humidity: float | None = None
    winddir: int | None = None
    winddir10: int | None = None
    apparent: float | None = None
    vpd: float | None = None
    windspeedmph: float | None = None
    windgustmph: float | None = None
    solarradiation: float | None = None
    uv: float | None = None
    daywindmax: float | None = None
    feellike: float | None = None
    dewpoint: float | None = None

    # Rain data
    rainratein: float | None = None
    eventrainin: float | None = None
    dailyrainin: float | None = None
    weeklyrainin: float | None = None
    monthlyrainin: float | None = None
    yearlyrainin: float | None = None
    totalrainin: float | None = None
    h24rainin: float | None = None

    # Piezo rain data
    rrain_piezo: float | None = None
    erain_piezo: float | None = None
    drain_piezo: float | None = None
    wrain_piezo: float | None = None
    mrain_piezo: float | None = None
    yrain_piezo: float | None = None
    train_piezo: float | None = None
    h24rain_piezo: float | None = None
    srain_piezo: str | None = None
    piezora_batt: int | None = None

    # Console battery
    con_batt: int | None = None
    con_batt_volt: float | None = None
    con_ext_volt: float | None = None

    # CO2 sensors
    co2in: int | None = None
    co2in_24h: int | None = None
    co2: int | None = None
    co2_24h: int | None = None
    pm25_co2: float | None = None
    pm25_24h_co2: float | None = None
    pm10_co2: float | None = None
    pm10_24h_co2: float | None = None
    pm10_aqi_co2: int | None = None
    pm25_aqi_co2: int | None = None
    tf_co2: float | None = None
    humi_co2: float | None = None

    # Lightning
    lightning: float | None = None
    lightning_time: str | None = None
    lightning_num: int | None = None

    # Device information
    ver: str | None = None
    devname: str | None = None
    mac: str | None = None

    # IoT devices
    iot_list: dict[str, Any] | None = None


@dataclass
class ChannelSensors(DataClassDictMixin):
    """Channel-based sensors (PM2.5, leak, temp/humidity, soil, etc.)."""

    # PM2.5 channels
    pm25_ch1: float | None = None
    pm25_ch2: float | None = None
    pm25_ch3: float | None = None
    pm25_ch4: float | None = None
    pm25_24h_ch1: float | None = None
    pm25_24h_ch2: float | None = None
    pm25_24h_ch3: float | None = None
    pm25_24h_ch4: float | None = None
    pm25_aqi_ch1: int | None = None
    pm25_aqi_ch2: int | None = None
    pm25_aqi_ch3: int | None = None
    pm25_aqi_ch4: int | None = None

    # Leak sensors
    leak_ch1: str | None = None
    leak_ch2: str | None = None
    leak_ch3: str | None = None
    leak_ch4: str | None = None

    # Temperature & Humidity channels (1-8)
    temp_ch1: float | None = None
    temp_ch2: float | None = None
    temp_ch3: float | None = None
    temp_ch4: float | None = None
    temp_ch5: float | None = None
    temp_ch6: float | None = None
    temp_ch7: float | None = None
    temp_ch8: float | None = None
    humidity_ch1: float | None = None
    humidity_ch2: float | None = None
    humidity_ch3: float | None = None
    humidity_ch4: float | None = None
    humidity_ch5: float | None = None
    humidity_ch6: float | None = None
    humidity_ch7: float | None = None
    humidity_ch8: float | None = None

    # Soil moisture (1-16)
    soilmoisture_ch1: float | None = None
    soilmoisture_ch2: float | None = None
    soilmoisture_ch3: float | None = None
    soilmoisture_ch4: float | None = None
    soilmoisture_ch5: float | None = None
    soilmoisture_ch6: float | None = None
    soilmoisture_ch7: float | None = None
    soilmoisture_ch8: float | None = None
    soilmoisture_ch9: float | None = None
    soilmoisture_ch10: float | None = None
    soilmoisture_ch11: float | None = None
    soilmoisture_ch12: float | None = None
    soilmoisture_ch13: float | None = None
    soilmoisture_ch14: float | None = None
    soilmoisture_ch15: float | None = None
    soilmoisture_ch16: float | None = None

    # Temperature only channels (1-8)
    tf_ch1: float | None = None
    tf_ch2: float | None = None
    tf_ch3: float | None = None
    tf_ch4: float | None = None
    tf_ch5: float | None = None
    tf_ch6: float | None = None
    tf_ch7: float | None = None
    tf_ch8: float | None = None

    # Leaf wetness (1-8)
    leaf_ch1: float | None = None
    leaf_ch2: float | None = None
    leaf_ch3: float | None = None
    leaf_ch4: float | None = None
    leaf_ch5: float | None = None
    leaf_ch6: float | None = None
    leaf_ch7: float | None = None
    leaf_ch8: float | None = None

    # LDS sensors (1-4)
    lds_air_ch1: float | None = None
    lds_air_ch2: float | None = None
    lds_air_ch3: float | None = None
    lds_air_ch4: float | None = None
    lds_depth_ch1: float | None = None
    lds_depth_ch2: float | None = None
    lds_depth_ch3: float | None = None
    lds_depth_ch4: float | None = None
    lds_heat_ch1: int | None = None
    lds_heat_ch2: int | None = None
    lds_heat_ch3: int | None = None
    lds_heat_ch4: int | None = None
    lds_height_ch1: float | None = None
    lds_height_ch2: float | None = None
    lds_height_ch3: float | None = None
    lds_height_ch4: float | None = None


@dataclass
class SensorDiagnostics(DataClassDictMixin):
    """Sensor diagnostic data (battery, RSSI, signal)."""

    # Battery levels for various sensor types
    pm25_ch1_batt: int | None = None
    pm25_ch2_batt: int | None = None
    pm25_ch3_batt: int | None = None
    pm25_ch4_batt: int | None = None
    leak_ch1_batt: int | None = None
    leak_ch2_batt: int | None = None
    leak_ch3_batt: int | None = None
    leak_ch4_batt: int | None = None

    # Device batteries (WH series)
    wh85_batt: int | None = None
    wh90_batt: int | None = None
    wh69_batt: int | None = None
    wh68_batt: int | None = None
    wh40_batt: int | None = None
    wh25_batt: int | None = None
    wh26_batt: int | None = None
    wh80_batt: int | None = None
    wh57_batt: int | None = None
    wh45_batt: int | None = None

    # RSSI values
    pm25_ch1_rssi: int | None = None
    pm25_ch2_rssi: int | None = None
    pm25_ch3_rssi: int | None = None
    pm25_ch4_rssi: int | None = None
    wh85_rssi: int | None = None
    wh90_rssi: int | None = None
    wh69_rssi: int | None = None
    wh68_rssi: int | None = None
    wh40_rssi: int | None = None
    wh25_rssi: int | None = None
    wh26_rssi: int | None = None
    wh80_rssi: int | None = None
    wh57_rssi: int | None = None
    wh45_rssi: int | None = None

    # Signal strength
    pm25_ch1_signal: int | None = None
    pm25_ch2_signal: int | None = None
    pm25_ch3_signal: int | None = None
    pm25_ch4_signal: int | None = None
    wh85_signal: int | None = None
    wh90_signal: int | None = None
    wh69_signal: int | None = None
    wh68_signal: int | None = None
    wh40_signal: int | None = None
    wh25_signal: int | None = None
    wh26_signal: int | None = None
    wh80_signal: int | None = None
    wh57_signal: int | None = None
    wh45_signal: int | None = None


@dataclass
class EcoWittDeviceData(DataClassDictMixin):
    """Complete device data grouped for Home Assistant integration."""

    device_info: DeviceInfo
    weather_data: WeatherData
    channel_sensors: ChannelSensors
    sensor_diagnostics: SensorDiagnostics
    iot_devices: list[IoTDevice]