from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attribute_io import AttributeIO
from fastcs.attribute_io_ref import AttributeIORef
from fastcs.attributes import AttrR, AttrRW, AttrW
from fastcs.connections import (
    IPConnection,
    IPConnectionSettings,
)
from fastcs.controller import Controller
from fastcs.datatypes import Float, Int, String

NumberT = TypeVar("NumberT", int, float)


@dataclass
class WpiMicro4ControllerAttributeIORef(AttributeIORef):
    name: str
    _: KW_ONLY
    update_period: float | None = 0.5


class WpiMicro4ControllerAttributeIO(
    AttributeIO[NumberT, WpiMicro4ControllerAttributeIORef]
):
    def __init__(self, connection: IPConnection):
        super().__init__()

        self._connection = connection

    async def update(self, attr: AttrR[NumberT, WpiMicro4ControllerAttributeIORef]):
        query = f"?{attr.io_ref.name}"
        response = await self._connection.send_query(f"{query}\r\n")
        value = response.strip(query + " ; \r\n")

        if value != "":
            if value != "Set line number:    L1...L4":
                await attr.update(attr.dtype(value))

    async def send(
        self, attr: AttrW[NumberT, WpiMicro4ControllerAttributeIORef], value: NumberT
    ) -> None:
        command = f"{attr.io_ref.name}{attr.dtype(value)};"
        await self._connection.send_command(f"{command}")


@dataclass
class WpiMicro4ControllerLineIORef(AttributeIORef):
    name: str
    _: KW_ONLY
    update_period: float | None = 0.5


class WpiMicro4ControllerLineIO(AttributeIO[NumberT, WpiMicro4ControllerLineIORef]):
    def __init__(self, connection: IPConnection):
        super().__init__()

        self._connection = connection

    async def update(self, attr: AttrR[NumberT, WpiMicro4ControllerLineIORef]):
        query = f"?{attr.io_ref.name}"
        response = await self._connection.send_query(f"{query}\r\n")
        value = response.strip(query + " ; \r\n")

        if value in ["11", "22", "33", "44"]:
            line_number = attr.dtype(value)
            last_digit = line_number % 10
            await attr.update(last_digit)
        elif value != "":
            if value != "Set line number:    L1...L4":
                await attr.update(attr.dtype(value))

    async def send(
        self, attr: AttrW[NumberT, WpiMicro4ControllerLineIORef], value: NumberT
    ) -> None:
        command = f"{attr.io_ref.name}{attr.dtype(value)};"
        await self._connection.send_command(f"{command}")


class WpiMicro4Controller(Controller):
    line_number = AttrRW(Int(), io_ref=WpiMicro4ControllerLineIORef("L"))
    volume_counter = AttrRW(Float(), io_ref=WpiMicro4ControllerAttributeIORef("C"))
    volume = AttrRW(Float(), io_ref=WpiMicro4ControllerAttributeIORef("V"))
    # volume_rate_rbv = AttrR(Float(),
    #  io_ref=WpiMicro4ControllerAttributeIORef("R"))
    # volume_max_rate_rbv = AttrR(Float(),
    # io_ref=WpiMicro4ControllerAttributeIORef("X"))
    # step_rate_rbv = AttrR(Float(), io_ref=WpiMicro4ControllerAttributeIORef("P"))
    # number_of_steps_rbv = AttrR(Float(),
    # io_ref=WpiMicro4ControllerAttributeIORef("T"))
    beeper_on1_rbv = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("1"))
    beeper_on2_rbv = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("2"))
    # press_once_to_run1_rbv = AttrR(
    #    String(), io_ref=WpiMicro4ControllerAttributeIORef("3")
    # )
    # press_once_to_run2_rbv = AttrR(
    #    String(), io_ref=WpiMicro4ControllerAttributeIORef("4")
    # )
    # microstepping_on1_rbv = AttrR(
    #    String(), io_ref=WpiMicro4ControllerAttributeIORef("6")
    # )
    # microstepping_on2_rbv = AttrR(
    #    String(), io_ref=WpiMicro4ControllerAttributeIORef("7")
    # )
    # grupped_mode_on_rbv = AttrR(String(),
    # io_ref=WpiMicro4ControllerAttributeIORef("M"))
    # pump_direction_rbv = AttrR(String(),
    # io_ref=WpiMicro4ControllerAttributeIORef("D"))
    # pump_units_rbv = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("U"))
    # pump_running_rbv = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("G"))
    # syringe_type_rbv = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("S"))

    def __init__(self, settings: IPConnectionSettings):
        self._ip_settings = settings
        self.connection = IPConnection()

        super().__init__(
            ios=[
                WpiMicro4ControllerAttributeIO(self.connection),
                WpiMicro4ControllerLineIO(self.connection),
            ]
        )

    async def connect(self):
        await self.connection.connect(self._ip_settings)
