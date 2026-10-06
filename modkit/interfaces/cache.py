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


class RawClientProvider(Cache):
    """
    Capability for a cache backend that wraps a real client library and can
    hand it out for advanced use cases the port doesn't cover.

    Not every backend has one (e.g. the in-process ``memory`` adapter), so
    this is kept separate from ``Cache`` and checked with ``isinstance``.
    """

    @abstractmethod
    def raw_client(self) -> Any:
        """
        Return the underlying client object. Requires ``start()`` to have run.
        """
        ...