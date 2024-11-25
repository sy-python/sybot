import aiohttp
import dotenv

import os
from typing import Protocol, Self


class TokenError(Exception): ...


class MissingTokenError(TokenError): ...


class RefreshError(TokenError): ...


class InvalidTokenError(TokenError): ...


def get_env_token(key: str) -> str:
    token = os.getenv(key)
    if token is None:
        raise MissingTokenError(f"Missing {key}. Please set it in .env")
    return token


class TokenManager(Protocol):
    async def validate(self) -> bool: ...
    async def refresh(self) -> None: ...
    async def get(self) -> str: ...

    @classmethod
    def from_env(cls) -> Self: ...


class DiscordTokenManager(TokenManager):
    def __init__(self, token: str):
        self.token = token

    @staticmethod
    async def validate(token: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://discord.com/api/users/@me",
                headers={"Authorization": f"Bot {token}"},
            ) as response:
                return response.status == 200

    async def refresh(self) -> None:
        raise RefreshError(
            "Discord token is not refreshable. If the token failed to validate, it means it is invalid."
        )

    async def get(self) -> str:
        if not await self.validate(self.token):
            raise InvalidTokenError("Discord token is invalid")
        return self.token

    @classmethod
    def from_env(cls) -> Self:
        token = get_env_token("DISCORD_TOKEN")
        return cls(token)


class TwitchTokenManager(TokenManager):
    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        twitch_client_id: str,
        twitch_client_secret: str,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.twitch_client_id = twitch_client_id
        self.twitch_client_secret = twitch_client_secret

    @staticmethod
    async def validate(token: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://id.twitch.tv/oauth2/validate",
                headers={"Authorization": f"OAuth {token}"},
            ) as response:
                return response.status == 200

    async def refresh(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://id.twitch.tv/oauth2/token",
                data={
                    "client_id": self.twitch_client_id,
                    "client_secret": self.twitch_client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
            ) as response:
                access_token = (await response.json())["access_token"]
                dotenv.set_key(".env", "TWITCH_TOKEN", access_token)
                self.access_token = access_token

    async def get(self) -> str:
        if not await self.validate(self.access_token):
            await self.refresh()
        return self.access_token

    @classmethod
    def from_env(cls):
        access_token = get_env_token("TWITCH_TOKEN")
        refresh_token = get_env_token("TWITCH_REFRESH_TOKEN")
        client_id = get_env_token("TWITCH_CLIENT_ID")
        client_secret = get_env_token("TWITCH_CLIENT_SECRET")
        return cls(access_token, refresh_token, client_id, client_secret)
