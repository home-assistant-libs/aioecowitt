"""Sensor and mapping data from ecowitt."""

from __future__ import annotations

import datetime as dt
import enum
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from collections.abc import Callable

    from .station import EcoWittStation


@dataclass
class EcoWittSensor:
    """An internal sensor to the ecowitt."""

    name: str
    key: str
    stype: EcoWittSensorTypes
    station: EcoWittStation
    value: None | str | int | float | dt.datetime = field(default=None, init=False)
    last_update: float = field(default=0, init=False)
    last_update_m: float = field(default=0, init=False)
    update_cb: list[Callable[[], None]] = field(default_factory=list, init=False)

    def update_value(
        self,
        value: None | str | float | dt.datetime,
        last_update: float,
        last_update_m: float,
    ) -> None:
        """Update the value of the sensor."""
        self.last_update = last_update
        self.last_update_m = last_update_m

        # Set the value
        if self.value == value:
            return
        self.value = value

        # notify listeners
        for callback in self.update_cb:
            callback()


def _convert_timestamp(value: str) -> dt.datetime:
    return dt.datetime.fromtimestamp(int(value), dt.UTC)


@enum.unique
class EcoWittSensorTypes(enum.IntEnum):
    """EcoWitt sensor types."""

    convert_fn: Callable[[str], str | int | float | dt.datetime]

    def __new__(
        cls,
        value: int,
        convert_fn: Callable[[str], str | int | float | dt.datetime],
    ) -> Self:
        """Create new EcoWittSensorTypes."""
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.convert_fn = convert_fn
        return obj

    INTERNAL = 1, lambda x: x
    PRESSURE_HPA = 2, lambda x: x  # HA should convert
    PRESSURE_INHG = 3, float
    RAIN_COUNT_MM = 4, lambda x: x  # HA should convert
    RAIN_COUNT_INCHES = 5, float
    RAIN_RATE_MM = 6, lambda x: x  # HA should convert
    RAIN_RATE_INCHES = 7, float
    HUMIDITY = 8, int
    DEGREE = 9, int
    SPEED_KPH = 10, lambda x: x  # HA should convert
    SPEED_MPH = 11, float
    TEMPERATURE_C = 12, lambda x: x  # HA should convert
    TEMPERATURE_F = 13, float
    WATT_METERS_SQUARED = 14, float
    UV_INDEX = 15, int
    PM25 = 16, float
    PM10 = 17, float
    TIMESTAMP = 18, _convert_timestamp
    LIGHTNING_COUNT = 19, int
    LIGHTNING_DISTANCE_KM = 20, int
    LIGHTNING_DISTANCE_MILES = 21, lambda x: x  # HA should convert
    LEAK = 22, int
    VOLTAGE = 23, float
    BATTERY_BINARY = 24, float
    BATTERY_VOLTAGE = 25, float
    BATTERY_PERCENTAGE = 26, lambda x: int(x) * 20
    CO2_PPM = 27, int
    LUX = 28, lambda x: x  # HA should convert
    PERCENTAGE = 29, int
    SOIL_RAWADC = 30, lambda x: x  # Keep it as it comes in
    RAIN_STATE = 31, int
    SOIL_MOISTURE = 32, int
    VPD_INHG = 33, float
    PM1 = 34, float
    PM4 = 35, float
    DISTANCE_MM = 36, int
    HEAT_COUNT = 37, int


@dataclass
class EcoWittMapping:
    """Mapping Sensor information."""

    name: str
    stype: EcoWittSensorTypes


