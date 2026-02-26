import asyncio
from dataclasses import dataclass

import serial_asyncio
from fastcs.tracer import Tracer


class DisconnectedError(Exception):
    """Raised if the ip connection is disconnected."""

    pass


@dataclass
class USBConnectionSettings:
    port: str = "/dev/ttyUSB0"
    baudrate: int = 9600


@dataclass
class StreamConnection:
    """For reading and writing to a stream."""

    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    def __post_init__(self):
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    async def send_message(self, message) -> None:
        self.writer.write(message.encode("utf-8"))
        await self.writer.drain()

    async def receive_response(self) -> str:
        data = await self.reader.readuntil(b"OK\n\r")
        return data.decode("utf-8")

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()


class USBConnection(Tracer):
    """For connecting to an ip using a `StreamConnection`."""

    def __init__(self):
        super().__init__()
        self.__connection = None

    @property
    def _connection(self) -> StreamConnection:
        if self.__connection is None:
            raise DisconnectedError(
                "Need to call connect() before using USBConnection."
            )

        return self.__connection

    async def connect(self, settings: USBConnectionSettings):
        reader, writer = await serial_asyncio.open_serial_connection(
            url=settings.port, baudrate=settings.baudrate
        )
        self.__connection = StreamConnection(reader, writer)

    async def send_command(self, message: str) -> None:
        async with self._connection as connection:
            await connection.send_message(message)

    async def send_query(self, message: str) -> str:
        async with self._connection as connection:
            await connection.send_message(message)
            response = await connection.receive_response()
            self.log_event(
                "Received query response",
                query=message.strip(),
                response=response.strip(),
            )
            return response

    async def close(self):
        async with self._connection as connection:
            await connection.close()
            self.__connection = None
