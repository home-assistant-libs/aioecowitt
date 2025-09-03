"""aioEcoWitt API server."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from aiohttp import web

from .calc import weather_datapoints
from .sensor import SENSOR_MAP, EcoWittSensor
from .station import EcoWittStation, extract_station

if TYPE_CHECKING:
    from collections.abc import Callable

_LOGGER = logging.getLogger(__name__)
_ECOWITT_LISTEN_PORT = 49199


class EcoWittListener:
    """EcoWitt Server API server."""

    def __init__(
        self, port: int = _ECOWITT_LISTEN_PORT, path: str | None = None
    ) -> None:
        """Initialize EcoWitt Server."""
        # API Constants
        self.port: int = port
        self.path: str = path

        # webserver
        self.server: None | web.Server = None
        self.runner: None | web.ServerRunner = None
        self.site: None | web.TCPSite = None

        # internal data
        self.last_values: dict[str, dict[str, str | None]] = {}
        self.new_sensor_cb: list[Callable[[EcoWittSensor], None]] = []
        self._warned_unknown: set[str] = set()

        # storage
        self.sensors: dict[str, EcoWittSensor] = {}
        self.stations: dict[str, EcoWittStation] = {}

    def _new_sensor_cb(self, sensor: EcoWittSensor) -> None:
        """Internal new sensor callback.

        binds to self.new_sensor_cb
        """
        for callback in self.new_sensor_cb:
            callback(sensor)

    def process_data(self, data: dict[str, str | float | int | None]) -> None:
        """Process data from weather station."""
        data = data.copy()
        station = extract_station(data)
        weather_data = weather_datapoints(data)

        # add station to list
        if station.key not in self.stations:
            _LOGGER.debug("Found new station: %s", station.key)
            self.stations[station.key] = station
        else:
            station = self.stations[station.key]

        last_update = time.time()
        last_update_m = time.monotonic()

        for datapoint in weather_data:
            sensor_id = f"{station.key}.{datapoint}"
            sensor = self.sensors.get(sensor_id)
            if sensor is None:
                # we have a new sensor
                if datapoint not in SENSOR_MAP:
                    if datapoint not in self._warned_unknown:
                        self._warned_unknown.add(datapoint)
                        _LOGGER.warning(
                            "Unhandled sensor type %s value %s",
                            datapoint,
                            weather_data[datapoint],
                        )
                    continue
                metadata = SENSOR_MAP[datapoint]

                sensor = EcoWittSensor(
                    metadata.name, datapoint, metadata.stype, station
                )
                self.sensors[sensor_id] = sensor
                try:
                    self._new_sensor_cb(sensor)
                except Exception as err:  # pylint: disable=broad-except # noqa: BLE001
                    _LOGGER.warning("EcoWitt new sensor callback error: %s", err)

            try:
                sensor.update_value(weather_data[datapoint], last_update, last_update_m)
            except Exception as err:  # pylint: disable=broad-except # noqa: BLE001
                _LOGGER.warning("Sensor update error: %s", err)

    async def handler(self, request: web.BaseRequest) -> web.Response:
        """AIOHTTP handler for the API."""
        if request.method != "POST":
            return web.Response(status=405)
        if self.path is not None and request.path != self.path:
            return web.Response(status=404)
        data = await request.post()
        _LOGGER.debug("Received data: %s", data)

        # data is not a dict, it's a MultiDict
        self.last_values[data["PASSKEY"]] = data.copy()
        self.last_values[data["PASSKEY"]].pop("PASSKEY")
        self.process_data(data)

        return web.Response(text="OK")

    async def start(self) -> None:
        """Listen and process."""
        self.server = web.Server(self.handler)
        self.runner = web.ServerRunner(self.server)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, port=self.port)
        await self.site.start()

    async def stop(self) -> None:
        """Stop listening."""
        await self.site.stop()
