from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import (  # type: ignore
    AttributeIO,  # type: ignore
    AttributeIORef,  # type: ignore
    AttrR,
    AttrRW,
    AttrW,
)
from fastcs.util import ONCE  # type: ignore

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
class WpiMicro4ControllerCommandSettingIORef(AttributeIORef):  # type: ignore
    name: str
    response_prefix: str
    line_num: int
    pump_atrr_instance: AttrRW  # type: ignore
    _: KW_ONLY
    update_period: float | None = ONCE  # type: ignore


# for the settings which only requires command only
class WpiMicro4ControllerCommandSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerCommandSettingIORef]  # type: ignore
):
    def __init__(self, connection: USBConnection):
        super().__init__()  # type: ignore

        self._connection = connection

    async def send(
        self,
        attr: AttrW[NumberT, WpiMicro4ControllerCommandSettingIORef],  # type: ignore
        value: NumberT,
    ) -> None:
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()  # type: ignore
        if chosen_pump_number == attr.io_ref.line_num:  # type: ignore
            command_long = f"{attr.dtype(value)}"
            command = WpiMicro4ControllerCommandSettingNameDict.name_to_symbol[
                command_long
            ]
            try:
                r = await self._connection.send_query(f"{command}\r")
                if "OK" in r:
                    await self.update(attr)  # type: ignore
            except Exception as e:
                print(f"error: new line query - {e}")

    # run once at init stage
    async def update(
        self,
        attr: AttrR[NumberT, WpiMicro4ControllerCommandSettingIORef],  # type: ignore
    ) -> None:
        # instead of this check the ine atribute value is same as the line number
        # if not don't update
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()  # type: ignore
        if chosen_pump_number == attr.io_ref.line_num:  # type: ignore
            query = f"?{attr.io_ref.name}"  # type: ignore
            response = await self._connection.send_query(f"{query}\r")
            if f"{attr.io_ref.response_prefix}" in response:  # type: ignore
                value_without_prefix = response.replace(
                    f"{attr.io_ref.response_prefix}",  # type: ignore
                    "",  # type: ignore
                )
                value = value_without_prefix.replace("\n\r>OK\n\r", "")
                value = value.replace("\n\rOK\n\r", "")

            await attr.update(attr.dtype(value))  # type: ignore
