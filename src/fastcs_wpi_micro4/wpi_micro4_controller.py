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


# class TerminateTaskGroup(Exception):
#    """Exception raised to terminate a task group."""


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

        await self._connection.send_command(f"{command}\r\n")


@dataclass
class WpiMicro4ControllerLineSettingIORef(AttributeIORef):
    name: str
    line_num: int
    _: KW_ONLY
    update_period: float | None = None


class WpiMicro4ControllerLineSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerLineSettingIORef]
):
    def __init__(self, connection: IPConnection):
        super().__init__()

        self._connection = connection

    # async def force_terminate_task_group(self):
    # """Used to force termination of a task group."""
    # raise TerminateTaskGroup()

    async def send(
        self, attr: AttrW[NumberT, WpiMicro4ControllerLineSettingIORef], value: NumberT
    ) -> None:
        # line_command = f"L{str(attr.io_ref.line_num)};"
        command = f"{attr.io_ref.name}{attr.dtype(value)};"
        # await asyncio.gather(
        # await self._connection.send_command(f"{line_command}\r\n"),
        # await self.update(attr),
        # await self._connection.send_query("?L;\r\n"),
        await self._connection.send_command(f"{command}\r\n")
        # resp =await self._connection.send_query("?V;\r\n"),
        # )

    # async def update(
    # self, attr: AttrW[NumberT, WpiMicro4ControllerLineSettingIORef]):
    # respose = await self._connection.send_query("?L;\r\n")
    # respose = await self._connection.send_query("?V;\r\n")
    # if "?V;" in response and ";" not in response:
    # value = response.strip("?V" + " \r\n")
    # await attr.update(attr.dtype(value))
    # try:
    #    async with asyncio.TaskGroup() as tg:
    #        tg.create_task(self._connection.send_command(f"{line_command}\r\n"))
    #        res = tg.create_task(self._connection.send_query(f"?L;\r\n"))
    #        tg.create_task(self._connection.send_command(f"{command}\r\n"))
    #        res = tg.create_task(self._connection.send_query(f"?V;\r\n"))
    # asyncio.sleep(1)
    # tg.create_task(force_terminate_task_group())
    # except* TerminateTaskGroup:
    #    pass


class WpiMicro4Controller(Controller):
    line_number_attr = AttrW(Int(), io_ref=WpiMicro4ControllerSettingIORef("L"))
    line_number_rbv = AttrR(Int())

    def __init__(self, settings: IPConnectionSettings):
        self._ip_settings = settings
        self.connection = IPConnection()

        super().__init__(
            ios=[
                WpiMicro4ControllerSettingIO(self.connection),
                WpiMicro4ControllerLineSettingIO(self.connection),
            ]
        )

        self.name_query_list = self.creat_query_atributes()
        self.creat_setting_attributes()

    async def connect(self):
        await self.connection.connect(self._ip_settings)

    def creat_query_atributes(self) -> list[dict[str, str]]:
        name_query_list = []  # contains 4 dicts, one for each line
        # floats
        float_atrr_base_names = [
            "volume_l",
            # "volume_counter_l",
            # "delivery_rate_l",
            # "volume_max_rate_l",
            # "step_rate_l",
            # "number_of_steps_l",
        ]
        float_quaries = ["?V"]  # , "?C", "?R", "?X", "?P", "?T"]
        # bools
        bool_atrr_base_names = [
            "beeper_l"
        ]  # , "press_once_to_run_l", "microstepping_on_l"]
        bool_quaries = ["?1"]  # , "?3", "?6"]
        # strings
        string_atrr_base_names = [
            "mode_l",
            # "pump_direction_l",
            # "pump_units_l",
            # "pump_running_l",
            # "syringe_type_l",
        ]
        string_quaries = ["?M"]  # , "?D", "?U", "?G", "?S"]

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

    def creat_setting_attributes(self):
        float_atrr_base_names = [
            "volume_l",
            # "volume_counter_l",
            # "delivery_rate_l"
        ]
        float_commands = ["V"]  # , "?C", "?R"]
        bool_atrr_base_names = [
            "infuse_mode_l",
            # "withdraw_mode_l",
            # "go_l",
            # "halt_l",
            # "rate_per_sec_l",
            # "rate_per_min_l",
            # "not_grupped_l", #?
            # "grupped_l", #?
            # "disabled_l"
        ]
        bool_commands = ["I"]  # , "W", "G", "H", "S", "M", "N", "P", "D" ]
        for line in range(4):  # 4
            for j in range(len(float_atrr_base_names)):
                base_name = float_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}"
                setattr(
                    self,
                    attr_name,
                    AttrW(
                        Float(),
                        io_ref=WpiMicro4ControllerLineSettingIORef(
                            float_commands[j], line + 1
                        ),
                    ),
                )
            for j in range(len(bool_atrr_base_names)):
                base_name = bool_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}"
                setattr(
                    self,
                    attr_name,
                    AttrW(
                        Bool(),
                        io_ref=WpiMicro4ControllerLineSettingIORef(
                            bool_commands[j], line + 1
                        ),
                    ),
                )

    async def set_line_number(self, number: int):
        await self.line_number_attr.put(
            self.line_number_attr.dtype(number), sync_setpoint=True
        )
        await asyncio.sleep(0.1)

    async def update_line_num(self):
        query = "?L;"
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

    # TEST using a command to set a fixed volume value

    async def set_value_number_l1(self, number: int):
        await self.volume_l1.put(self.volume_l1.dtype(number), sync_setpoint=True)
        await asyncio.sleep(0.1)

    async def update_value_num_l1(self):
        query = "?V;"
        response = await self.connection.send_query(f"{query}\r\n")
        if "V" in response:
            value = response.strip(query + "; \r\n")
            await self.volume_l1_rbv.update(value)

    @command()
    async def set_value_number_l1_1(self):
        await asyncio.gather(
            self.set_line_number(1),
            self.update_line_num(),
            self.set_value_number_l1(1),
            self.update_value_num_l1(),
        )

    @command()
    async def set_value_number_l1_2(self):
        await asyncio.gather(
            self.set_line_number(1),
            self.update_line_num(),
            self.set_value_number_l1(2),
            self.update_value_num_l1(),
        )
