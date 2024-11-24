import typing

from ..entities import Message
from ..senders import Sender


class Command(typing.Protocol):
    def can_handle(self, message: Message) -> bool: ...
    async def handle(self, message: Message, sender: Sender) -> None: ...
