"""
Cache module interface for the modkit backend.

Author: Toby Johnson
Date: 01 September 2026
Modified: 02 September 2026
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from modkit.interfaces.module import Module

if TYPE_CHECKING:
    from redis.asyncio import Redis


class Cache(Module):
    """
    Cache solution used for access tokens, session token, any short-lived credentials can be stored here.
    """

    category = "cache"

    @abstractmethod
    async def aclose(self) -> None:
        """
        Release resources / close the connection. Must be idempotent.
        """
        ...

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """
        Return the value for ``key``, or ``None`` if it is not present.
        """
        ...

    @abstractmethod
    async def set(self, key: str, value: str, *, ttl_seconds: int | None = None) -> None:
        """
        Store ``value`` under ``key``, optionally expiring after ``ttl_seconds``.
        """
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Remove ``key`` if present; a no-op if it is not.
        """
        ...

    @abstractmethod
    async def try_increment(self, key: str, limit: int, ttl_seconds: int) -> bool:
        """
        Check if the user has usage left, if they do permit the request otherwise block it.
        """
        ...


class RawRedisClientProvider(Cache):
    """
    Capability for a cache backend that can hand out its underlying redis-py
    client.

    Only needed for Quart's lifecycle session.
    """

    @abstractmethod
    def redis_client(self) -> "Redis":
        """
        Return the underlying redis-py client. Requires ``start()`` to have run.
        """
        ...