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
from fastcs.datatypes import Float, Int
from fastcs.wrappers import command

NumberT = TypeVar("NumberT", int, float)


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


# queries only
@dataclass
class WpiMicro4ControllerAttributeIORef(AttributeIORef):
    name: str
    _: KW_ONLY
    update_period: float | None = 0.5


# Queries only
class WpiMicro4ControllerAttributeIO(
    AttributeIO[NumberT, WpiMicro4ControllerAttributeIORef]
):
    def __init__(self, connection: IPConnection):
        super().__init__()

        self._connection = connection

    async def update(self, attr: AttrR[NumberT, WpiMicro4ControllerAttributeIORef]):
        query = f"?{attr.io_ref.name}"
        response = await self._connection.send_query(f"{query}\r\n")
        # make sure the query and response match
        if query in response and ";" not in response:
            value = response.strip(query + " \r\n")
            await attr.update(attr.dtype(value))
        # else: #what if it doesn't - new line arrives

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
    line_number = AttrW(Int(), io_ref=WpiMicro4ControllerSettingIORef("L"))
    volume_counter_1 = AttrW(
        Float(), io_ref=WpiMicro4ControllerSettingIORef("C")
    )  # TODO: check what happens to the value
    volume_rbv = AttrR(Float(), io_ref=WpiMicro4ControllerAttributeIORef("V"))
    # volume_counter_rbv = AttrR(Float(), io_ref=WpiMicro4ControllerAttributeIORef("C"))
    # delivery_rate_rbv = AttrR(Float(), io_ref=WpiMicro4ControllerAttributeIORef("R"))
    # volume_max_rate_rbv =
    # AttrR(Float(), io_ref=WpiMicro4ControllerAttributeIORef("X"))
    # step_rate_rbv = AttrR(Float(), io_ref=WpiMicro4ControllerAttributeIORef("P"))
    # number_of_steps_rbv = AttrR(Float(),
    # io_ref=WpiMicro4ControllerAttributeIORef("T"))
    # beeper_on1_rbv = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("1"))
    # beeper_on2_rbv = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("2"))
    # press_once_to_run1_rbv = AttrR(
    #    String(), io_ref=WpiMicro4ControllerAttributeIORef("3"))
    # press_once_to_run2_rbv = AttrR(
    #    String(), io_ref=WpiMicro4ControllerAttributeIORef("4"))
    # microstepping_on1_rbv = AttrR(
    #    String(), io_ref=WpiMicro4ControllerAttributeIORef("6"))
    # microstepping_on2_rbv = AttrR(
    #    String(), io_ref=WpiMicro4ControllerAttributeIORef("7"))
    # grupped_mode_on_rbv =
    # AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("M"))
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
                WpiMicro4ControllerSettingIO(self.connection),
            ]
        )

    async def connect(self):
        await self.connection.connect(self._ip_settings)

    @command()
    async def set_linen_nr1(self):
        await self.line_number.put(self.line_number.dtype(1), sync_setpoint=True)
        await asyncio.sleep(0.1)

    @command()
    async def set_linen_nr2(self):
        await self.line_number.put(self.line_number.dtype(2), sync_setpoint=True)
        await asyncio.sleep(0.11)

    @command()
    async def set_linen_nr3(self):
        await self.line_number.put(self.line_number.dtype(3), sync_setpoint=True)
        await asyncio.sleep(0.1)

    @command()
    async def set_linen_nr4(self):
        await self.line_number.put(self.line_number.dtype(4), sync_setpoint=True)
        await asyncio.sleep(0.1)
