from dataclasses import KW_ONLY, dataclass
from typing import TypeVar

from fastcs.attributes import AttributeIO, AttributeIORef, AttrR, AttrW  # type: ignore
from fastcs.util import ONCE  # type: ignore

from fastcs_wpi_micro4.usb_connection import USBConnection

NumberT = TypeVar("NumberT", int, float, str)


@dataclass
class WpiMicro4ControllerLineSettingIORef(AttributeIORef):  # type: ignore
    command: str
    _: KW_ONLY
    update_period: float | None = ONCE  # type: ignore


# for the settings which require both the command and value
# query is the same a the comm
class WpiMicro4ControllerLineSettingIO(
    AttributeIO[NumberT, WpiMicro4ControllerLineSettingIORef]  # type: ignore
):
    def __init__(self, connection: USBConnection):
        super().__init__()  # type: ignore

        self._connection = connection

    async def send(
        self,
        attr: AttrW[NumberT, WpiMicro4ControllerLineSettingIORef],  # type: ignore
        value: NumberT,  # type: ignore
    ) -> None:
        command = f"{attr.io_ref.command}{attr.dtype(value)}"  # type: ignore
        try:
            r = await self._connection.send_query(f"{command}\r")
            if "OK" in r:
                await self.set(value, attr)  # type: ignore
        except Exception as e:
            print(f"error: LINE query - {e}")

    # to allow for the initial value to be set
    async def update(
        self,
        attr: AttrR[NumberT, WpiMicro4ControllerLineSettingIORef],  # type: ignore
    ) -> None:
        pass

    # rbv set based on the request no query for line number provided
    async def set(
        self,
        value,  # type: ignore
        attr: AttrR[NumberT, WpiMicro4ControllerLineSettingIORef],  # type: ignore
    ):
        await attr.update(attr.dtype(value))  # type: ignore
