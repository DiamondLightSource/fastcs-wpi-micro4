from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrW
from fastcs.util import ONCE

from fastcs_wpi_micro4.usb_connection import USBConnection

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerCommandSettingIORef(AttributeIORef):
    name: str
    line_num: int
    _: KW_ONLY
    update_period: float | None = ONCE


# for the settings which only requires command only
class WpiMicro4ControllerCommandSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerCommandSettingIORef]
):
    def __init__(self, connection: USBConnection):
        super().__init__()

        self._connection = connection

    async def send(
        self,
        attr: AttrW[NumberT, WpiMicro4ControllerCommandSettingIORef],
        value: NumberT,
    ) -> None:
        line_command = f"L{attr.io_ref.line_num}"
        command = f"{attr.dtype(value)}"
        try:
            await self._connection.send_query(f"{line_command}\r")
            r = await self._connection.send_query(f"{command}\r")
            v = r.strip(";\n ")
            chars = list(v)
            print(r, " val only:", chars[1])
            if len(chars) > 0:
                setting = chars[1]
                if setting in {"1", "3", "6"}:
                    setting = "T"
                elif setting in {"2", "4", "7"}:
                    setting = "F"
                await attr.update(attr.dtype(setting))
        except Exception as e:
            print(f"error: new line query - {e}")
            # await self._connection.connect(IPConnectionSettings("192.168.1.6", 7004))

    # run once at init stage
    async def update(
        self, attr: AttrR[NumberT, WpiMicro4ControllerCommandSettingIORef]
    ) -> None:
        line_command = f"L{attr.io_ref.line_num};"
        await self._connection.send_command(f"{line_command}\r")
        query = f"?{attr.io_ref.name}"
        response = await self._connection.send_query(f"{query}\r")
        value = response.strip(query + "; \r \n")

        await attr.update(attr.dtype(value))
