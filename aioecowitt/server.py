"""aioEcoWitt API server."""
from __future__ import annotations

import logging
import time
from typing import Callable

from aiohttp import web

from .sensor import EcoWittSensor, SENSOR_MAP, EcoWittSensorTypes
from . import calc

_LOGGER = logging.getLogger(__name__)
_ECOWITT_LISTEN_PORT = 49199


class EcoWittListener:
    """EcoWitt Server API server."""

    def __init__(self, port: int = _ECOWITT_LISTEN_PORT, path: str = None):
        """Initialize EcoWitt Server."""
        # API Constants
        self.port: int = port
        self.path: str = path

        # webserver
        self.server: None | web.Server = None
        self.runner: None | web.ServerRunner = None
        self.site: None | web.TCPSite = None

        # internal data
        self.last_values: dict[str, str | int | float | None] = {}
        self.lastupd: float = 0
        self.new_sensor_cb: list[Callable[[EcoWittSensor], None]] = []

        # storage
        self._station_type: str = "Unknown"
        self._station_freq: str = "Unknown"
        self._station_model: str = "Unknown"
        self._mac_addr: None | str = None

        self.sensors: dict[str, EcoWittSensor] = {}

    def _new_sensor_cb(self, sensor: EcoWittSensor) -> None:
        """Internal new sensor callback

        binds to self.new_sensor_cb
        """
        for callback in self.new_sensor_cb:
            callback(sensor)

    def process_data(self, weather_data: dict[str, str | float | int | None]) -> None:
        """Process data from weather station."""
        station = weather_data["PASSKEY"]
        last_update = time.time()
        last_update_m = time.monotonic()

        for datapoint in weather_data.keys():
            sensor = self.sensors.get(datapoint)
            if sensor is None:
                # we have a new sensor
                if datapoint not in SENSOR_MAP:
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
                self.sensors[datapoint] = sensor
                try:
                    self._new_sensor_cb(sensor)
                except Exception as err:  # pylint: disable=broad-except
                    _LOGGER.warning("EcoWitt new sensor callback error: %s", err)

            try:
                sensor.update_value(weather_data[datapoint], last_update, last_update_m)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Sensor update error: %s", err)

    async def handler(self, request: web.BaseRequest) -> web.Response:
        """AIOHTTP handler for the API."""
        if request.method != "POST":
            return web.Response(status=405)
        if self.path is not None and request.path != self.path:
            return web.Response(status=404)
        data = await request.post()

        # data is not a dict, it's a MultiDict
        weather_data = calc.weather_datapoints({**data})
        self.last_values = weather_data.copy()
        self.lastupd = time.time()
        self.process_data(weather_data)

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

    def list_sensor_keys(self) -> list[str]:
        """List all available sensors by key."""
        return [sensor.key for sensor in self.sensors]

    def list_sensor_keys_by_type(self, stype: EcoWittSensorTypes) -> list[str]:
        """List all available sensors of a given type."""
        sensor_list = []
        for sensor in self.sensors:
            if sensor.stype == stype:
                sensor_list.append(sensor.key)
        return sensor_list

    def get_sensor_value_by_key(self, key: str) -> None | str | int | float:
        """Find the sensor named key and return its value."""
        sensor = self.sensors.get(key)
        if sensor is None:
            return None
        return sensor.value
