import time
from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrW
from fastcs.util import ONCE

from fastcs_wpi_micro4.usb_connection import USBConnection

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerLineSettingIORef(AttributeIORef):
    command: str
    _: KW_ONLY
    update_period: float | None = ONCE


# for the settings which require both the command and value
# query is the same a the comm
class WpiMicro4ControllerLineSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerLineSettingIORef]
):
    def __init__(self, connection: USBConnection):
        super().__init__()

        self._connection = connection

    async def send(
        self, attr: AttrW[NumberT, WpiMicro4ControllerLineSettingIORef], value: NumberT
    ) -> None:
        command = f"{attr.io_ref.command}{attr.dtype(value)}"
        try:
            r = await self._connection.send_query(f"{command}\r")
            if "OK" in r:
                await self.set(value, attr)
        except Exception as e:
            print(f"error: LINE query - {e}")

    # to allow for the initial value to be set
    async def update(
        self, attr: AttrR[NumberT, WpiMicro4ControllerLineSettingIORef]
    ) -> None:
        pass

    # rbv set based on the request no query for line number provided
    async def set(
        self, value, attr: AttrR[NumberT, WpiMicro4ControllerLineSettingIORef]
    ):
        await attr.update(attr.dtype(value))
        time.sleep(1)  # ????
