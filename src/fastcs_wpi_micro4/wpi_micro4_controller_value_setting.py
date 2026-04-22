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
class WpiMicro4ControllerValueSettingIORef(AttributeIORef):  # type: ignore
    command: str
    query: str
    response_prefix: str
    line_num: int
    pump_atrr_instance: AttrRW  # type: ignore
    _: KW_ONLY
    update_period: float | None = ONCE  # type: ignore


# for the settings which require both the command and value
# query is the same a the comm
class WpiMicro4ControllerValueSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerValueSettingIORef]  # type: ignore
):
    def __init__(self, connection: USBConnection):
        super().__init__()  # type: ignore

        self._connection = connection

    async def send(
        self,
        attr: AttrW[NumberT, WpiMicro4ControllerValueSettingIORef],  # type: ignore
        value: NumberT,  # type: ignore
    ) -> None:
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()  # type: ignore
        if chosen_pump_number == attr.io_ref.line_num:  # type: ignore
            command = f"{attr.io_ref.command}{attr.dtype(value)}"  # type: ignore
            try:
                r = await self._connection.send_query(f"{command}\r")
                if "OK" in r:
                    await self.update(attr)  # type: ignore
                # This could work for R and V
                # But R is now returning wrong responce
                # await self.set(r, attr)
            except Exception as e:
                print(f"error: LINE query - {e}")

    # run once at init stage
    async def update(
        self,
        attr: AttrR[NumberT, WpiMicro4ControllerValueSettingIORef],  # type: ignore
    ) -> None:
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()  # type: ignore
        if chosen_pump_number == attr.io_ref.line_num:  # type: ignore
            query = f"?{attr.io_ref.query}"  # type: ignore
            response = await self._connection.send_query(f"{query}\r")
            await self.set(response, attr)  # type: ignore

    async def set(
        self,
        response,  # type: ignore
        attr: AttrR[NumberT, WpiMicro4ControllerValueSettingIORef],  # type: ignore
    ):
        if f"{attr.io_ref.response_prefix}" in response:  # type: ignore
            value = response.strip(f">{attr.io_ref.response_prefix}" + " \n\rOK\n\r")  # type: ignore
            value = value.replace("\n\r>OK\n\r", "")  # type: ignore
            if "L" in value:
                value = value[:-2]  # type: ignore # remove the units as well
            await attr.update(attr.dtype(value))  # type: ignore
        else:
            raise Exception("Response doesn't match query")
