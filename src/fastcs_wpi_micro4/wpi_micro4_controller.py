from fastcs.attributes import AttrR, AttrRW
from fastcs.connections import (
    IPConnection,
    IPConnectionSettings,
)
from fastcs.controller import Controller
from fastcs.datatypes import Float, String

from fastcs_wpi_micro4.wpi_micro4_controller_command_setting import (
    WpiMicro4ControllerCommandSettingIO,
    WpiMicro4ControllerCommandSettingIORef,
)
from fastcs_wpi_micro4.wpi_micro4_controller_query import (
    WpiMicro4ControllerQueryIO,
    WpiMicro4ControllerQueryIORef,
)
from fastcs_wpi_micro4.wpi_micro4_controller_value_setting import (
    WpiMicro4ControllerValueSettingIO,
    WpiMicro4ControllerValueSettingIORef,
)


class WpiMicro4Controller(Controller):
    def __init__(self, settings: IPConnectionSettings):
        self._ip_settings = settings
        self.connection = IPConnection()

        super().__init__(
            ios=[
                WpiMicro4ControllerValueSettingIO(self.connection),
                WpiMicro4ControllerCommandSettingIO(self.connection),
                WpiMicro4ControllerQueryIO(self.connection),
            ]
        )

        self.creat_setting_attributes()

    async def connect(self):
        await self.connection.connect(self._ip_settings)

    def creat_setting_attributes(self):
        float_atrr_names_commands = ["volume_l", "volume_counter_l", "delivery_rate_l"]
        float_commands = ["V", "C", "R"]  # queries same as commands
        float_queries = ["V", "C", "R"]
        string_atrr_base_names = [  # pv values are commands
            "mode_l",  # P/N/D
            "pump_direction_l",  # I/W
            "rate_units_l",  # S/M
            "pump_state_l",  # G/H
            "beeper_l",  # 1 (on)/2(off)
            "hold_toggle_l",  # 3(hold)/4(toggle)
            "microstepping_on_l",  # 6(on)/7(off)
        ]
        string_queries = ["M", "D", "U", "G", "1", "3", "6"]
        float_atrr_names_queries = [
            "maximum_rate_l",
            "step_rate_l",
            "number_of_steps_l",
        ]
        float_queries_only = ["X", "T", "P"]
        for line in range(4):
            for j in range(len(float_atrr_names_commands)):
                base_name = float_atrr_names_commands[j]
                attr_name = f"{base_name}{line + 1}"
                setattr(
                    self,
                    attr_name,
                    AttrRW(
                        Float(prec=3),
                        io_ref=WpiMicro4ControllerValueSettingIORef(
                            float_commands[j], float_queries[j], line + 1
                        ),
                    ),
                )
            for j in range(len(string_atrr_base_names)):
                base_name = string_atrr_base_names[j]
                attr_name = f"{base_name}{line + 1}"
                setattr(
                    self,
                    attr_name,
                    AttrRW(
                        String(),
                        io_ref=WpiMicro4ControllerCommandSettingIORef(
                            string_queries[j], line + 1
                        ),
                    ),
                )
            for j in range(len(float_atrr_names_queries)):
                base_name = float_atrr_names_queries[j]
                attr_name = f"{base_name}{line + 1}"
                setattr(
                    self,
                    attr_name,
                    AttrR(
                        Float(),
                        io_ref=WpiMicro4ControllerQueryIORef(
                            float_queries_only[j], line + 1
                        ),
                    ),
                )
            # special case
            base_name = "type_l"
            attr_name = f"{base_name}{line + 1}"
            setattr(
                self,
                attr_name,
                AttrRW(
                    String(),
                    io_ref=WpiMicro4ControllerValueSettingIORef("T", "S", line + 1),
                ),
            )
