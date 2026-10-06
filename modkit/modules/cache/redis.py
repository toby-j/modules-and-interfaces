"""
redis-py backed adapter for the `Cache` port.
"""
from __future__ import annotations

import asyncio
import logging
from typing import ClassVar

from redis.asyncio import Redis as AsyncRedis
from redis.exceptions import (
    AuthenticationError,
    ConnectionError as RedisConnectionError,
    TimeoutError as RedisTimeoutError,
)

from modkit.interfaces import ErrorMap, HealthCheck, Module, ServiceHealth, Startable, Cache

logger = logging.getLogger(__name__)


class Redis(Cache, Startable):
    """Cache backed by a real Redis server via redis-py."""

    _health_timeout: float = 5.0

    # As we look to find a match, the fallback base error exceptions from the
    health_check_error_map: ClassVar[ErrorMap] = (
        (RedisTimeoutError, ServiceHealth.TIMEOUT),
        (AuthenticationError, ServiceHealth.AUTH_FAILED),
        (RedisConnectionError, ServiceHealth.UNREACHABLE),
    ) + Module.health_check_error_map


    def __init__(self) -> None:
        super().__init__()
        self._client: AsyncRedis | None = None

    async def start(self) -> None:
        if self._client is not None:
            return

        settings = self.settings
        self._client = AsyncRedis(
            host=settings.redis_host,
            port=settings.redis_port,
            ssl=settings.redis_ssl,
            username=settings.redis_username,
            password=settings.redis_password.get_secret_value(),
            decode_responses=True,
        )
        logger.info("cache_started backend=redis")

    async def health_check(self) -> HealthCheck:
        async with self.probe("ping") as probe:
            async with asyncio.timeout(self._health_timeout):
                await self.start()
                await self._require_client().ping()
        return probe.result

    async def aclose(self) -> None:
        if self._client is None:
            return
        try:
            await self._client.aclose()
        finally:
            self._client = None
            logger.info("cache_closed backend=redis")

    def _require_client(self) -> AsyncRedis:
        if self._client is None:
            raise RuntimeError("cache not started; call start() first")
        return self._client

    async def get(self, key: str) -> str | None:
        return await self._require_client().get(key)

    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> None:
        await self._require_client().set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._require_client().delete(key)
