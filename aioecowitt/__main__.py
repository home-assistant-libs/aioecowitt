"""Run local Test server."""

from __future__ import annotations

import asyncio
import sys

from aioecowitt import EcoWittListener, EcoWittSensor


def usage() -> None:
    """Print usage of the CLI."""
    print(f"Usage: {sys.argv[0]} port")


async def my_handler(sensor: EcoWittSensor) -> None:
    """Callback handler for printing data."""
    print("In my handler")
    print(f"{sensor!s}")


def main() -> None:
    """Run main."""
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    print(f"Firing up webserver to listen on port {sys.argv[1]}")
    ecowitt_server = EcoWittListener(port=sys.argv[1])

    ecowitt_server.new_sensor_cb.append(my_handler)
    loop = asyncio.new_event_loop()
    loop.create_task(ecowitt_server.start())  # noqa: RUF006

    try:
        loop.run_forever()
    except Exception as err:  # pylint: disable=broad-except # noqa: BLE001
        print(str(err))
    print("Exiting")


if __name__ == "__main__":
    main()