SENSOR_MAP: dict[str, EcoWittMapping] = {
    "baromabshpa": EcoWittMapping("Absolute Pressure", EcoWittSensorTypes.PRESSURE_HPA),
    "baromrelhpa": EcoWittMapping("Relative Pressure", EcoWittSensorTypes.PRESSURE_HPA),
    "baromabsin": EcoWittMapping("Absolute Pressure", EcoWittSensorTypes.PRESSURE_INHG),
    "baromrelin": EcoWittMapping("Relative Pressure", EcoWittSensorTypes.PRESSURE_INHG),
    "vpd": EcoWittMapping("Vapour Pressure Deficit", EcoWittSensorTypes.VPD_INHG),
    "rainratein": EcoWittMapping("Rain Rate", EcoWittSensorTypes.RAIN_RATE_INCHES),
    "eventrainin": EcoWittMapping("Event Rain", EcoWittSensorTypes.RAIN_COUNT_INCHES),
    "hourlyrainin": EcoWittMapping("Hourly Rain", EcoWittSensorTypes.RAIN_COUNT_INCHES),
    "totalrainin": EcoWittMapping("Total Rain", EcoWittSensorTypes.RAIN_COUNT_INCHES),
    "dailyrainin": EcoWittMapping("Daily Rain", EcoWittSensorTypes.RAIN_COUNT_INCHES),
    "weeklyrainin": EcoWittMapping("Weekly Rain", EcoWittSensorTypes.RAIN_COUNT_INCHES),
    "monthlyrainin": EcoWittMapping(
        "Monthly Rain", EcoWittSensorTypes.RAIN_COUNT_INCHES
    ),
    "yearlyrainin": EcoWittMapping("Yearly Rain", EcoWittSensorTypes.RAIN_COUNT_INCHES),
    "rainratemm": EcoWittMapping("Rain Rate", EcoWittSensorTypes.RAIN_RATE_MM),
    "eventrainmm": EcoWittMapping("Event Rain", EcoWittSensorTypes.RAIN_COUNT_MM),
    "hourlyrainmm": EcoWittMapping("Hourly Rain", EcoWittSensorTypes.RAIN_COUNT_MM),
    "totalrainmm": EcoWittMapping("Total Rain", EcoWittSensorTypes.RAIN_COUNT_MM),
    "dailyrainmm": EcoWittMapping("Daily Rain", EcoWittSensorTypes.RAIN_COUNT_MM),
    "weeklyrainmm": EcoWittMapping("Weekly Rain", EcoWittSensorTypes.RAIN_COUNT_MM),
    "monthlyrainmm": EcoWittMapping("Monthly Rain", EcoWittSensorTypes.RAIN_COUNT_MM),
    "yearlyrainmm": EcoWittMapping("Yearly Rain", EcoWittSensorTypes.RAIN_COUNT_MM),
    "humidity": EcoWittMapping("Humidity", EcoWittSensorTypes.HUMIDITY),
    "humidityin": EcoWittMapping("Indoor Humidity", EcoWittSensorTypes.HUMIDITY),
    "humidity1": EcoWittMapping("Humidity 1", EcoWittSensorTypes.HUMIDITY),
    "humidity2": EcoWittMapping("Humidity 2", EcoWittSensorTypes.HUMIDITY),
    "humidity3": EcoWittMapping("Humidity 3", EcoWittSensorTypes.HUMIDITY),
    "humidity4": EcoWittMapping("Humidity 4", EcoWittSensorTypes.HUMIDITY),
    "humidity5": EcoWittMapping("Humidity 5", EcoWittSensorTypes.HUMIDITY),
    "humidity6": EcoWittMapping("Humidity 6", EcoWittSensorTypes.HUMIDITY),
    "humidity7": EcoWittMapping("Humidity 7", EcoWittSensorTypes.HUMIDITY),
    "humidity8": EcoWittMapping("Humidity 8", EcoWittSensorTypes.HUMIDITY),
    "winddir": EcoWittMapping("Wind Direction", EcoWittSensorTypes.DEGREE),
    "winddir_avg10m": EcoWittMapping(
        "Wind Direction 10m Avg", EcoWittSensorTypes.DEGREE
    ),
    "windspeedkmh": EcoWittMapping("Wind Speed", EcoWittSensorTypes.SPEED_KPH),
    "windspdkmh_avg10m": EcoWittMapping(
        "Wind Speed 10m Avg", EcoWittSensorTypes.SPEED_KPH
    ),
    "windgustkmh": EcoWittMapping("Wind Gust", EcoWittSensorTypes.SPEED_KPH),
    "maxdailygustkmh": EcoWittMapping("Max Daily Gust", EcoWittSensorTypes.SPEED_KPH),
    "windspeedmph": EcoWittMapping("Wind Speed", EcoWittSensorTypes.SPEED_MPH),
    "windspdmph_avg10m": EcoWittMapping(
        "Wind Speed 10m Avg", EcoWittSensorTypes.SPEED_MPH
    ),
    "windgustmph": EcoWittMapping("Wind Gust", EcoWittSensorTypes.SPEED_MPH),
    "maxdailygust": EcoWittMapping("Max Daily Wind Gust", EcoWittSensorTypes.SPEED_MPH),
    "tempc": EcoWittMapping("Outdoor Temperature", EcoWittSensorTypes.TEMPERATURE_C),
    "tempfeelsc": EcoWittMapping(
        "Feels like Temperature", EcoWittSensorTypes.TEMPERATURE_C
    ),
    "tempinc": EcoWittMapping("Indoor Temperature", EcoWittSensorTypes.TEMPERATURE_C),
    "temp1c": EcoWittMapping("Temperature 1", EcoWittSensorTypes.TEMPERATURE_C),
    "temp2c": EcoWittMapping("Temperature 2", EcoWittSensorTypes.TEMPERATURE_C),
    "temp3c": EcoWittMapping("Temperature 3", EcoWittSensorTypes.TEMPERATURE_C),
    "temp4c": EcoWittMapping("Temperature 4", EcoWittSensorTypes.TEMPERATURE_C),
    "temp5c": EcoWittMapping("Temperature 5", EcoWittSensorTypes.TEMPERATURE_C),
    "temp6c": EcoWittMapping("Temperature 6", EcoWittSensorTypes.TEMPERATURE_C),
    "temp7c": EcoWittMapping("Temperature 7", EcoWittSensorTypes.TEMPERATURE_C),
    "temp8c": EcoWittMapping("Temperature 8", EcoWittSensorTypes.TEMPERATURE_C),
    "dewpointc": EcoWittMapping("Dewpoint", EcoWittSensorTypes.TEMPERATURE_C),
    "dewpointinc": EcoWittMapping("Indoor Dewpoint", EcoWittSensorTypes.TEMPERATURE_C),
    "dewpoint1c": EcoWittMapping("Dewpoint 1", EcoWittSensorTypes.TEMPERATURE_C),
    "dewpoint2c": EcoWittMapping("Dewpoint 2", EcoWittSensorTypes.TEMPERATURE_C),
    "dewpoint3c": EcoWittMapping("Dewpoint 3", EcoWittSensorTypes.TEMPERATURE_C),
    "dewpoint4c": EcoWittMapping("Dewpoint 4", EcoWittSensorTypes.TEMPERATURE_C),
    "dewpoint5c": EcoWittMapping("Dewpoint 5", EcoWittSensorTypes.TEMPERATURE_C),
    "dewpoint6c": EcoWittMapping("Dewpoint 6", EcoWittSensorTypes.TEMPERATURE_C),
    "dewpoint7c": EcoWittMapping("Dewpoint 7", EcoWittSensorTypes.TEMPERATURE_C),
    "dewpoint8c": EcoWittMapping("Dewpoint 8", EcoWittSensorTypes.TEMPERATURE_C),
    "windchillc": EcoWittMapping("Windchill", EcoWittSensorTypes.TEMPERATURE_C),
    "tempf": EcoWittMapping("Outdoor Temperature", EcoWittSensorTypes.TEMPERATURE_F),
    "tempfeelsf": EcoWittMapping(
        "Feels like Temperature",
        EcoWittSensorTypes.TEMPERATURE_F,
    ),
    "tempinf": EcoWittMapping("Indoor Temperature", EcoWittSensorTypes.TEMPERATURE_F),
    "temp1f": EcoWittMapping("Temperature 1", EcoWittSensorTypes.TEMPERATURE_F),
    "temp2f": EcoWittMapping("Temperature 2", EcoWittSensorTypes.TEMPERATURE_F),
    "temp3f": EcoWittMapping("Temperature 3", EcoWittSensorTypes.TEMPERATURE_F),
    "temp4f": EcoWittMapping("Temperature 4", EcoWittSensorTypes.TEMPERATURE_F),
    "temp5f": EcoWittMapping("Temperature 5", EcoWittSensorTypes.TEMPERATURE_F),
    "temp6f": EcoWittMapping("Temperature 6", EcoWittSensorTypes.TEMPERATURE_F),
    "temp7f": EcoWittMapping("Temperature 7", EcoWittSensorTypes.TEMPERATURE_F),
    "temp8f": EcoWittMapping("Temperature 8", EcoWittSensorTypes.TEMPERATURE_F),
    "dewpointf": EcoWittMapping("Dewpoint", EcoWittSensorTypes.TEMPERATURE_F),
    "dewpointinf": EcoWittMapping("Indoor Dewpoint", EcoWittSensorTypes.TEMPERATURE_F),
    "dewpoint1f": EcoWittMapping("Dewpoint 1", EcoWittSensorTypes.TEMPERATURE_F),
    "dewpoint2f": EcoWittMapping("Dewpoint 2", EcoWittSensorTypes.TEMPERATURE_F),
    "dewpoint3f": EcoWittMapping("Dewpoint 3", EcoWittSensorTypes.TEMPERATURE_F),
    "dewpoint4f": EcoWittMapping("Dewpoint 4", EcoWittSensorTypes.TEMPERATURE_F),
    "dewpoint5f": EcoWittMapping("Dewpoint 5", EcoWittSensorTypes.TEMPERATURE_F),
    "dewpoint6f": EcoWittMapping("Dewpoint 6", EcoWittSensorTypes.TEMPERATURE_F),
    "dewpoint7f": EcoWittMapping("Dewpoint 7", EcoWittSensorTypes.TEMPERATURE_F),
    "dewpoint8f": EcoWittMapping("Dewpoint 8", EcoWittSensorTypes.TEMPERATURE_F),
    "windchillf": EcoWittMapping("Windchill", EcoWittSensorTypes.TEMPERATURE_F),
    "solarradiation": EcoWittMapping(
        "Solar Radiation", EcoWittSensorTypes.WATT_METERS_SQUARED
    ),
    "solarradiation_lux": EcoWittMapping("Solar Lux", EcoWittSensorTypes.LUX),
    "uv": EcoWittMapping("UV Index", EcoWittSensorTypes.UV_INDEX),
    "soilmoisture1": EcoWittMapping(
        "Soil Moisture 1", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture2": EcoWittMapping(
        "Soil Moisture 2", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture3": EcoWittMapping(
        "Soil Moisture 3", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture4": EcoWittMapping(
        "Soil Moisture 4", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture5": EcoWittMapping(
        "Soil Moisture 5", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture6": EcoWittMapping(
        "Soil Moisture 6", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture7": EcoWittMapping(
        "Soil Moisture 7", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture8": EcoWittMapping(
        "Soil Moisture 8", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture9": EcoWittMapping(
        "Soil Moisture 9", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture10": EcoWittMapping(
        "Soil Moisture 10", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture11": EcoWittMapping(
        "Soil Moisture 11", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture12": EcoWittMapping(
        "Soil Moisture 12", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture13": EcoWittMapping(
        "Soil Moisture 13", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture14": EcoWittMapping(
        "Soil Moisture 14", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture15": EcoWittMapping(
        "Soil Moisture 15", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilmoisture16": EcoWittMapping(
        "Soil Moisture 16", EcoWittSensorTypes.SOIL_MOISTURE
    ),
    "soilad1": EcoWittMapping("Soil AD 1", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad2": EcoWittMapping("Soil AD 2", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad3": EcoWittMapping("Soil AD 3", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad4": EcoWittMapping("Soil AD 4", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad5": EcoWittMapping("Soil AD 5", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad6": EcoWittMapping("Soil AD 6", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad7": EcoWittMapping("Soil AD 7", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad8": EcoWittMapping("Soil AD 8", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad9": EcoWittMapping("Soil AD 9", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad10": EcoWittMapping("Soil AD 10", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad11": EcoWittMapping("Soil AD 11", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad12": EcoWittMapping("Soil AD 12", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad13": EcoWittMapping("Soil AD 13", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad14": EcoWittMapping("Soil AD 14", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad15": EcoWittMapping("Soil AD 15", EcoWittSensorTypes.SOIL_RAWADC),
    "soilad16": EcoWittMapping("Soil AD 16", EcoWittSensorTypes.SOIL_RAWADC),
    "pm25_ch1": EcoWittMapping("PM2.5 1", EcoWittSensorTypes.PM25),
    "pm25_ch2": EcoWittMapping("PM2.5 2", EcoWittSensorTypes.PM25),
    "pm25_ch3": EcoWittMapping("PM2.5 3", EcoWittSensorTypes.PM25),
    "pm25_ch4": EcoWittMapping("PM2.5 4", EcoWittSensorTypes.PM25),
    "pm25_avg_24h_ch1": EcoWittMapping("PM2.5 24h Average 1", EcoWittSensorTypes.PM25),
    "pm25_avg_24h_ch2": EcoWittMapping("PM2.5 24h Average 2", EcoWittSensorTypes.PM25),
    "pm25_avg_24h_ch3": EcoWittMapping("PM2.5 24h Average 3", EcoWittSensorTypes.PM25),
    "pm25_avg_24h_ch4": EcoWittMapping("PM2.5 24h Average 4", EcoWittSensorTypes.PM25),
    "lightning_time": EcoWittMapping(
        "Last Lightning strike", EcoWittSensorTypes.TIMESTAMP
    ),
    "lightning_num": EcoWittMapping(
        "Lightning strikes", EcoWittSensorTypes.LIGHTNING_COUNT
    ),
    "lightning": EcoWittMapping(
        "Lightning strike distance", EcoWittSensorTypes.LIGHTNING_DISTANCE_KM
    ),
    "lightning_mi": EcoWittMapping(
        "Lightning strike distance",
        EcoWittSensorTypes.LIGHTNING_DISTANCE_MILES,
    ),
    "tf_co2": EcoWittMapping("WH45 Temperature", EcoWittSensorTypes.TEMPERATURE_F),
    "tf_co2c": EcoWittMapping("WH45 Temperature", EcoWittSensorTypes.TEMPERATURE_C),
    "humi_co2": EcoWittMapping("WH45 Humidity", EcoWittSensorTypes.HUMIDITY),
    "pm1_co2": EcoWittMapping("WH46 PM1 CO2", EcoWittSensorTypes.PM1),
    "pm1_24h_co2": EcoWittMapping("WH46 PM1 CO2 24h average", EcoWittSensorTypes.PM1),
    "pm4_co2": EcoWittMapping("WH46 PM4 CO2", EcoWittSensorTypes.PM4),
    "pm4_24h_co2": EcoWittMapping("WH46 PM4 CO2 24h average", EcoWittSensorTypes.PM4),
    "pm25_co2": EcoWittMapping("WH45 PM2.5 CO2", EcoWittSensorTypes.PM25),
    "pm25_24h_co2": EcoWittMapping(
        "WH45 PM2.5 CO2 24h average", EcoWittSensorTypes.PM25
    ),
    "pm10_co2": EcoWittMapping("WH45 PM10 CO2", EcoWittSensorTypes.PM10),
    "pm10_24h_co2": EcoWittMapping(
        "WH45 PM10 CO2 24h average", EcoWittSensorTypes.PM10
    ),
    "co2": EcoWittMapping("WH45 CO2", EcoWittSensorTypes.CO2_PPM),
    "co2_24h": EcoWittMapping("WH45 CO2 24h average", EcoWittSensorTypes.CO2_PPM),
    "co2_batt": EcoWittMapping("WH45 Battery", EcoWittSensorTypes.BATTERY_PERCENTAGE),
    "co2in": EcoWittMapping("Console CO2", EcoWittSensorTypes.CO2_PPM),
    "co2in_24h": EcoWittMapping("Console CO2 24h average", EcoWittSensorTypes.CO2_PPM),
    "console_batt": EcoWittMapping(
        "Console Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "leak_ch1": EcoWittMapping("Leak Detection 1", EcoWittSensorTypes.LEAK),
    "leak_ch2": EcoWittMapping("Leak Detection 2", EcoWittSensorTypes.LEAK),
    "leak_ch3": EcoWittMapping("Leak Detection 3", EcoWittSensorTypes.LEAK),
    "leak_ch4": EcoWittMapping("Leak Detection 4", EcoWittSensorTypes.LEAK),
    "wh25batt": EcoWittMapping("WH25 Battery", EcoWittSensorTypes.BATTERY_BINARY),
    "wh26batt": EcoWittMapping("WH26 Battery", EcoWittSensorTypes.BATTERY_BINARY),
    "wh40batt": EcoWittMapping("WH40 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "wh57batt": EcoWittMapping("WH57 Battery", EcoWittSensorTypes.BATTERY_PERCENTAGE),
    "wh65batt": EcoWittMapping("WH65 Battery", EcoWittSensorTypes.BATTERY_BINARY),
    "wh68batt": EcoWittMapping("WH68 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "wh80batt": EcoWittMapping("WH80 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "wh85batt": EcoWittMapping("WH85 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "wh90batt": EcoWittMapping("WH90 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt1": EcoWittMapping("Soil Battery 1", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt2": EcoWittMapping("Soil Battery 2", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt3": EcoWittMapping("Soil Battery 3", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt4": EcoWittMapping("Soil Battery 4", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt5": EcoWittMapping("Soil Battery 5", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt6": EcoWittMapping("Soil Battery 6", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt7": EcoWittMapping("Soil Battery 7", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt8": EcoWittMapping("Soil Battery 8", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt9": EcoWittMapping("Soil Battery 9", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt10": EcoWittMapping("Soil Battery 10", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt11": EcoWittMapping("Soil Battery 11", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt12": EcoWittMapping("Soil Battery 12", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt13": EcoWittMapping("Soil Battery 13", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt14": EcoWittMapping("Soil Battery 14", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt15": EcoWittMapping("Soil Battery 15", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt16": EcoWittMapping("Soil Battery 16", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "batt1": EcoWittMapping("Battery 1", EcoWittSensorTypes.BATTERY_BINARY),
    "batt2": EcoWittMapping("Battery 2", EcoWittSensorTypes.BATTERY_BINARY),
    "batt3": EcoWittMapping("Battery 3", EcoWittSensorTypes.BATTERY_BINARY),
    "batt4": EcoWittMapping("Battery 4", EcoWittSensorTypes.BATTERY_BINARY),
    "batt5": EcoWittMapping("Battery 5", EcoWittSensorTypes.BATTERY_BINARY),
    "batt6": EcoWittMapping("Battery 6", EcoWittSensorTypes.BATTERY_BINARY),
    "batt7": EcoWittMapping("Battery 7", EcoWittSensorTypes.BATTERY_BINARY),
    "batt8": EcoWittMapping("Battery 8", EcoWittSensorTypes.BATTERY_BINARY),
    "pm25batt1": EcoWittMapping(
        "PM2.5 1 Battery", EcoWittSensorTypes.BATTERY_PERCENTAGE
    ),
    "pm25batt2": EcoWittMapping(
        "PM2.5 2 Battery", EcoWittSensorTypes.BATTERY_PERCENTAGE
    ),
    "pm25batt3": EcoWittMapping(
        "PM2.5 3 Battery", EcoWittSensorTypes.BATTERY_PERCENTAGE
    ),
    "pm25batt4": EcoWittMapping(
        "PM2.5 4 Battery", EcoWittSensorTypes.BATTERY_PERCENTAGE
    ),
    "pm25batt5": EcoWittMapping(
        "PM2.5 5 Battery", EcoWittSensorTypes.BATTERY_PERCENTAGE
    ),
    "pm25batt6": EcoWittMapping(
        "PM2.5 6 Battery", EcoWittSensorTypes.BATTERY_PERCENTAGE
    ),
    "pm25batt7": EcoWittMapping(
        "PM2.5 7 Battery", EcoWittSensorTypes.BATTERY_PERCENTAGE
    ),
    "pm25batt8": EcoWittMapping(
        "PM2.5 8 Battery", EcoWittSensorTypes.BATTERY_PERCENTAGE
    ),
    "leakbatt1": EcoWittMapping(
        "Leak Detection 1 Battery",
        EcoWittSensorTypes.BATTERY_PERCENTAGE,
    ),
    "leakbatt2": EcoWittMapping(
        "Leak Detection 2 Battery",
        EcoWittSensorTypes.BATTERY_PERCENTAGE,
    ),
    "leakbatt3": EcoWittMapping(
        "Leak Detection 3 Battery",
        EcoWittSensorTypes.BATTERY_PERCENTAGE,
    ),
    "leakbatt4": EcoWittMapping(
        "Leak Detection 4 Battery",
        EcoWittSensorTypes.BATTERY_PERCENTAGE,
    ),
    "leakbatt5": EcoWittMapping(
        "Leak Detection 5 Battery",
        EcoWittSensorTypes.BATTERY_PERCENTAGE,
    ),
    "leakbatt6": EcoWittMapping(
        "Leak Detection 6 Battery",
        EcoWittSensorTypes.BATTERY_PERCENTAGE,
    ),
    "leakbatt7": EcoWittMapping(
        "Leak Detection 7 Battery",
        EcoWittSensorTypes.BATTERY_PERCENTAGE,
    ),
    "leakbatt8": EcoWittMapping(
        "Leak Detection 8 Battery",
        EcoWittSensorTypes.BATTERY_PERCENTAGE,
    ),
    "tf_ch1c": EcoWittMapping("Soil Temperature 1", EcoWittSensorTypes.TEMPERATURE_C),
    "tf_ch2c": EcoWittMapping("Soil Temperature 2", EcoWittSensorTypes.TEMPERATURE_C),
    "tf_ch3c": EcoWittMapping("Soil Temperature 3", EcoWittSensorTypes.TEMPERATURE_C),
    "tf_ch4c": EcoWittMapping("Soil Temperature 4", EcoWittSensorTypes.TEMPERATURE_C),
    "tf_ch5c": EcoWittMapping("Soil Temperature 5", EcoWittSensorTypes.TEMPERATURE_C),
    "tf_ch6c": EcoWittMapping("Soil Temperature 6", EcoWittSensorTypes.TEMPERATURE_C),
    "tf_ch7c": EcoWittMapping("Soil Temperature 7", EcoWittSensorTypes.TEMPERATURE_C),
    "tf_ch8c": EcoWittMapping("Soil Temperature 8", EcoWittSensorTypes.TEMPERATURE_C),
    "tf_ch1": EcoWittMapping("Soil Temperature 1", EcoWittSensorTypes.TEMPERATURE_F),
    "tf_ch2": EcoWittMapping("Soil Temperature 2", EcoWittSensorTypes.TEMPERATURE_F),
    "tf_ch3": EcoWittMapping("Soil Temperature 3", EcoWittSensorTypes.TEMPERATURE_F),
    "tf_ch4": EcoWittMapping("Soil Temperature 4", EcoWittSensorTypes.TEMPERATURE_F),
    "tf_ch5": EcoWittMapping("Soil Temperature 5", EcoWittSensorTypes.TEMPERATURE_F),
    "tf_ch6": EcoWittMapping("Soil Temperature 6", EcoWittSensorTypes.TEMPERATURE_F),
    "tf_ch7": EcoWittMapping("Soil Temperature 7", EcoWittSensorTypes.TEMPERATURE_F),
    "tf_ch8": EcoWittMapping("Soil Temperature 8", EcoWittSensorTypes.TEMPERATURE_F),
    "tf_batt1": EcoWittMapping(
        "Soil Temperature 1 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "tf_batt2": EcoWittMapping(
        "Soil Temperature 2 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "tf_batt3": EcoWittMapping(
        "Soil Temperature 3 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "tf_batt4": EcoWittMapping(
        "Soil Temperature 4 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "tf_batt5": EcoWittMapping(
        "Soil Temperature 5 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "tf_batt6": EcoWittMapping(
        "Soil Temperature 6 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "tf_batt7": EcoWittMapping(
        "Soil Temperature 7 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "tf_batt8": EcoWittMapping(
        "Soil Temperature 8 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "leafwetness_ch1": EcoWittMapping("Leaf Wetness 1", EcoWittSensorTypes.PERCENTAGE),
    "leafwetness_ch2": EcoWittMapping("Leaf Wetness 2", EcoWittSensorTypes.PERCENTAGE),
    "leafwetness_ch3": EcoWittMapping("Leaf Wetness 3", EcoWittSensorTypes.PERCENTAGE),
    "leafwetness_ch4": EcoWittMapping("Leaf Wetness 4", EcoWittSensorTypes.PERCENTAGE),
    "leafwetness_ch5": EcoWittMapping("Leaf Wetness 5", EcoWittSensorTypes.PERCENTAGE),
    "leafwetness_ch6": EcoWittMapping("Leaf Wetness 6", EcoWittSensorTypes.PERCENTAGE),
    "leafwetness_ch7": EcoWittMapping("Leaf Wetness 7", EcoWittSensorTypes.PERCENTAGE),
    "leafwetness_ch8": EcoWittMapping("Leaf Wetness 8", EcoWittSensorTypes.PERCENTAGE),
    "leaf_batt1": EcoWittMapping(
        "Leaf Wetness 1 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "leaf_batt2": EcoWittMapping(
        "Leaf Wetness 2 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "leaf_batt3": EcoWittMapping(
        "Leaf Wetness 3 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "leaf_batt4": EcoWittMapping(
        "Leaf Wetness 4 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "leaf_batt5": EcoWittMapping(
        "Leaf Wetness 5 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "leaf_batt6": EcoWittMapping(
        "Leaf Wetness 6 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "leaf_batt7": EcoWittMapping(
        "Leaf Wetness 7 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "leaf_batt8": EcoWittMapping(
        "Leaf Wetness 8 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE
    ),
    "depth_ch1": EcoWittMapping("Current Depth 1", EcoWittSensorTypes.DISTANCE_MM),
    "depth_ch2": EcoWittMapping("Current Depth 2", EcoWittSensorTypes.DISTANCE_MM),
    "depth_ch3": EcoWittMapping("Current Depth 3", EcoWittSensorTypes.DISTANCE_MM),
    "depth_ch4": EcoWittMapping("Current Depth 4", EcoWittSensorTypes.DISTANCE_MM),
    "thi_ch1": EcoWittMapping(
        "Total Historical Depth Index 1", EcoWittSensorTypes.DISTANCE_MM
    ),
    "thi_ch2": EcoWittMapping(
        "Total Historical Depth Index 2", EcoWittSensorTypes.DISTANCE_MM
    ),
    "thi_ch3": EcoWittMapping(
        "Total Historical Depth Index 3", EcoWittSensorTypes.DISTANCE_MM
    ),
    "thi_ch4": EcoWittMapping(
        "Total Historical Depth Index 4", EcoWittSensorTypes.DISTANCE_MM
    ),
    "air_ch1": EcoWittMapping("Air Gap 1", EcoWittSensorTypes.DISTANCE_MM),
    "air_ch2": EcoWittMapping("Air Gap 2", EcoWittSensorTypes.DISTANCE_MM),
    "air_ch3": EcoWittMapping("Air Gap 3", EcoWittSensorTypes.DISTANCE_MM),
    "air_ch4": EcoWittMapping("Air Gap 4", EcoWittSensorTypes.DISTANCE_MM),
    "ldsbatt1": EcoWittMapping("LDS 1 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "ldsbatt2": EcoWittMapping("LDS 2 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "ldsbatt3": EcoWittMapping("LDS 3 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "ldsbatt4": EcoWittMapping("LDS 4 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "ldsheat_ch1": EcoWittMapping("Heater-on Counter 1", EcoWittSensorTypes.HEAT_COUNT),
    "ldsheat_ch2": EcoWittMapping("Heater-on Counter 2", EcoWittSensorTypes.HEAT_COUNT),
    "ldsheat_ch3": EcoWittMapping("Heater-on Counter 3", EcoWittSensorTypes.HEAT_COUNT),
    "ldsheat_ch4": EcoWittMapping("Heater-on Counter 4", EcoWittSensorTypes.HEAT_COUNT),
    "dateutc": EcoWittMapping("dateutc", EcoWittSensorTypes.INTERNAL),
    "fields": EcoWittMapping("field list", EcoWittSensorTypes.INTERNAL),
    "ws85cap_volt": EcoWittMapping("WH85 Capacitor", EcoWittSensorTypes.VOLTAGE),
    "ws90cap_volt": EcoWittMapping("WH90 Capacitor", EcoWittSensorTypes.VOLTAGE),
    "rrain_piezo": EcoWittMapping(
        "Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "erain_piezo": EcoWittMapping(
        "Event Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_INCHES
    ),
    "hrain_piezo": EcoWittMapping(
        "Hourly Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_INCHES
    ),
    "drain_piezo": EcoWittMapping(
        "Daily Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_INCHES
    ),
    "wrain_piezo": EcoWittMapping(
        "Weekly Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_INCHES
    ),
    "mrain_piezo": EcoWittMapping(
        "Monthly Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_INCHES
    ),
    "yrain_piezo": EcoWittMapping(
        "Yearly Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_INCHES
    ),
    "srain_piezo": EcoWittMapping("Rain State Piezo", EcoWittSensorTypes.RAIN_STATE),
    "rrain_piezomm": EcoWittMapping("Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_MM),
    "erain_piezomm": EcoWittMapping(
        "Event Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_MM
    ),
    "hrain_piezomm": EcoWittMapping(
        "Hourly Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_MM
    ),
    "drain_piezomm": EcoWittMapping(
        "Daily Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_MM
    ),
    "wrain_piezomm": EcoWittMapping(
        "Weekly Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_MM
    ),
    "mrain_piezomm": EcoWittMapping(
        "Monthly Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_MM
    ),
    "yrain_piezomm": EcoWittMapping(
        "Yearly Rain Piezo", EcoWittSensorTypes.RAIN_COUNT_MM
    ),
    "runtime": EcoWittMapping("Runtime", EcoWittSensorTypes.INTERNAL),
    "interval": EcoWittMapping("Interval", EcoWittSensorTypes.INTERNAL),
    "heap": EcoWittMapping("Memory heap", EcoWittSensorTypes.INTERNAL),
}
