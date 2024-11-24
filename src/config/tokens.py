import aiohttp
import dotenv

import os
import typing

dotenv.load_dotenv()


class TokenError(Exception): ...


class TokenManager(typing.Protocol):
    env_name: str

    @staticmethod
    async def validate(token: str) -> bool: ...
    @staticmethod
    async def refresh() -> str: ...
    async def get(self) -> str:
        token = os.getenv(self.env_name)
        if token is None:
            raise TokenError(f"Missing {self.env_name}. Please set it in .env")
        if not await self.validate(token):
            token = await self.refresh()
        return token


class DiscordTokenManager(TokenManager):
    env_name = "DISCORD_TOKEN"

    @staticmethod
    async def validate(token: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://discord.com/api/users/@me",
                headers={"Authorization": f"Bot {token}"},
            ) as response:
                return response.status == 200

    async def refresh(self) -> str:
        raise TokenError(
            "Discord token is not refreshable. If the token failed to validate, it means it is invalid."
        )


class TwitchTokenManager(TokenManager):
    env_name = "TWITCH_TOKEN"

    @staticmethod
    async def validate(token: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://id.twitch.tv/oauth2/validate",
                headers={"Authorization": f"OAuth {token}"},
            ) as response:
                return response.status == 200

    @staticmethod
    async def refresh() -> str:
        refresh_token = os.getenv("TWITCH_REFRESH_TOKEN")
        twitch_client_id = os.getenv("TWITCH_CLIENT_ID")
        twitch_client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        if refresh_token is None:
            raise TokenError("Missing TWITCH_REFRESH_TOKEN. Please set it in .env")
        if twitch_client_id is None:
            raise TokenError("Missing TWITCH_CLIENT_ID. Please set it in .env")
        if twitch_client_secret is None:
            raise TokenError("Missing TWITCH_CLIENT_SECRET. Please set it in .env")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://id.twitch.tv/oauth2/token",
                data={
                    "client_id": twitch_client_id,
                    "client_secret": twitch_client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            ) as response:
                return (await response.json())["access_token"]
