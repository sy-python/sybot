from typing import Protocol

from ..entities import Message


class Sender(Protocol):
    async def send(self, message: Message): ...
