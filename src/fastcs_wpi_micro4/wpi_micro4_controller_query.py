from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR
from fastcs.connections import (
    IPConnection,
)
from fastcs.util import ONCE

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerQueryIORef(AttributeIORef):
    name: str
    line_num: int
    _: KW_ONLY
    update_period: float | None = ONCE


class WpiMicro4ControllerQueryIO(AttributeIO[NumberT, WpiMicro4ControllerQueryIORef]):
    def __init__(self, connection: IPConnection):
        super().__init__()

        self._connection = connection

    async def update(self, attr: AttrR[NumberT, WpiMicro4ControllerQueryIORef]) -> None:
        line_command = f"L{attr.io_ref.line_num};"
        await self._connection.send_query(f"{line_command}\n")
        query = f"?{attr.io_ref.name}"
        response = await self._connection.send_query(f"{query}\n")
        value = response.strip(query + "; \n")

        await attr.update(attr.dtype(value))
