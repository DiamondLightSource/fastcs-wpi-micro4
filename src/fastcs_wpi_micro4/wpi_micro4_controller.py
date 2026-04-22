from fastcs.attributes import AttrR, AttrRW
from fastcs.controllers import Controller
from fastcs.datatypes import Float, Int, String

from fastcs_wpi_micro4.usb_connection import USBConnection, USBConnectionSettings
from fastcs_wpi_micro4.wpi_micro4_controller_command_setting import (
    WpiMicro4ControllerCommandSettingIO,
    WpiMicro4ControllerCommandSettingIORef,
)
from fastcs_wpi_micro4.wpi_micro4_controller_line_setting import (
    WpiMicro4ControllerLineSettingIO,
    WpiMicro4ControllerLineSettingIORef,
)
from fastcs_wpi_micro4.wpi_micro4_controller_query import (
    WpiMicro4ControllerQueryIO,
    WpiMicro4ControllerQueryIORef,
)
from fastcs_wpi_micro4.wpi_micro4_controller_state_setting import (
    WpiMicro4ControllerStateSettingIO,
    WpiMicro4ControllerStateSettingIORef,
)
from fastcs_wpi_micro4.wpi_micro4_controller_type_setting import (
    WpiMicro4ControllerTypeSettingIO,
    WpiMicro4ControllerTypeSettingIORef,
)
from fastcs_wpi_micro4.wpi_micro4_controller_value_setting import (
    WpiMicro4ControllerValueSettingIO,
    WpiMicro4ControllerValueSettingIORef,
)


class WpiMicro4Controller(Controller):
    def __init__(self, settings: USBConnectionSettings):
        self._usb_settings = settings
        self.connection = USBConnection()

        super().__init__(  # type: ignore
            ios=[
                WpiMicro4ControllerValueSettingIO(self.connection),
                WpiMicro4ControllerTypeSettingIO(self.connection),
                WpiMicro4ControllerLineSettingIO(self.connection),
                WpiMicro4ControllerQueryIO(self.connection),
                WpiMicro4ControllerStateSettingIO(self.connection),
                WpiMicro4ControllerCommandSettingIO(self.connection),
            ]
        )

        self.creat_setting_attributes()

    async def connect(self):
        await self.connection.connect(self._usb_settings)

    def creat_setting_attributes(self):
        float_atrr_names_commands = ["volume_l", "delivery_rate_l"]
        float_commands = ["V", "R"]
        float_queries = ["V", "R"]
        float_expeted_prefixes = ["Target Volume = ", ">Rate = "]

        string_atrr_base_names = [  # pv values are commands
            "pump_direction_l",  # I/W
            "rate_units_l",  # S/M
            "mode_l",  # P/N/D
            "motor_drive_l",  # BT/BS
            "volume_counter_mode_l",  # EI/EN
        ]
        string_queries = ["D", "U", "M", "B", "E"]
        string_expeted_prefixes = [
            ">Direction: ",
            ">Rate Units: ",
            ">Mode: ",
            ">",
            ">",
        ]

        atrr_names_queries_only = [
            "volume_couner_l",
        ]
        queries_only = ["C"]
        queries_only_expected_prefixes = [">Volume Counter = "]

        # pump number
        attr_name = "pump_number"
        pump_command = "L"
        pump_atrr_instance = AttrRW(  # type: ignore
            Int(),
            io_ref=WpiMicro4ControllerLineSettingIORef(  # type: ignore
                pump_command,
            ),
            initial_value=1,
        )
        setattr(
            self,
            attr_name,
            pump_atrr_instance,
        )

        for line in range(2):
            for j in range(len(float_atrr_names_commands)):
                base_name = float_atrr_names_commands[j]
                attr_name = f"{base_name}{line + 1}"
                setattr(
                    self,
                    attr_name,
                    AttrRW(
                        Float(prec=1),
                        io_ref=WpiMicro4ControllerValueSettingIORef(  # type: ignore
                            float_commands[j],
                            float_queries[j],
                            float_expeted_prefixes[j],
                            line + 1,
                            pump_atrr_instance,
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
                        io_ref=WpiMicro4ControllerCommandSettingIORef(  # type: ignore
                            string_queries[j],
                            string_expeted_prefixes[j],
                            line + 1,
                            pump_atrr_instance,
                        ),
                    ),
                )
            for j in range(len(atrr_names_queries_only)):
                base_name = atrr_names_queries_only[j]
                attr_name = f"{base_name}{line + 1}"
                setattr(
                    self,
                    attr_name,
                    AttrR(
                        Float(),
                        io_ref=WpiMicro4ControllerQueryIORef(  # type: ignore
                            queries_only[j],
                            queries_only_expected_prefixes[j],
                            line + 1,
                            pump_atrr_instance,
                        ),
                    ),
                )
            # state
            state_base_name = "pump_state_l"
            state_query = "G"
            state_query_prefix = ">Motor State: "  # G/H/U/*G/Z (kill)
            attr_name = f"{state_base_name}{line + 1}"
            setattr(
                self,
                attr_name,
                AttrRW(
                    String(),
                    io_ref=WpiMicro4ControllerStateSettingIORef(  # type: ignore
                        state_query, state_query_prefix, line + 1, pump_atrr_instance
                    ),
                ),
            )

            # type
            att_volume = AttrR(String())
            base_name = "syringe_volume_l"
            attr_name = f"{base_name}{line + 1}"
            setattr(self, attr_name, att_volume)
            att_length = AttrR(String())
            base_name = "syringe_length_l"
            attr_name = f"{base_name}{line + 1}"
            setattr(self, attr_name, att_length)
            base_name = "type_l"
            attr_name = f"{base_name}{line + 1}"
            setattr(
                self,
                attr_name,
                AttrRW(
                    String(),
                    io_ref=WpiMicro4ControllerTypeSettingIORef(  # type: ignore
                        ">", line + 1, att_volume, att_length, pump_atrr_instance
                    ),
                ),
            )
