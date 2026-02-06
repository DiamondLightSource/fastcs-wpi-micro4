import asyncio


class Connection:
    line = 1

    async def send(self, command: str):
        await asyncio.sleep(0.1)

        if command.startswith("!L"):
            self.line = int(command[2:])
            return command[1:]

        elif command.startswith("!C"):
            return f"L{self.line}C"

        elif command.startswith("?"):
            return f"L{self.line}{command[1:]}"


class Controller:
    line = 1

    def __init__(self, connection):
        self.connection = connection

    async def update(self, period: float):
        line = self.line

        while True:
            await asyncio.gather(
                self.change_line(line),
                self.update_field("A"),
                self.update_field("B"),
            )

            line += 1
            if line > 4:
                line = 1

            await asyncio.sleep(period)

    async def update_field(self, name: str):
        line = self.line
        query = f"?{name}"
        print(f"Do {query}")
        response = await self.connection.send(query)

        if not response.startswith(f"L{line}"):
            raise ValueError(f"Expected line {line}, got {response}")

        print(f"{line}: {query} -> {response}")

    async def change_line(self, line: int):
        self.line = line
        query = f"!L{line}"
        print(f"Do {query}")
        await self.connection.send(query)

    async def put(self):
        await asyncio.gather(
            self.change_line(2),
            self.send_command(),
        )

    async def send_command(self):
        print("Do !C")
        response = await self.connection.send("!C")

        if not response.startswith("L2C"):
            raise ValueError(f"Expected L2C, got {response}")

        print(f"!C -> {response}")


async def main():
    connection = Connection()
    controller = Controller(connection)

    asyncio.create_task(controller.update(0.2))

    await asyncio.sleep(1)

    while True:
        await controller.put()
        await asyncio.sleep(0.33)
