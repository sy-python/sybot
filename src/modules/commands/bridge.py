from ..entities import Message
from ..senders import Sender


class BridgeCommand:
    def __init__(self, target_platform: str):
        self.target_platform = target_platform

    def can_handle(self, message: Message) -> bool:
        return message.sender.platform != self.target_platform

    async def handle(self, message: Message, sender: Sender):
        await sender.send(message)
