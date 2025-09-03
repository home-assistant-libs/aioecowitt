"""Test for stations from station.py."""

from aioecowitt import station

from .const import EASYWEATHER_DATA, GW2000A_DATA


def test_gw2000a_v2() -> None:
    """Test Calculated values from GW2000A_V2."""
    ecowitt_station = station.extract_station(GW2000A_DATA)

    assert "PASSKEY" not in GW2000A_DATA
    assert "model" not in GW2000A_DATA
    assert "frequence" not in GW2000A_DATA
    assert "stationtype" not in GW2000A_DATA
    assert "ws90_ver" not in GW2000A_DATA

    assert ecowitt_station.station == "GW2000A_V2.1.5"
    assert ecowitt_station.key == "345544D8EAF42E1B8824A86D8250D5A3"
    assert ecowitt_station.model == "GW2000A"
    assert ecowitt_station.version == "119"
    assert ecowitt_station.frequence == "868M"


def test_easyweather() -> None:
    """Test EasyWeather station."""
    ecowitt_station = station.extract_station(EASYWEATHER_DATA)

    assert "PASSKEY" not in EASYWEATHER_DATA
    assert "model" not in EASYWEATHER_DATA
    assert "frequence" not in EASYWEATHER_DATA
    assert "stationtype" not in EASYWEATHER_DATA

    assert ecowitt_station.station == "EasyWeatherV1.4.9"
    assert ecowitt_station.key == "34271334ED1FADA6D8B988B14267E55D"
    assert ecowitt_station.model == "HP3500_V1.6.2"
    assert ecowitt_station.frequence == "915M"
