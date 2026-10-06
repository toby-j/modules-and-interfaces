"""Cache port: a simple key/value store with optional expiry."""
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from modkit.interfaces.module import Module


class Cache(Module):
    """Key/value cache. Every backend must support this minimal contract."""

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