from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR
from fastcs.util import ONCE

from fastcs_wpi_micro4.usb_connection import USBConnection

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerQueryIORef(AttributeIORef):
    name: str
    response_prefix: str
    line_num: int
    _: KW_ONLY
    update_period: float | None = ONCE


class WpiMicro4ControllerQueryIO(AttributeIO[NumberT, WpiMicro4ControllerQueryIORef]):
    def __init__(self, connection: USBConnection):
        super().__init__()

        self._connection = connection

    async def update(self, attr: AttrR[NumberT, WpiMicro4ControllerQueryIORef]) -> None:
        line_command = f"L{attr.io_ref.line_num}"
        await self._connection.send_query(f"{line_command}\r")
        query = f"?{attr.io_ref.name}"
        response = await self._connection.send_query(f"{query}\r")
        if f"{attr.io_ref.response_prefix}" in response:
            value = response.strip(f"{attr.io_ref.response_prefix}" + " \n\rOK\n\r")
            if "L" in value:
                value = value[:-2]  # remove the units as well

            await attr.update(attr.dtype(value))
        else:
            raise Exception("Response doesn't much query")
