import asyncio
from typing import Iterable

from ..entities import Message
from .base import Sender


class MultiSender:
    def __init__(self, senders: Iterable[Sender]):
        self.senders = senders

    async def send(self, message: Message) -> None:
        results = await asyncio.gather(
            *(sender.send(message) for sender in self.senders), return_exceptions=True
        )
        exceptions = [result for result in results if isinstance(result, Exception)]
        if exceptions:
            raise ExceptionGroup("Failed to send message to all senders", exceptions)
