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
    rssi: str | None = None
    iotbatt: str | None = None
    iot_running: str | None = None
    run_time: int | None = None
    velocity_total: float | None = None
    elect_total: float | None = None
    data_water_t: str | None = None
    data_ac_v: str | None = None
    wfc02_position: int | None = None


@dataclass
class WeatherData(DataClassDictMixin):
    """Weather station data grouped by device."""

    # Main console data
    tempinf: str | None = None
    humidityin: str | None = None
    baromrelin: str | None = None
    baromabsin: str | None = None
    tempf: str | None = None
    humidity: str | None = None
    winddir: str | None = None
    winddir10: str | None = None
    apparent: str | None = None
    vpd: str | None = None
    windspeedmph: str | None = None
    windgustmph: str | None = None
    solarradiation: str | None = None
    uv: str | None = None
    daywindmax: str | None = None
    feellike: str | None = None
    dewpoint: str | None = None

    # Rain data
    rainratein: str | None = None
    eventrainin: str | None = None
    dailyrainin: str | None = None
    weeklyrainin: str | None = None
    monthlyrainin: str | None = None
    yearlyrainin: str | None = None
    totalrainin: str | None = None
    h24rainin: str | None = None

    # Piezo rain data
    rrain_piezo: str | None = None
    erain_piezo: str | None = None
    drain_piezo: str | None = None
    wrain_piezo: str | None = None
    mrain_piezo: str | None = None
    yrain_piezo: str | None = None
    train_piezo: str | None = None
    h24rain_piezo: str | None = None
    srain_piezo: str | None = None
    piezora_batt: str | None = None

    # Console battery
    con_batt: str | None = None
    con_batt_volt: str | None = None
    con_ext_volt: str | None = None

    # CO2 sensors
    co2in: str | None = None
    co2in_24h: str | None = None
    co2: str | None = None
    co2_24h: str | None = None
    pm25_co2: str | None = None
    pm25_24h_co2: str | None = None
    pm10_co2: str | None = None
    pm10_24h_co2: str | None = None
    pm10_aqi_co2: str | None = None
    pm25_aqi_co2: str | None = None
    tf_co2: str | None = None
    humi_co2: str | None = None

    # Lightning
    lightning: str | None = None
    lightning_time: str | None = None
    lightning_num: str | None = None

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
    pm25_ch1: str | None = None
    pm25_ch2: str | None = None
    pm25_ch3: str | None = None
    pm25_ch4: str | None = None
    pm25_24h_ch1: str | None = None
    pm25_24h_ch2: str | None = None
    pm25_24h_ch3: str | None = None
    pm25_24h_ch4: str | None = None
    pm25_aqi_ch1: str | None = None
    pm25_aqi_ch2: str | None = None
    pm25_aqi_ch3: str | None = None
    pm25_aqi_ch4: str | None = None

    # Leak sensors
    leak_ch1: str | None = None
    leak_ch2: str | None = None
    leak_ch3: str | None = None
    leak_ch4: str | None = None

    # Temperature & Humidity channels (1-8)
    temp_ch1: str | None = None
    temp_ch2: str | None = None
    temp_ch3: str | None = None
    temp_ch4: str | None = None
    temp_ch5: str | None = None
    temp_ch6: str | None = None
    temp_ch7: str | None = None
    temp_ch8: str | None = None
    humidity_ch1: str | None = None
    humidity_ch2: str | None = None
    humidity_ch3: str | None = None
    humidity_ch4: str | None = None
    humidity_ch5: str | None = None
    humidity_ch6: str | None = None
    humidity_ch7: str | None = None
    humidity_ch8: str | None = None

    # Soil moisture (1-16)
    soilmoisture_ch1: str | None = None
    soilmoisture_ch2: str | None = None
    soilmoisture_ch3: str | None = None
    soilmoisture_ch4: str | None = None
    soilmoisture_ch5: str | None = None
    soilmoisture_ch6: str | None = None
    soilmoisture_ch7: str | None = None
    soilmoisture_ch8: str | None = None
    soilmoisture_ch9: str | None = None
    soilmoisture_ch10: str | None = None
    soilmoisture_ch11: str | None = None
    soilmoisture_ch12: str | None = None
    soilmoisture_ch13: str | None = None
    soilmoisture_ch14: str | None = None
    soilmoisture_ch15: str | None = None
    soilmoisture_ch16: str | None = None

    # Temperature only channels (1-8)
    tf_ch1: str | None = None
    tf_ch2: str | None = None
    tf_ch3: str | None = None
    tf_ch4: str | None = None
    tf_ch5: str | None = None
    tf_ch6: str | None = None
    tf_ch7: str | None = None
    tf_ch8: str | None = None

    # Leaf wetness (1-8)
    leaf_ch1: str | None = None
    leaf_ch2: str | None = None
    leaf_ch3: str | None = None
    leaf_ch4: str | None = None
    leaf_ch5: str | None = None
    leaf_ch6: str | None = None
    leaf_ch7: str | None = None
    leaf_ch8: str | None = None

    # LDS sensors (1-4)
    lds_air_ch1: str | None = None
    lds_air_ch2: str | None = None
    lds_air_ch3: str | None = None
    lds_air_ch4: str | None = None
    lds_depth_ch1: str | None = None
    lds_depth_ch2: str | None = None
    lds_depth_ch3: str | None = None
    lds_depth_ch4: str | None = None
    lds_heat_ch1: str | None = None
    lds_heat_ch2: str | None = None
    lds_heat_ch3: str | None = None
    lds_heat_ch4: str | None = None
    lds_height_ch1: str | None = None
    lds_height_ch2: str | None = None
    lds_height_ch3: str | None = None
    lds_height_ch4: str | None = None


