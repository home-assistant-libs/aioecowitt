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


class TemperatureUnit(Enum):
    """Temperature units."""

    CELSIUS = "C"
    FAHRENHEIT = "F"


class PressureUnit(Enum):
    """Pressure units."""

    HPA = "hPa"
    INHG = "inHg"
    MMHG = "mmHg"
    KPA = "kPa"


class DistanceUnit(Enum):
    """Distance units."""

    MM = "mm"
    IN = "in"
    FT = "ft"
    M = "m"


class SpeedUnit(Enum):
    """Speed units."""

    MS = "m/s"
    MPH = "mph"
    KMH = "km/h"
    KNOTS = "knots"
    FTS = "ft/s"


class RainRateUnit(Enum):
    """Rain rate units."""

    MM_HR = "mm/Hr"
    IN_HR = "in/Hr"


class PowerUnit(Enum):
    """Power units."""

    WM2 = "W/m2"
    KFC = "Kfc"
    KLUX = "Klux"


class PercentageUnit(Enum):
    """Percentage units."""

    PERCENT = "%"


class VoltageUnit(Enum):
    """Voltage units."""

    V = "V"


@dataclass
class SensorReading(DataClassDictMixin):
    """A sensor reading with value and unit."""

    value: float | int | str | None
    unit: str | None = None


@dataclass
class DeviceInfo(DataClassDictMixin):
    """Device information."""

    version: str
    dev_name: str
    mac: str


@dataclass
class SensorInfo(DataClassDictMixin):
    """Sensor information from sensor list."""

    img: str
    type: int
    name: str
    id: str
    batt: int | None = None
    rssi: int | None = None
    signal: int | None = None
    version: str | None = None
    idst: str | None = None


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
class CommonSensor(DataClassDictMixin):
    """Common sensor data."""

    id: str
    val: str
    unit: str | None = None


@dataclass
class RainSensor(DataClassDictMixin):
    """Rain sensor data."""

    id: str
    val: str
    unit: str | None = None


@dataclass
class PiezoRainSensor(DataClassDictMixin):
    """Piezo rain sensor data."""

    id: str
    val: str
    unit: str | None = None
    battery: str | None = None
    voltage: str | None = None
    ws90cap_volt: str | None = None
    ws90_ver: str | None = None


@dataclass
class WH25Data(DataClassDictMixin):
    """WH25 indoor sensor data."""

    intemp: str
    unit: str
    inhumi: str
    abs: str
    rel: str
    CO2: str | None = None
    CO2_24H: str | None = None


@dataclass
class PM25Sensor(DataClassDictMixin):
    """PM2.5 sensor data."""

    channel: str
    PM25: str | None = None
    PM25_24H: str | None = None
    PM25_RealAQI: str | None = None
    battery: str | None = None
    rssi: str | None = None
    signal: str | None = None


@dataclass
class LeakSensor(DataClassDictMixin):
    """Leak sensor data."""

    channel: str
    status: str
    battery: str | None = None
    rssi: str | None = None
    signal: str | None = None


@dataclass
class TempHumiditySensor(DataClassDictMixin):
    """Temperature and humidity sensor data."""

    channel: str
    temp: str | None = None
    humidity: str | None = None
    unit: str | None = None
    battery: str | None = None
    rssi: str | None = None
    signal: str | None = None


@dataclass
class SoilSensor(DataClassDictMixin):
    """Soil moisture sensor data."""

    channel: str
    humidity: str | None = None
    unit: str | None = None
    battery: str | None = None
    rssi: str | None = None
    signal: str | None = None


@dataclass
class TempSensor(DataClassDictMixin):
    """Temperature-only sensor data."""

    channel: str
    temp: str | None = None
    unit: str | None = None
    battery: str | None = None
    rssi: str | None = None
    signal: str | None = None


@dataclass
class LeafSensor(DataClassDictMixin):
    """Leaf wetness sensor data."""

    channel: str
    humidity: str | None = None
    unit: str | None = None
    battery: str | None = None
    rssi: str | None = None
    signal: str | None = None


@dataclass
class LDSSensor(DataClassDictMixin):
    """LDS (Laser Distance Sensor) data."""

    channel: str
    name: str
    unit: str
    battery: str
    voltage: str
    air: str
    depth: str
    total_height: str
    total_heat: str
    device_id: str | None = None  # From sensor info


@dataclass
class ConsoleSensor(DataClassDictMixin):
    """Console sensor data."""

    battery: str
    console_batt_volt: str | None = None
    console_ext_volt: str | None = None


@dataclass
class CO2Sensor(DataClassDictMixin):
    """CO2 sensor data."""

    CO2: str | None = None
    CO2_24H: str | None = None
    PM25: str | None = None
    PM25_24H: str | None = None
    PM10: str | None = None
    PM10_24H: str | None = None
    PM10_RealAQI: str | None = None
    PM25_RealAQI: str | None = None
    temp: str | None = None
    humidity: str | None = None
    unit: str | None = None


@dataclass
class LightningSensor(DataClassDictMixin):
    """Lightning sensor data."""

    distance: str
    timestamp: str | None = None
    count: str | None = None
    unit: str | None = None


@dataclass
class EcoWittDeviceData(DataClassDictMixin):
    """Complete device data keeping original structure."""

    device_info: DeviceInfo
    sensors: list[SensorInfo]
    iot_devices: list[IoTDevice]
    
    # Keep original grouped structure - all optional with defaults
    common_list: list[CommonSensor] | None = None
    rain: list[RainSensor] | None = None
    piezoRain: list[PiezoRainSensor] | None = None
    wh25: list[WH25Data] | None = None
    ch_pm25: list[PM25Sensor] | None = None
    ch_leak: list[LeakSensor] | None = None
    ch_aisle: list[TempHumiditySensor] | None = None
    ch_soil: list[SoilSensor] | None = None
    ch_temp: list[TempSensor] | None = None
    ch_leaf: list[LeafSensor] | None = None
    ch_lds: list[LDSSensor] | None = None
    console: list[ConsoleSensor] | None = None
    co2: list[CO2Sensor] | None = None
    lightning: list[LightningSensor] | None = None