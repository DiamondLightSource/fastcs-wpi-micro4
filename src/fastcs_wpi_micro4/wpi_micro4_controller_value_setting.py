from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrRW, AttrW
from fastcs.util import ONCE

from fastcs_wpi_micro4.usb_connection import USBConnection

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerValueSettingIORef(AttributeIORef):
    command: str
    query: str
    response_prefix: str
    line_num: int
    pump_atrr_instance: AttrRW
    _: KW_ONLY
    update_period: float | None = ONCE


# for the settings which require both the command and value
# query is the same a the comm
class WpiMicro4ControllerValueSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerValueSettingIORef]
):
    def __init__(self, connection: USBConnection):
        super().__init__()

        self._connection = connection

    async def send(
        self, attr: AttrW[NumberT, WpiMicro4ControllerValueSettingIORef], value: NumberT
    ) -> None:
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()
        if chosen_pump_number == attr.io_ref.line_num:
            command = f"{attr.io_ref.command}{attr.dtype(value)}"
            try:
                r = await self._connection.send_query(f"{command}\r")
                if "OK" in r:
                    await self.update(attr)
                # This could work for R and V
                # But R is now returning wrong responce
                # await self.set(r, attr)
            except Exception as e:
                print(f"error: LINE query - {e}")

    # run once at init stage
    async def update(
        self, attr: AttrR[NumberT, WpiMicro4ControllerValueSettingIORef]
    ) -> None:
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()
        if chosen_pump_number == attr.io_ref.line_num:
            query = f"?{attr.io_ref.query}"
            response = await self._connection.send_query(f"{query}\r")
            await self.set(response, attr)

    async def set(
        self, response, attr: AttrR[NumberT, WpiMicro4ControllerValueSettingIORef]
    ):
        if f"{attr.io_ref.response_prefix}" in response:
            value = response.strip(f">{attr.io_ref.response_prefix}" + " \n\rOK\n\r")
            value = value.replace("\n\r>OK\n\r", "")
            if "L" in value:
                value = value[:-2]  # remove the units as well
            await attr.update(attr.dtype(value))
        else:
            raise Exception("Response doesn't match query")
