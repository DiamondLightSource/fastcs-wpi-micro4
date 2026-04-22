from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import (
    AttributeIO,  # type: ignore
    AttributeIORef,  # type: ignore
    AttrR,
    AttrRW,
    AttrW,
)

from fastcs_wpi_micro4.usb_connection import USBConnection

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerStateSettingNameDict:
    name_to_symbol = {
        "Run": "G",
        "Stop": "H",
        "Pause": "U",
    }


@dataclass
class WpiMicro4ControllerStateSettingIORef(AttributeIORef):  # type: ignore
    name: str
    response_prefix: str
    line_num: int
    pump_atrr_instance: AttrRW  # type: ignore
    _: KW_ONLY
    update_period: float | None = 0.5


# state is same a scommand by it is scanned periodically
class WpiMicro4ControllerStateSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerStateSettingIORef]  # type: ignore
):
    def __init__(self, connection: USBConnection):
        super().__init__()  # type: ignore

        self._connection = connection

    async def send(
        self,
        attr: AttrW[NumberT, WpiMicro4ControllerStateSettingIORef],  # type: ignore
        value: NumberT,
    ) -> None:
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()  # type: ignore
        if chosen_pump_number == attr.io_ref.line_num:  # type: ignore
            command_long = f"{attr.dtype(value)}"
            if (
                command_long
                in WpiMicro4ControllerStateSettingNameDict.name_to_symbol.keys()
            ):
                command = WpiMicro4ControllerStateSettingNameDict.name_to_symbol[
                    command_long
                ]
                try:
                    r = await self._connection.send_query(f"{command}\r")
                    if "OK" in r:
                        await self.update(attr)  # type: ignore
                except Exception as e:
                    print(f"error: new line query - {e}")

    # run periodically
    async def update(
        self,
        attr: AttrR[NumberT, WpiMicro4ControllerStateSettingIORef],  # type: ignore
    ) -> None:
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()  # type: ignore
        if chosen_pump_number == attr.io_ref.line_num:  # type: ignore
            query = f"?{attr.io_ref.name}"  # type: ignore
            response = await self._connection.send_query(f"{query}\r")
            if f"{attr.io_ref.response_prefix}" in response:  # type: ignore
                value_without_prefix = response.replace(
                    f"{attr.io_ref.response_prefix}",  # type: ignore
                    "",
                )
                value = value_without_prefix.replace("\n\r>OK\n\r", "")
                value = value.replace("\n\rOK\n\r", "")

            await attr.update(attr.dtype(value))  # type: ignore
