"""Weather datapoint calculator."""

from __future__ import annotations

from typing import TYPE_CHECKING

import meteocalc

from .sensor import SENSOR_MAP

if TYPE_CHECKING:
    import datetime as dt

_INCHES_2_MM = 25.4
_WATT_METERS_SQUARED_2_LUX = 0.0079
_MPH_2_KMH = 1.60934
_KM_2_MI = 0.6213712
_INHG_2_HPA = 33.86


def convert_fahrenheit_to_celsius(
    data: dict[str, str | int | float | dt.datetime | None],
    key_source: str,
    key_destination: str,
) -> None:
    """Convert f to c."""
    if key_source in data:
        data[key_destination] = round(meteocalc.Temp(data[key_source], "F").c, 1)


def _convert_inches_to_mm(
    data: dict[str, str | int | float | dt.datetime | None],
    key_source: str,
    key_destination: str,
) -> None:
    """Convert source value from inches to mm and save it into destination."""
    if key_source in data:
        data[key_destination] = round(data[key_source] * _INCHES_2_MM, 1)


def weather_datapoints(  # noqa: C901, PLR0912
    data: dict[str, str],
) -> dict[str, str | int | float | dt.datetime | None]:
    """Calculate and convert weather data."""
    for key, value in data.copy().items():
        if key in SENSOR_MAP:
            mapping = SENSOR_MAP[key]
            if value:
                data[key] = mapping.stype.convert_fn(value)
            else:
                data[key] = None

    if "solarradiation" in data:
        data["solarradiation_lux"] = round(
            data["solarradiation"] / _WATT_METERS_SQUARED_2_LUX, 1
        )

    # lightning
    if value := data.get("lightning"):
        data["lightning_mi"] = round(value * _KM_2_MI)

    for source, dst in (
        ("tempf", "tempc"),
        ("tempinf", "tempinc"),
        ("tf_co2", "tf_co2c"),
        ("temp1f", "temp1c"),
        ("temp2f", "temp2c"),
        ("temp3f", "temp3c"),
        ("temp4f", "temp4c"),
        ("temp5f", "temp5c"),
        ("temp6f", "temp6c"),
        ("temp7f", "temp7c"),
        ("temp8f", "temp8c"),
        ("tf_ch1", "tf_ch1c"),
        ("tf_ch2", "tf_ch2c"),
        ("tf_ch3", "tf_ch3c"),
        ("tf_ch4", "tf_ch4c"),
        ("tf_ch5", "tf_ch5c"),
        ("tf_ch6", "tf_ch6c"),
        ("tf_ch7", "tf_ch7c"),
        ("tf_ch8", "tf_ch8c"),
    ):
        convert_fahrenheit_to_celsius(data, source, dst)

    # speeds
    for source, dst in (
        ("windspeedmph", "windspeedkmh"),
        ("windgustmph", "windgustkmh"),
        ("maxdailygust", "maxdailygustkmh"),
        ("windspdmph_avg10m", "windspdkmh_avg10m"),
    ):
        if source in data:
            data[dst] = round(data[source] * _MPH_2_KMH, 1)

    for key in (
        "eventrain",
        "hourlyrain",
        "dailyrain",
        "weeklyrain",
        "monthlyrain",
        "yearlyrain",
        "totalrain",
        "rainrate",
    ):
        _convert_inches_to_mm(data, f"{key}in", f"{key}mm")

    for key in (
        "erain_piezo",
        "hrain_piezo",
        "drain_piezo",
        "wrain_piezo",
        "mrain_piezo",
        "yrain_piezo",
        "rrain_piezo",
    ):
        _convert_inches_to_mm(data, key, f"{key}mm")

    # Pressure
    for key in ("baromrel", "baromabs"):
        if value := data.get(f"{key}in"):
            data[f"{key}hpa"] = round(value * _INHG_2_HPA, 1)

    # Wind chill
    if "tempf" in data and "windspeedmph" in data:
        try:
            wind_chill = meteocalc.wind_chill(data["tempf"], data["windspeedmph"])
        except ValueError:
            data["windchillf"] = None
            data["windchillc"] = None
        else:
            data["windchillf"] = round(wind_chill.f, 1)
            data["windchillc"] = round(wind_chill.c, 1)

    # Dew point
    for j in ["", "in", "1", "2", "3", "4", "5", "6", "7", "8"]:
        if f"temp{j}c" in data and f"humidity{j}" in data:
            dewpoint = meteocalc.dew_point(data[f"temp{j}c"], data[f"humidity{j}"])
            data[f"dewpoint{j}c"] = round(dewpoint.c, 1)
            data[f"dewpoint{j}f"] = round(dewpoint.f, 1)

    # Feels like
    if "tempf" in data and "humidity" in data and "windspeedmph" in data:
        feels_like = meteocalc.feels_like(
            data["tempf"], data["humidity"], data["windspeedmph"]
        )
        data["tempfeelsf"] = round(feels_like.f, 1)
        data["tempfeelsc"] = round(feels_like.c, 1)

    return data
