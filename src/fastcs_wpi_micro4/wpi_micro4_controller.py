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
from fastcs.datatypes import Bool, Float, String
from fastcs.wrappers import scan

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerCommandSettingIORef(AttributeIORef):
    line_num: int
    _: KW_ONLY
    update_period: float | None = None


# for the settings which only requires sending a command
class WpiMicro4ControllerCommandSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerCommandSettingIORef]
):
    def __init__(self, connection: IPConnection):
        super().__init__()

        self._connection = connection

    async def send(
        self,
        attr: AttrW[NumberT, WpiMicro4ControllerCommandSettingIORef],
        value: NumberT,
    ) -> None:
        line_command = f"L{attr.io_ref.line_num};"
        command = f"{attr.dtype(value)};"
        await self._connection.send_query(f"{line_command}\n")
        await self._connection.send_query(f"{command}\n")


@dataclass
class WpiMicro4ControllerValueSettingIORef(AttributeIORef):
    name: str
    line_num: int
    rbv: float
    _: KW_ONLY
    update_period: float | None = None


# for the settings which require both the command and value
class WpiMicro4ControllerValueSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerValueSettingIORef]
):
    def __init__(self, connection: IPConnection):
        super().__init__()

        self._connection = connection

    async def task(self, ch):
        try:
            await self._connection.send_command(f"{ch}")
        except Exception as e:
            print(f"error: CHAR command - {e}")
            await self._connection.connect(IPConnectionSettings("192.168.1.6", 7004))
            # time.wait(3)

    async def send(
        self, attr: AttrW[NumberT, WpiMicro4ControllerValueSettingIORef], value: NumberT
    ) -> None:
        line_command = f"L{attr.io_ref.line_num};"
        command = f"{attr.io_ref.name}{attr.dtype(value)};"
        try:
            await self._connection.send_query(f"{line_command}\n")
        except Exception as e:
            print(f"error: LINE query - {e}")
            await self._connection.connect(IPConnectionSettings("192.168.1.6", 7004))
            # time.wait(3)

        list_of_chars = list(command)
        if len(list_of_chars) > 7:  # command letter + 4 numerals +'.' + ';'
            print("Too many chars. The limit is 4.")
        else:
            for ch in list_of_chars:
                await self.task(ch)
            try:
                r2 = await self._connection.send_query("\n")
                if len(r2) > 5:  #!!! not nice
                    val = r2[-7:]
                    print(r2, " val only:", val)
                    attr.io_ref.rbv = val
            except Exception as e:
                print(f"error: new line query - {e}")
                await self._connection.connect(
                    IPConnectionSettings("192.168.1.6", 7004)
                )
                # time.wait(3)


class WpiMicro4Controller(Controller):
    def __init__(self, settings: IPConnectionSettings):
        self._ip_settings = settings
        self.connection = IPConnection()

        super().__init__(
            ios=[
                WpiMicro4ControllerValueSettingIO(self.connection),
                WpiMicro4ControllerCommandSettingIO(self.connection),
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
            "volume_counter_l",
            "delivery_rate_l",
            "volume_max_rate_l",
            "step_rate_l",
            "number_of_steps_l",
        ]
        float_quaries = ["?V", "?C", "?R", "?X", "?P", "?T"]
        # bools
        bool_atrr_base_names = [
            "beeper_l",
            "microstepping_on_l",
        ]
        bool_quaries = ["?1", "?6"]  # T/F
        # strings
        string_atrr_base_names = [
            "mode_l",  # G/N/D
            "pump_direction_l",  # I/W
            "rate_units_l",  # S/M
            "pump_state_l",  # R/S
            "type_l",  # A..F
            "hold_toggle_l",  # H/T
        ]
        string_quaries = ["?M", "?D", "?U", "?G", "?S", "?3"]

        for line in range(4):
            name_query = {}
            for j in range(len(float_atrr_base_names)):
                base_name = float_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}_rbv"
                setattr(
                    self,
                    attr_name,
                    AttrR(Float(prec=3)),
                )
                name_query[attr_name] = float_quaries[j]
            for j in range(len(bool_atrr_base_names)):
                base_name = bool_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}_rbv"
                setattr(
                    self,
                    attr_name,
                    AttrR(Bool()),
                )
                name_query[attr_name] = bool_quaries[j]
            for j in range(len(string_atrr_base_names)):
                base_name = string_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}_rbv"
                setattr(
                    self,
                    attr_name,
                    AttrR(String()),
                )
                name_query[attr_name] = string_quaries[j]
            name_query_list.append(name_query)

        return name_query_list

    def creat_setting_attributes(self):
        float_atrr_base_names = ["volume_l", "volume_counter_l", "delivery_rate_l"]
        float_commands = ["V", "C", "R"]
        string_atrr_base_names = [
            "mode_l",  # P/N/D
            "pump_direction_l",  # I/W
            "rate_units_l",  # S/M
            "pump_state_l",  # G/H
            "beeper_l",  # 1 (on)/2(off)
            "microstepping_on_l",  # 6(on)/7(off)
            "hold_toggle_l",  # 3(hold)/4(toggle)
        ]
        for line in range(4):
            for j in range(len(float_atrr_base_names)):
                base_name = float_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}"
                setattr(
                    self,
                    attr_name,
                    AttrW(
                        Float(prec=3),
                        io_ref=WpiMicro4ControllerValueSettingIORef(
                            float_commands[j], line + 1, 10.0
                        ),
                    ),
                )
            for j in range(len(string_atrr_base_names)):
                base_name = string_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}"
                setattr(
                    self,
                    attr_name,
                    AttrW(
                        String(),
                        io_ref=WpiMicro4ControllerCommandSettingIORef(line + 1),
                    ),
                )
            # special case
            # base_name = "type_l"
            # attr_name = f"{base_name}{line + 1}"
            # setattr(
            #    self,
            #    attr_name,
            #    AttrW(
            #        String(),
            #        io_ref=WpiMicro4ControllerValueSettingIORef("T", line + 1, 0.0),
            #           # needs diffrent  IORef
            #    ),
            # )

    @scan(10)
    async def update_query_attributes(self):
        for a_name in self.attributes:
            if "rbv" not in a_name:
                a = getattr(self, a_name)
                a_rbv = getattr(self, a.name + "_rbv")
                await a_rbv.update(a.io_ref.rbv)
                # print(self.volume_l1_rbv.get())
