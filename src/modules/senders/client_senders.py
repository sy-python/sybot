import discord
import twitchio

from ..entities import Message


class DiscordSender:
    def __init__(self, channel: discord.TextChannel):
        self.channel = channel

    async def send(self, message: Message) -> None:
        await self.channel.send(message.content)


class TwitchSender:
    def __init__(self, channel: twitchio.Channel):
        self.channel = channel

    async def send(self, message: Message) -> None:
        await self.channel.send(message.content)
