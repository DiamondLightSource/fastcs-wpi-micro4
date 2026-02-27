from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrW

from fastcs_wpi_micro4.usb_connection import USBConnection

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerCommandIORef(AttributeIORef):
    command: str
    line_num: int
    _: KW_ONLY
    update_period: float | None = None


# for the settings which require both the command and value
# query is the same a the comm
class WpiMicro4ControllerCommandIO(
    AttributeIO[NumberT, WpiMicro4ControllerCommandIORef]
):
    def __init__(self, connection: USBConnection):
        super().__init__()

        self._connection = connection

    async def send(
        self, attr: AttrW[NumberT, WpiMicro4ControllerCommandIORef], value: NumberT
    ) -> None:
        line_command = f"L{attr.io_ref.line_num};"
        command = f"{attr.io_ref.command}{attr.dtype(value)}"
        try:
            await self._connection.send_query(f"{line_command}\r")
            r = await self._connection.send_query(f"{command}\r")
            print(r)
        except Exception as e:
            print(f"error: LINE query - {e}")
