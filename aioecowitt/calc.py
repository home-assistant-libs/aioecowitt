"""Weather datapoint calculator."""
from __future__ import annotations

import meteocalc


def _ftoc(fahrenheit: float | str) -> float:
    """Convert f to c."""
    return round(meteocalc.Temp(fahrenheit, "F").c, 1)


def _volt_to_percent(volt: float, low: float, high: float) -> float | int:
    percent = round(((volt - low) / (high - low)) * 100)
    if percent < 0:
        percent = 0
    elif percent > 100:
        percent = 100
    return percent


def weather_datapoints(data: dict[str, str]) -> dict[str, str | int | float | None]:
    """Calculate and convert weather data."""
    mph_kmh = 1.60934
    in_hpa = 33.86
    in_mm = 25.4
    km_mi = 0.6213712
    wm_lux = 0.0079

    # basic conversions
    if "humidityin" in data:
        data["humidityin"] = int(data["humidityin"])
    if "humidity" in data:
        data["humidity"] = int(data["humidity"])
    if "winddir" in data:
        data["winddir"] = int(data["winddir"])
    if "winddir_avg10m" in data:
        data["winddir_avg10m"] = int(data["winddir_avg10m"])
    if "uv" in data:
        data["uv"] = int(data["uv"])
    if "solarradiation" in data:
        data["solarradiation"] = float(data["solarradiation"])
        data["solarradiation_lux"] = round(data["solarradiation"] / wm_lux, 1)

    # lightning
    if "lightning_time" in data:
        if data["lightning_time"] is not None and data["lightning_time"] != "":
            data["lightning_time"] = int(data["lightning_time"])
    if "lightning_num" in data:
        data["lightning_num"] = int(data["lightning_num"])
    if "lightning" in data:
        if data["lightning"] is not None and data["lightning"] != "":
            data["lightning"] = int(data["lightning"])
            data["lightning_mi"] = int(round(data["lightning"] * km_mi))

    # temperatures
    if "tempf" in data:
        data["tempf"] = float(data["tempf"])
        data["tempc"] = _ftoc(data["tempf"])
    if "tempinf" in data:
        data["tempinf"] = float(data["tempinf"])
        data["tempinc"] = _ftoc(data["tempinf"])
    # (WH45)
    if "tf_co2" in data:
        data["tf_co2"] = float(data["tf_co2"])
        data["tf_co2c"] = _ftoc(data["tf_co2"])
    # WN34 Soil Temperature Sensor
    for j in range(1, 9):
        wnf = f"tf_ch{j}"
        wnc = f"tf_ch{j}c"
        if wnf in data:
            data[wnf] = float(data[wnf])
            data[wnc] = _ftoc(data[wnf])

    # numbered WH31 temp/humid
    for j in range(1, 9):
        tmpf = f"temp{j}f"
        tmpc = f"temp{j}c"
        hum = f"humidity{j}"
        if tmpf in data:
            data[tmpf] = float(data[tmpf])
            data[tmpc] = _ftoc(data[tmpf])
        if hum in data:
            data[hum] = int(data[hum])

    # speeds
    if "windspeedmph" in data:
        data["windspeedmph"] = float(data["windspeedmph"])
        data["windspeedkmh"] = round(data["windspeedmph"] * mph_kmh, 1)
    if "windgustmph" in data:
        data["windgustmph"] = float(data["windgustmph"])
        data["windgustkmh"] = round(data["windgustmph"] * mph_kmh, 1)
    # I assume this is MPH?
    if "maxdailygust" in data:
        data["maxdailygust"] = float(data["maxdailygust"])
        data["maxdailygustkmh"] = round(data["maxdailygust"] * mph_kmh, 1)
    if "windspdmph_avg10m" in data:
        data["windspdmph_avg10m"] = float(data["windspdmph_avg10m"])
        data["windspdkmh_avg10m"] = round(float(data["windspdmph_avg10m"] * mph_kmh), 1)

    # distances
    if "rainratein" in data:
        data["rainratein"] = float(data["rainratein"])
        data["rainratemm"] = round(data["rainratein"] * in_mm, 1)
    if "eventrainin" in data:
        data["eventrainin"] = float(data["eventrainin"])
        data["eventrainmm"] = round(data["eventrainin"] * in_mm, 1)
    if "hourlyrainin" in data:
        data["hourlyrainin"] = float(data["hourlyrainin"])
        data["hourlyrainmm"] = round(data["hourlyrainin"] * in_mm, 1)
    if "dailyrainin" in data:
        data["dailyrainin"] = float(data["dailyrainin"])
        data["dailyrainmm"] = round(data["dailyrainin"] * in_mm, 1)
    if "weeklyrainin" in data:
        data["weeklyrainin"] = float(data["weeklyrainin"])
        data["weeklyrainmm"] = round(data["weeklyrainin"] * in_mm, 1)
    if "monthlyrainin" in data:
        data["monthlyrainin"] = float(data["monthlyrainin"])
        data["monthlyrainmm"] = round(data["monthlyrainin"] * in_mm, 1)
    if "yearlyrainin" in data:
        data["yearlyrainin"] = float(data["yearlyrainin"])
        data["yearlyrainmm"] = round(data["yearlyrainin"] * in_mm, 1)
    if "totalrainin" in data:
        data["totalrainin"] = float(data["totalrainin"])
        data["totalrainmm"] = round(data["totalrainin"] * in_mm, 1)

    # piezo rain sensor
    if "rrain_piezo" in data:
        data["rrain_piezo"] = float(data["rrain_piezo"])
        data["rrain_piezomm"] = round(data["rrain_piezo"] * in_mm, 1)
    if "erain_piezo" in data:
        data["erain_piezo"] = float(data["erain_piezo"])
        data["erain_piezomm"] = round(data["erain_piezo"] * in_mm, 1)
    if "hrain_piezo" in data:
        data["hrain_piezo"] = float(data["hrain_piezo"])
        data["hrain_piezomm"] = round(data["hrain_piezo"] * in_mm, 1)
    if "drain_piezo" in data:
        data["drain_piezo"] = float(data["drain_piezo"])
        data["drain_piezomm"] = round(data["drain_piezo"] * in_mm, 1)
    if "wrain_piezo" in data:
        data["wrain_piezo"] = float(data["wrain_piezo"])
        data["wrain_piezomm"] = round(data["wrain_piezo"] * in_mm, 1)
    if "mrain_piezo" in data:
        data["mrain_piezo"] = float(data["mrain_piezo"])
        data["mrain_piezomm"] = round(data["mrain_piezo"] * in_mm, 1)
    if "yrain_piezo" in data:
        data["yrain_piezo"] = float(data["yrain_piezo"])
        data["yrain_piezomm"] = round(data["yrain_piezo"] * in_mm, 1)

    # Pressure
    if "baromrelin" in data:
        data["baromrelin"] = float(data["baromrelin"])
        data["baromrelhpa"] = round(data["baromrelin"] * in_hpa, 1)
    if "baromabsin" in data:
        data["baromabsin"] = float(data["baromabsin"])
        data["baromabshpa"] = round(data["baromabsin"] * in_hpa, 1)

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
            data["tempf"], data["windspeedmph"], data["humidity"]
        )
        data["tempfeelsf"] = round(feels_like.f, 1)
        data["tempfeelsc"] = round(feels_like.c, 1)

    # Soil moisture (WH51)
    for j in range(1, 9):
        name = f"soilmoisture{j}"
        if name in data:
            data[name] = int(data[name])

    # PM 2.5 sensor (WH41)
    for j in range(1, 5):
        pmc = f"pm25_ch{j}"
        pma = f"pm25_avg_24h_ch{j}"
        if pmc in data:
            data[pmc] = float(data[pmc])
        if pma in data:
            data[pma] = float(data[pma])

    # Leak sensor (WH55)
    for j in range(1, 5):
        leak = f"leak_ch{j}"
        if leak in data:
            data[leak] = int(data[leak])

    # CO2 indoor air quality (WH45) (note temp is in temps above)
    pm_floats = [
        "pm25",
        "pm25_24h",
        "pm10",
        "pm10_24",
    ]
    for prefix in pm_floats:
        name = f"{prefix}_co2"
        if name in data:
            data[name] = float(data[name])
    if "co2" in data:
        data["co2"] = int(data["co2"])
    if "co2_24h" in data:
        data["co2_24h"] = int(data["co2_24h"])
    if "humi_co2" in data:
        data["humi_co2"] = int(data["humi_co2"])

    # Batteries
    bat_names = [
        "wh25",
        "wh26",
        "wh40",
        "wh57",
        "wh65",
        "wh68",
        "wh80",
        "wh90",
        "co2_",
    ]
    bat_range_names = [
        "soil",
        "",  # for just 'batt'
        "pm25",
        "leak",
        "tf_",  # WN34 voltage type
    ]

    for prefix in bat_names:
        name = f"{prefix}batt"
        if name in data:
            data[name] = float(data[name])

    for r_prefix in bat_range_names:
        for j in range(1, 9):
            name = f"{r_prefix}batt{j}"
            if name in data:
                data[name] = float(data[name])

    # percentage battery for device view
    if "wh90batt" in data:
        data["wh90battpc"] = _volt_to_percent(data["wh90batt"], 2.4, 3.0)
        data["ws90cap_volt"] = float(data["ws90cap_volt"])

    return data
