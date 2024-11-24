from ..entities import Message


class ConsoleSender:
    async def send(self, message: Message) -> None:
        print(message)


class TestSender:
    def __init__(self):
        self.messages: list[Message] = []

    async def send(self, message: Message) -> None:
        self.messages.append(message)

    def clear(self):
        self.messages = []
