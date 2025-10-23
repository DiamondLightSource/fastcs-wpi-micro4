from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attribute_io import AttributeIO
from fastcs.attribute_io_ref import AttributeIORef
from fastcs.attributes import AttrR
from fastcs.connections import (
    IPConnection,
    IPConnectionSettings,
)
from fastcs.controller import Controller
from fastcs.datatypes import String

NumberT = TypeVar("NumberT", int, float)


@dataclass
class WpiMicro4ControllerAttributeIORef(AttributeIORef):
    name: str
    _: KW_ONLY
    update_period: float | None = 0.2


class WpiMicro4ControllerAttributeIO(
    AttributeIO[NumberT, WpiMicro4ControllerAttributeIORef]
):
    def __init__(self, connection: IPConnection):
        super().__init__()

        self._connection = connection

    async def update(self, attr: AttrR[NumberT, WpiMicro4ControllerAttributeIORef]):
        query = f"{attr.io_ref.name}?\n"
        response = await self._connection.send_query(query)
        value = response.strip(query + " ")

        await attr.set(attr.dtype(value))

    # async def send(
    #    self, attr: AttrW[NumberT, WpiMicro4ControllerAttributeIORef], value: NumberT
    # ) -> None:
    #    command = f"{attr.io_ref.name}={attr.dtype(value)}"
    #    await self._connection.send_command(f"{command}\n")


class WpiMicro4Controller(Controller):
    BEEPER_ON1_RBV = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("1"))
    BEEPER_ON2_RBV = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("2"))
    PRESS_ONCE_TO_RUN1_RBV = AttrR(
        String(), io_ref=WpiMicro4ControllerAttributeIORef("3")
    )
    PRESS_ONCE_TO_RUN2_RBV = AttrR(
        String(), io_ref=WpiMicro4ControllerAttributeIORef("4")
    )
    MICROSTEPPING_ON1_RBV = AttrR(
        String(), io_ref=WpiMicro4ControllerAttributeIORef("6")
    )
    MICROSTEPPING_ON2_RBV = AttrR(
        String(), io_ref=WpiMicro4ControllerAttributeIORef("7")
    )
    GROUPED_MODE_RBV = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("M"))
    SYRINGE_TYPE_RBV = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("S"))
    PUMP_DIRECTION_RBV = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("D"))
    PUMP_UNITS_RBV = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("U"))
    PUMP_RUNNING_RBV = AttrR(String(), io_ref=WpiMicro4ControllerAttributeIORef("G"))

    # GRUPED_MODE = AttrRW(String(), io_ref=WpiMicro4ControllerAttributeIORef("G")) #N
    # NOT_GRUPED_MODE = AttrRW(String(), io_ref=WpiMicro4ControllerAttributeIORef("N"))

    def __init__(self, settings: IPConnectionSettings):
        self._ip_settings = settings
        self.connection = IPConnection()

        super().__init__(ios=[WpiMicro4ControllerAttributeIO(self.connection)])

    async def connect(self):
        await self.connection.connect(self._ip_settings)  # type: ignore
