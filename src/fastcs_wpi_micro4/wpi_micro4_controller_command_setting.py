from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrW
from fastcs.util import ONCE

from fastcs_wpi_micro4.usb_connection import USBConnection

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerCommandSettingNameDict:
    # maps names inserted by the user in the GUI to acuall Commands
    name_to_symbol = {
        "Infuse": "I",
        "Paused": "U",
        "nL/Sec": "S",
        "nL/Min": "M",
        "Non-Grouped": "N",
        "Grupped": "G",
        "Disabled": "D",
        "Max Load Drive": "BT",
        "Smooth Drive": "BS",
        "Delivered Volume": "EN",
        "Remaining Volume": "EI",
    }


@dataclass
class WpiMicro4ControllerCommandSettingIORef(AttributeIORef):
    name: str
    response_prefix: str
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
        command_long = f"{attr.dtype(value)}"
        command = WpiMicro4ControllerCommandSettingNameDict.name_to_symbol[command_long]
        try:
            await self._connection.send_query(f"{line_command}\r")
            r = await self._connection.send_query(f"{command}\r")
            if "OK" in r:
                await self.update(attr)
        except Exception as e:
            print(f"error: new line query - {e}")

    # run once at init stage
    async def update(
        self, attr: AttrR[NumberT, WpiMicro4ControllerCommandSettingIORef]
    ) -> None:
        line_command = f"L{attr.io_ref.line_num};"
        await self._connection.send_query(f"{line_command}\r")
        query = f"?{attr.io_ref.name}"
        response = await self._connection.send_query(f"{query}\r")
        if f"{attr.io_ref.response_prefix}" in response:
            # value = response.strip(f"{attr.io_ref.response_prefix}" +"\n\rOK\n\r")
            value_without_prefix = response.replace(
                f"{attr.io_ref.response_prefix}", ""
            )
            value = value_without_prefix.replace("\n\r>OK\n\r", "")
            value = value.replace("\n\rOK\n\r", "")

        await attr.update(attr.dtype(value))
