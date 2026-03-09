from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrRW

from fastcs_wpi_micro4.usb_connection import USBConnection

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerQueryIORef(AttributeIORef):
    name: str
    response_prefix: str
    line_num: int
    pump_atrr_instance: AttrRW
    _: KW_ONLY
    update_period: float | None = 0.5
    # needs state atribute to keep updating it too


class WpiMicro4ControllerQueryIO(AttributeIO[NumberT, WpiMicro4ControllerQueryIORef]):
    def __init__(self, connection: USBConnection):
        super().__init__()

        self._connection = connection

    async def update(self, attr: AttrR[NumberT, WpiMicro4ControllerQueryIORef]) -> None:
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()
        if chosen_pump_number == attr.io_ref.line_num:
            query = f"?{attr.io_ref.name}"

            response = await self._connection.send_query(f"{query}\r")
            if f"{attr.io_ref.response_prefix}" in response:
                value = response.strip(f"{attr.io_ref.response_prefix}" + " \n\rOK\n\r")
                value = value.replace("\n\r>OK\n\r", "")
                if "L" in value:
                    value = value[:-2]  # remove the units as well

                await attr.update(attr.dtype(value))
            else:
                raise Exception("Response doesn't much query")
