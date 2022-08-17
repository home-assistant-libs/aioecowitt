"""Sensor and mapping data from ecowitt."""
from __future__ import annotations
from typing import Callable

from dataclasses import dataclass, field
import enum

from .station import EcoWittStation


@dataclass
class EcoWittSensor:
    """An internal sensor to the ecowitt."""

    name: str
    key: str
    stype: EcoWittSensorTypes
    station: EcoWittStation
    value: None | str | int | float = field(default=None, init=False)
    last_update: float = field(default=0, init=False)
    last_update_m: float = field(default=0, init=False)
    update_cb: list[Callable[[None], None]] = field(default_factory=list, init=False)

    def update_value(
        self, value: None | str | int | float, last_update: float, last_update_m: float
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


class EcoWittSensorTypes(enum.Enum):
    """EcoWitt sensor types."""

    INTERNAL = 1
    PRESSURE_HPA = 2
    PRESSURE_INHG = 3
    RAIN_RATE_MM = 4
    RAIN_RATE_INCHES = 5
    HUMIDITY = 6
    DEGREE = 7
    SPEED_KPH = 8
    SPEED_MPH = 9
    TEMPERATURE_C = 10
    TEMPERATURE_F = 11
    WATT_METERS_SQUARED = 12
    UV_INDEX = 13
    PM25 = 14
    PM10 = 15
    TIMESTAMP = 16
    LIGHTNING_COUNT = 17
    LIGHTNING_DISTANCE_KM = 18
    LIGHTNING_DISTANCE_MILES = 19
    LEAK = 20
    VOLTAGE = 21
    BATTERY_BINARY = 22
    BATTERY_VOLTAGE = 23
    BATTERY_PERCENTAGE = 24
    CO2_PPM = 25
    LUX = 26


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
    "rainratein": EcoWittMapping("Rain Rate", EcoWittSensorTypes.RAIN_RATE_INCHES),
    "eventrainin": EcoWittMapping(
        "Event Rain Rate", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "hourlyrainin": EcoWittMapping(
        "Hourly Rain Rate", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "totalrainin": EcoWittMapping("Total Rain", EcoWittSensorTypes.RAIN_RATE_INCHES),
    "dailyrainin": EcoWittMapping(
        "Daily Rain Rate", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "weeklyrainin": EcoWittMapping(
        "Weekly Rain Rate", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "monthlyrainin": EcoWittMapping(
        "Monthly Rain Rate", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "yearlyrainin": EcoWittMapping(
        "Yearly Rain Rate", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "rainratemm": EcoWittMapping("Rain Rate", EcoWittSensorTypes.RAIN_RATE_MM),
    "eventrainmm": EcoWittMapping("Event Rain Rate", EcoWittSensorTypes.RAIN_RATE_MM),
    "hourlyrainmm": EcoWittMapping("Hourly Rain Rate", EcoWittSensorTypes.RAIN_RATE_MM),
    "totalrainmm": EcoWittMapping("Total Rain", EcoWittSensorTypes.RAIN_RATE_MM),
    "dailyrainmm": EcoWittMapping("Daily Rain Rate", EcoWittSensorTypes.RAIN_RATE_MM),
    "weeklyrainmm": EcoWittMapping("Weekly Rain Rate", EcoWittSensorTypes.RAIN_RATE_MM),
    "monthlyrainmm": EcoWittMapping(
        "Monthly Rain Rate", EcoWittSensorTypes.RAIN_RATE_MM
    ),
    "yearlyrainmm": EcoWittMapping("Yearly Rain Rate", EcoWittSensorTypes.RAIN_RATE_MM),
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
    "soilmoisture1": EcoWittMapping("Soil Moisture 1", EcoWittSensorTypes.HUMIDITY),
    "soilmoisture2": EcoWittMapping("Soil Moisture 2", EcoWittSensorTypes.HUMIDITY),
    "soilmoisture3": EcoWittMapping("Soil Moisture 3", EcoWittSensorTypes.HUMIDITY),
    "soilmoisture4": EcoWittMapping("Soil Moisture 4", EcoWittSensorTypes.HUMIDITY),
    "soilmoisture5": EcoWittMapping("Soil Moisture 5", EcoWittSensorTypes.HUMIDITY),
    "soilmoisture6": EcoWittMapping("Soil Moisture 6", EcoWittSensorTypes.HUMIDITY),
    "soilmoisture7": EcoWittMapping("Soil Moisture 7", EcoWittSensorTypes.HUMIDITY),
    "soilmoisture8": EcoWittMapping("Soil Moisture 8", EcoWittSensorTypes.HUMIDITY),
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
    "soilbatt1": EcoWittMapping("Soil Battery 1", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt2": EcoWittMapping("Soil Battery 2", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt3": EcoWittMapping("Soil Battery 3", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt4": EcoWittMapping("Soil Battery 4", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt5": EcoWittMapping("Soil Battery 5", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt6": EcoWittMapping("Soil Battery 6", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt7": EcoWittMapping("Soil Battery 7", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "soilbatt8": EcoWittMapping("Soil Battery 8", EcoWittSensorTypes.BATTERY_VOLTAGE),
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
    "dateutc": EcoWittMapping("dateutc", EcoWittSensorTypes.INTERNAL),
    "fields": EcoWittMapping("field list", EcoWittSensorTypes.INTERNAL),
    "wh90batt": EcoWittMapping("WH90 Battery", EcoWittSensorTypes.BATTERY_VOLTAGE),
    "wh90battpc": EcoWittMapping(
        "WH90 Battery Percentage",
        EcoWittSensorTypes.BATTERY_PERCENTAGE,
    ),
    "ws90cap_volt": EcoWittMapping("WH90 Capacitor", EcoWittSensorTypes.VOLTAGE),
    "rrain_piezo": EcoWittMapping(
        "Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "erain_piezo": EcoWittMapping(
        "Event Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "hrain_piezo": EcoWittMapping(
        "Hourly Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "drain_piezo": EcoWittMapping(
        "Daily Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "wrain_piezo": EcoWittMapping(
        "Weekly Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "mrain_piezo": EcoWittMapping(
        "Monthly Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "yrain_piezo": EcoWittMapping(
        "Yearly Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_INCHES
    ),
    "rrain_piezomm": EcoWittMapping("Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_MM),
    "erain_piezomm": EcoWittMapping(
        "Event Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_MM
    ),
    "hrain_piezomm": EcoWittMapping(
        "Hourly Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_MM
    ),
    "drain_piezomm": EcoWittMapping(
        "Daily Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_MM
    ),
    "wrain_piezomm": EcoWittMapping(
        "Weekly Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_MM
    ),
    "mrain_piezomm": EcoWittMapping(
        "Monthly Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_MM
    ),
    "yrain_piezomm": EcoWittMapping(
        "Yearly Rain Rate Piezo", EcoWittSensorTypes.RAIN_RATE_MM
    ),
    "runtime": EcoWittMapping("Runtime", EcoWittSensorTypes.INTERNAL),
}
