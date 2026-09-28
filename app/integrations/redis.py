"""Redis integration (ping/health and a shared client for future use).

Only this module talks to the Redis SDK from the API process; Celery
uses Redis as its broker independently.
"""

from typing import TYPE_CHECKING

import redis.asyncio as redis_asyncio

from app.core.config import Settings

if TYPE_CHECKING:
    from fastapi import FastAPI


class RedisIntegration:
    def __init__(self, url: str) -> None:
        self._client = redis_asyncio.from_url(url, decode_responses=True)

    @property
    def client(self) -> redis_asyncio.Redis:
        return self._client

    async def ping(self) -> bool:
        try:
            return bool(await self._client.ping())
        except Exception:
            return False

    async def close(self) -> None:
        await self._client.aclose()


def get_redis_integration(app: "FastAPI") -> RedisIntegration:
    """Return the app-scoped Redis integration, creating it on first use."""
    integration = getattr(app.state, "redis", None)
    if integration is None:
        settings: Settings = app.state.settings
        integration = RedisIntegration(url=settings.redis_url)
        app.state.redis = integration
    return integration