from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from fastcs.attributes import AttrHandlerR, AttrR
from fastcs.connections import (
    IPConnection,
    IPConnectionSettings,
)
from fastcs.controller import BaseController, Controller
from fastcs.datatypes import String

NumberT = TypeVar("NumberT", int, float)


@dataclass
class BeeperUpdater(AttrHandlerR):
    update_period: float | None = 0.2
    _controller: WpiMicro4Controller | None = None

    async def initialise(self, controller: BaseController):
        assert isinstance(controller, WpiMicro4Controller)
        self._controller = controller

    @property
    def controller(self) -> WpiMicro4Controller:
        if self._controller is None:
            raise RuntimeError("Handler not initialised")

        return self._controller

    async def update(self, attr: AttrR):  # type: ignore
        response = await self.controller.connection.send_query("?1\n")  # type: ignore
        value = response.strip("?1\n")
        await attr.set(value)  # type: ignore


class WpiMicro4Controller(Controller):
    BEEPER1_ON = AttrR(String(), handler=BeeperUpdater())

    def __init__(self, settings: IPConnectionSettings):
        super().__init__()

        self._ip_settings = settings
        self.connection = IPConnection()

    async def connect(self):
        await self.connection.connect(self._ip_settings)  # type: ignore
