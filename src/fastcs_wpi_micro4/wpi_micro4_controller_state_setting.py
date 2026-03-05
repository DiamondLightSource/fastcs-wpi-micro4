from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrW

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
class WpiMicro4ControllerStateSettingIORef(AttributeIORef):
    name: str
    response_prefix: str
    line_num: int
    _: KW_ONLY
    update_period: float | None = 0.5


# state is same a scommand by it is scanned periodically
class WpiMicro4ControllerStateSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerStateSettingIORef]
):
    def __init__(self, connection: USBConnection):
        super().__init__()

        self._connection = connection

    async def send(
        self,
        attr: AttrW[NumberT, WpiMicro4ControllerStateSettingIORef],
        value: NumberT,
    ) -> None:
        line_command = f"L{attr.io_ref.line_num}"
        command_long = f"{attr.dtype(value)}"
        command = WpiMicro4ControllerStateSettingNameDict.name_to_symbol[command_long]
        try:
            await self._connection.send_query(f"{line_command}\r")
            r = await self._connection.send_query(f"{command}\r")
            if "OK" in r:
                await self.update(attr)
        except Exception as e:
            print(f"error: new line query - {e}")

    # run periodically
    async def update(
        self, attr: AttrR[NumberT, WpiMicro4ControllerStateSettingIORef]
    ) -> None:
        line_command = f"L{attr.io_ref.line_num};"
        await self._connection.send_query(f"{line_command}\r")
        query = f"?{attr.io_ref.name}"
        response = await self._connection.send_query(f"{query}\r")
        if f"{attr.io_ref.response_prefix}" in response:
            value_without_prefix = response.replace(
                f"{attr.io_ref.response_prefix}", ""
            )
            value = value_without_prefix.replace("\n\r>OK\n\r", "")
            value = value.replace("\n\rOK\n\r", "")

        await attr.update(attr.dtype(value))
