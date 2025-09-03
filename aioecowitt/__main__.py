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


async def run_server(ecowitt_ws: EcoWittListener) -> None:
    """Run server in endless mode."""
    event = asyncio.Event()
    await ecowitt_ws.start()
    # use event to wait endless instead of sleep in a loop
    await event.wait()


def main() -> None:
    """Run main."""
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    print(f"Firing up webserver to listen on port {sys.argv[1]}")
    ecowitt_server = EcoWittListener(port=sys.argv[1])

    ecowitt_server.new_sensor_cb.append(my_handler)
    try:
        asyncio.run(run_server(ecowitt_server))
    except Exception as err:  # pylint: disable=broad-except # noqa: BLE001
        print(str(err))
    print("Exiting")


if __name__ == "__main__":
    main()
