import asyncio
from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attribute_io import AttributeIO
from fastcs.attribute_io_ref import AttributeIORef
from fastcs.attributes import AttrR, AttrW
from fastcs.connections import (
    IPConnection,
    IPConnectionSettings,
)
from fastcs.controller import Controller
from fastcs.datatypes import Bool, Float, Int, String
from fastcs.wrappers import command, scan

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerSettingIORef(AttributeIORef):
    name: str
    _: KW_ONLY
    update_period: float | None = None


class WpiMicro4ControllerSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerSettingIORef]
):
    def __init__(self, connection: IPConnection):
        super().__init__()

        self._connection = connection

    async def send(
        self, attr: AttrW[NumberT, WpiMicro4ControllerSettingIORef], value: NumberT
    ) -> None:
        command = f"{attr.io_ref.name}{attr.dtype(value)};"
        await self._connection.send_command(f"{command}")

    # volume_counter = AttrW(Float(), io_ref=WpiMicro4ControllerAttributeIORef("C"))
    # volume = AttrW(Float(), io_ref=WpiMicro4ControllerAttributeIORef("V"))
    # delivery_rate = AttrW(Float(), io_ref=WpiMicro4ControllerAttributeIORef("R"))
    # infuse_mode = AttrW(Bool(), io_ref=WpiMicro4ControllerAttributeIORef("I")) #on/off
    # withdraw_mode =
    # AttrW(Bool(), io_ref=WpiMicro4ControllerAttributeIORef("W")) #on/off
    # go = AttrW(Bool(), io_ref=WpiMicro4ControllerAttributeIORef("G")) on/off
    # halt = AttrW(Bool(), io_ref=WpiMicro4ControllerAttributeIORef("H")) #on/off
    # rate_per_sec = AttrW(Bool(), io_ref=WpiMicro4ControllerAttributeIORef("S")) on/off
    # rate_per_min = AttrW(Bool(), io_ref=WpiMicro4ControllerAttributeIORef("M")) on/off
    # not_grupped = AttrW(Bool(), io_ref=WpiMicro4ControllerAttributeIORef("N")) on/off
    # grupped = AttrW(Bool(), io_ref=WpiMicro4ControllerAttributeIORef("P")) on/off
    # disabled = AttrW(Bool(), io_ref=WpiMicro4ControllerAttributeIORef("D")) on/off


class WpiMicro4Controller(Controller):
    line_number_attr = AttrW(Int(), io_ref=WpiMicro4ControllerSettingIORef("L"))
    line_number_rbv = AttrR(Int())

    def __init__(self, settings: IPConnectionSettings):
        self._ip_settings = settings
        self.connection = IPConnection()

        super().__init__(
            ios=[
                WpiMicro4ControllerSettingIO(self.connection),
            ]
        )

        self.name_query_list = self.creat_query_atributes()

    async def connect(self):
        await self.connection.connect(self._ip_settings)

    def creat_query_atributes(self) -> list[dict[str, str]]:
        name_query_list = []  # contains 4 dicts, one for each line
        # floats
        float_atrr_base_names = [
            "volume_l",
            "volume_counter_l",
            "delivery_rate_l",
            "volume_max_rate_l",
            "step_rate_l",
            "number_of_steps_l",
        ]
        float_quaries = ["?V", "?C", "?R", "?X", "?P", "?T"]
        # bools
        bool_atrr_base_names = ["beeper_l", "press_once_to_run_l", "microstepping_on_l"]
        bool_quaries = ["?1", "?3", "?6"]
        # strings
        string_atrr_base_names = [
            "mode_l",
            "pump_direction_l",
            "pump_units_l",
            "pump_running_l",
            "syringe_type_l",
        ]
        string_quaries = ["?M", "?D", "?U", "?G", "?S"]

        for line in range(4):
            name_query = {}
            for j in range(len(float_atrr_base_names)):
                base_name = float_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}_rbv"
                setattr(self, attr_name, AttrR(Float()))
                name_query[attr_name] = float_quaries[j]
            for j in range(len(bool_atrr_base_names)):
                base_name = bool_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}_rbv"
                setattr(self, attr_name, AttrR(Bool()))
                name_query[attr_name] = bool_quaries[j]
            for j in range(len(string_atrr_base_names)):
                base_name = string_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}_rbv"
                setattr(self, attr_name, AttrR(String()))
                name_query[attr_name] = string_quaries[j]
            name_query_list.append(name_query)

        return name_query_list

    @command()
    async def set_linen_nr1(self):
        await self.line_number_attr.put(
            self.line_number_attr.dtype(1), sync_setpoint=True
        )
        await asyncio.sleep(0.1)

    @command()
    async def set_linen_nr2(self):
        await self.line_number_attr.put(
            self.line_number_attr.dtype(2), sync_setpoint=True
        )
        await asyncio.sleep(0.1)

    @command()
    async def set_linen_nr3(self):
        await self.line_number_attr.put(
            self.line_number_attr.dtype(3), sync_setpoint=True
        )
        await asyncio.sleep(0.1)

    @command()
    async def set_linen_nr4(self):
        await self.line_number_attr.put(
            self.line_number_attr.dtype(4), sync_setpoint=True
        )
        await asyncio.sleep(0.1)

    async def set_line_number(self, number: int):
        await self.line_number_attr.put(
            self.line_number_attr.dtype(number), sync_setpoint=True
        )
        await asyncio.sleep(0.1)

    async def update_line_num(self):
        query = "?L"
        response = await self.connection.send_query(f"{query}\r\n")
        if query in response:
            value = response.strip(query + "; \r\n")
            await self.line_number_rbv.update(value)

    async def update_value(self, atribute: AttrR[NumberT], query: str):
        response = await self.connection.send_query(f"{query}\r\n")
        if query in response and ";" not in response:
            value = response.strip(query + " \r\n")
            await atribute.update(value)

    async def update_line_atrr(self, line: int):
        name_query_dict = self.name_query_list[line]
        for name, query in name_query_dict.items():
            await self.update_value(getattr(self, name), query)

    @scan(0.1)
    async def update_lines(self):
        for line in range(4):
            await asyncio.gather(
                self.set_line_number(line + 1),
                self.update_line_num(),
                self.update_line_atrr(line),
            )
