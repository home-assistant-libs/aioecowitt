"""Station mapping from ecowitt."""

from __future__ import annotations

from dataclasses import dataclass, field

VERSION_FIELDS = {
    "ws90_ver",
}


@dataclass
class EcoWittStation:
    """An internal ecowitt station."""

    station: str
    model: str
    frequence: str | None
    key: str
    version: None | str = field(default=None)


def extract_station(data: dict[str, str]) -> EcoWittStation:
    """Extract station from data."""
    station = data.pop("stationtype")
    passkey = data.pop("PASSKEY")
    model = data.pop("model")
    frequence = data.pop("freq", None)

    version = None
    for value in VERSION_FIELDS:
        if value not in data:
            continue
        version = data.pop(value)
        break

    return EcoWittStation(
        station=station, model=model, frequence=frequence, key=passkey, version=version
    )
