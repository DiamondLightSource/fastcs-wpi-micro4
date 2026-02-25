import time
from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrW
from fastcs.connections import (
    IPConnection,
    IPConnectionSettings,
)
from fastcs.util import ONCE

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerValueSettingIORef(AttributeIORef):
    command: str
    query: str
    line_num: int
    _: KW_ONLY
    update_period: float | None = ONCE


# for the settings which require both the command and value
# query is the same a the comm
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
            await self._connection.connect(
                IPConnectionSettings("192.168.1.6", 7004)
            )  # "/dev/ttyUSB0:/dev/ttyUSB0"
            time.wait(3)

    async def send(
        self, attr: AttrW[NumberT, WpiMicro4ControllerValueSettingIORef], value: NumberT
    ) -> None:
        line_command = f"L{attr.io_ref.line_num};"
        command = f"{attr.io_ref.command}{attr.dtype(value)};"
        try:
            await self._connection.send_query(f"{line_command}\n")
        except Exception as e:
            print(f"error: LINE query - {e}")
            await self._connection.connect(IPConnectionSettings("192.168.1.6", 7004))
            time.wait(3)

        list_of_chars = list(command)
        if len(list_of_chars) > 7:  # command letter + 4 numerals +'.' + ';'
            print("Too many chars. The limit is 4.")
        else:
            for ch in list_of_chars:
                await self.task(ch)
            try:
                resp = await self._connection.send_query("\n")
                if len(resp) > 5:
                    val = resp.strip(f"{attr.io_ref.command};\n ")
                    print("val only:", val)
                    if ";" in val:  # for values
                        updated = val.split(";")[1]
                    else:  # for syringe type
                        updated = val[1].capitalize()
                    await attr.update(attr.dtype(updated))
            except Exception as e:
                print(f"error: new line query - {e}")
                await self._connection.connect(
                    IPConnectionSettings("192.168.1.6", 7004)
                )
                time.wait(3)

    # run once at init stage
    async def update(
        self, attr: AttrR[NumberT, WpiMicro4ControllerValueSettingIORef]
    ) -> None:
        line_command = f"L{attr.io_ref.line_num};"
        await self._connection.send_query(f"{line_command}\n")
        query = f"?{attr.io_ref.query}"
        response = await self._connection.send_query(f"{query}\n")
        value = response.strip(query + "; \n")

        await attr.update(attr.dtype(value))