@dataclass
class SensorDiagnostics(DataClassDictMixin):
    """Sensor diagnostic data (battery, RSSI, signal)."""

    # Battery levels for various sensor types
    pm25_ch1_batt: str | None = None
    pm25_ch2_batt: str | None = None
    pm25_ch3_batt: str | None = None
    pm25_ch4_batt: str | None = None
    leak_ch1_batt: str | None = None
    leak_ch2_batt: str | None = None
    leak_ch3_batt: str | None = None
    leak_ch4_batt: str | None = None

    # Device batteries (WH series)
    wh85_batt: str | None = None
    wh90_batt: str | None = None
    wh69_batt: str | None = None
    wh68_batt: str | None = None
    wh40_batt: str | None = None
    wh25_batt: str | None = None
    wh26_batt: str | None = None
    wh80_batt: str | None = None
    wh57_batt: str | None = None
    wh45_batt: str | None = None

    # RSSI values
    pm25_ch1_rssi: str | None = None
    pm25_ch2_rssi: str | None = None
    pm25_ch3_rssi: str | None = None
    pm25_ch4_rssi: str | None = None
    wh85_rssi: str | None = None
    wh90_rssi: str | None = None
    wh69_rssi: str | None = None
    wh68_rssi: str | None = None
    wh40_rssi: str | None = None
    wh25_rssi: str | None = None
    wh26_rssi: str | None = None
    wh80_rssi: str | None = None
    wh57_rssi: str | None = None
    wh45_rssi: str | None = None

    # Signal strength
    pm25_ch1_signal: str | None = None
    pm25_ch2_signal: str | None = None
    pm25_ch3_signal: str | None = None
    pm25_ch4_signal: str | None = None
    wh85_signal: str | None = None
    wh90_signal: str | None = None
    wh69_signal: str | None = None
    wh68_signal: str | None = None
    wh40_signal: str | None = None
    wh25_signal: str | None = None
    wh26_signal: str | None = None
    wh80_signal: str | None = None
    wh57_signal: str | None = None
    wh45_signal: str | None = None


@dataclass
class EcoWittDeviceData(DataClassDictMixin):
    """Complete device data grouped for Home Assistant integration."""

    device_info: DeviceInfo
    weather_data: WeatherData
    channel_sensors: ChannelSensors
    sensor_diagnostics: SensorDiagnostics
    iot_devices: list[IoTDevice]