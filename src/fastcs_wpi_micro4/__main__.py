"""Interface for ``python -m fastcs_kds_legato``."""

from pathlib import Path
from typing import Optional

import typer
from fastcs.launch import FastCS
from fastcs.transports.epics import EpicsIOCOptions
from fastcs.transports.epics.ca.transport import EpicsCATransport
from fastcs.transports.epics.options import EpicsGUIOptions

from fastcs_wpi_micro4 import __version__
from fastcs_wpi_micro4.usb_connection import USBConnectionSettings
from fastcs_wpi_micro4.wpi_micro4_controller import WpiMicro4Controller

__all__ = ["main"]

app = typer.Typer()

OPI_PATH = Path("/epics/opi")


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    # TODO: typer does not support `bool | None` yet
    # https://github.com/tiangolo/typer/issues/533
    version: Optional[bool] = typer.Option(  # noqa
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print the version and exit",
    ),
):
    pass


@app.command()
def ioc(pv_prefix: str = typer.Argument()):
    ui_path = OPI_PATH if OPI_PATH.is_dir() else Path.cwd()

    connection_settings = USBConnectionSettings("/dev/ttyUSB0", 9600)
    # Create a controller instance
    controller = WpiMicro4Controller(connection_settings)

    # IOC options
    options = EpicsCATransport(
        epicsca=EpicsIOCOptions(pv_prefix=pv_prefix),
        gui=EpicsGUIOptions(
            output_path=ui_path / "wpi_micro4.bob", title=f"WPI-MICRO4 - {pv_prefix}"
        ),
    )

    # ...and pass them both to FastCS
    launcher = FastCS(controller, [options])  # type: ignore
    # launcher.create_docs()
    # launcher.create_gui()
    launcher.run()  # type: ignore


if __name__ == "__main__":
    app()
