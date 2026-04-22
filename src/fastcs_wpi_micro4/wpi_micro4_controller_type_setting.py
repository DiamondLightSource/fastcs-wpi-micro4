from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import (
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
class WpiMicro4ControllerTypeSettingNameDict:
    # maps names inserted by the user in the GUI to acuall Commands
    name_to_symbol = {
        "Type A": "11",
        "Type B": "12",
        "Type C": "13",
        "Type 1": "1",
        "Type 2": "2",
        "Type 3": "3",
        "Type 4": "4",
        "Type 5": "5",
        "Type 6": "6",
        "Type 7": "7",
        "Type 8": "8",
        "Type 9": "9",
        # "Type 10": "10" # could ignore this type
        # special syrynge not used at Diamond
    }


@dataclass
class WpiMicro4ControllerTypeSettingIORef(AttributeIORef):  # type: ignore
    # command: str - T
    # query: str - S
    response_prefix: str
    line_num: int
    volume_att: AttrR  # type: ignore # syringe volume
    length_att: AttrR  # type: ignore # syringe lenght
    pump_atrr_instance: AttrRW  # type: ignore
    _: KW_ONLY
    update_period: float | None = ONCE  # type: ignore


# for the settings which require both the command and value
# query is the same a the comm
class WpiMicro4ControllerTypeSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerTypeSettingIORef]  # type: ignore
):
    def __init__(self, connection: USBConnection):
        super().__init__()  # type: ignore

        self._connection = connection

    async def send(
        self,
        attr: AttrW[NumberT, WpiMicro4ControllerTypeSettingIORef],  # type: ignore
        value: NumberT,  # type: ignore
    ) -> None:
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()  # type: ignore
        if chosen_pump_number == attr.io_ref.line_num:  # type: ignore
            value_long = f"{attr.dtype(value)}"
            value = WpiMicro4ControllerTypeSettingNameDict.name_to_symbol[value_long]  # type: ignore
            command = f"T{value}"
            try:
                r = await self._connection.send_query(f"{command}\r")
                if "OK" in r:
                    await self.update(attr)  # type: ignore
            except Exception as e:
                print(f"error: LINE query - {e}")

    # run once at init stage
    async def update(
        self,
        attr: AttrR[NumberT, WpiMicro4ControllerTypeSettingIORef],  # type: ignore
    ) -> None:
        chosen_pump_number = attr.io_ref.pump_atrr_instance.get()  # type: ignore
        if chosen_pump_number == attr.io_ref.line_num:  # type: ignore
            query = "?S"
            response = await self._connection.send_query(f"{query}\r")
            await self.set(response, attr)  # type: ignore

    async def set(
        self,
        response,  # type: ignore
        attr: AttrR[NumberT, WpiMicro4ControllerTypeSettingIORef],  # type: ignore
    ):
        if f"{attr.io_ref.response_prefix}" in response:  # type: ignore
            value = response.strip(f"{attr.io_ref.response_prefix}" + " \n\rOK\n\r")  # type: ignore
            value = value.replace("\n\r>OK\n\r", "")  # type: ignore
            type_volume_length = value.split(", ")  # type: ignore
            type = type_volume_length[0]  # type: ignore
            await attr.io_ref.volume_att.update(  # type: ignore
                attr.io_ref.volume_att.dtype(type_volume_length[1])  # type: ignore
            )
            await attr.io_ref.length_att.update(  # type: ignore
                attr.io_ref.length_att.dtype(type_volume_length[2])  # type: ignore
            )
            await attr.update(attr.dtype(type))  # type: ignore
        else:
            raise Exception("Response doesn't match query")
