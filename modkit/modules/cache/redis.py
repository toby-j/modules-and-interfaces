"""
Redis cache adapter for the modkit ``Cache`` port.

Author: Toby Johnson
Date: 01 September 2026
Modified: 02 September 2026
"""

from __future__ import annotations

import asyncio
import logging
from typing import ClassVar

from redis.asyncio import Redis
from redis.exceptions import AuthenticationError, ConnectionError as RedisConnectionError, TimeoutError as RedisTimeoutError
from modkit.interfaces import ErrorMap, HealthCheck, Module, RawRedisClientProvider, ServiceHealth, Startable
from modkit.interfaces.authorisation import RedisCredentialsProvider
from modkit.modules import authorisation_registry

logger = logging.getLogger(__name__)


class RedisCache(RawRedisClientProvider, Startable):
    """
    redis-py backed key/value cache.
    We use the credential module for authentication to Redis whereever it is.
    """

    _health_timeout: float = 5.0

    health_check_error_map: ClassVar[ErrorMap] = (
        (RedisTimeoutError, ServiceHealth.TIMEOUT),
        (AuthenticationError, ServiceHealth.AUTH_FAILED),
        (RedisConnectionError, ServiceHealth.UNREACHABLE),
    ) + Module.health_check_error_map

    def __init__(self) -> None:
        super().__init__()
        self._client: Redis | None = None

    def redis_client(self) -> Redis:
        """
        The underlying redis-py client (requires ``start()``).
        """
        return self._require_client()

    async def start(self) -> None:
        if self._client is not None:
            return

        settings = self.settings
        credentials = authorisation_registry.default
        # If the module that's been selected has the RedisCredentialsProvider extension, use it.
        if isinstance(credentials, RedisCredentialsProvider):
            self._client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                decode_responses=True,
                ssl=settings.redis_ssl,
                credential_provider=credentials.redis_credentials_provider(),
            )
        else:
            self._client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                decode_responses=True,
                username=settings.redis_username,
                password=(settings.redis_password.get_secret_value()),
                ssl=settings.redis_ssl,
            )
        logger.info("cache_started")

    async def health_check(self) -> HealthCheck:
        # This triggers __aenter__ in HealthProbe
        async with self.probe("ping") as probe:
            async with asyncio.timeout(self._health_timeout):
                await self.start()
                await self._require_client().ping()
        # Now we've broken out of async, __aexit__ in HealthProbe is called
        return probe.result

    async def aclose(self) -> None:
        if self._client is None:
            return
        try:
            await self._client.aclose()
        finally:
            self._client = None
            logger.info("cache_closed")

    def _require_client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("cache not started; call start() from the app serving hook first")
        return self._client

    async def get(self, key: str) -> str | None:
        return await self._require_client().get(key)

    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> None:
        await self._require_client().set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._require_client().delete(key)

    async def try_increment(self, key: str, limit: int, ttl_seconds: int) -> bool:
        """
        Check if the user has usage left, if they do permit the request otherwise block it.
        """
        return bool(await self._require_client().eval(_TRY_INCREMENT_LUA, 1, key, limit, ttl_seconds))