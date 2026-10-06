"""Demo: business logic sees only the port."""
from __future__ import annotations

import asyncio
import logging

from modkit.interfaces import Cache, RawClientProvider
from modkit.modules import cache_registry
from modkit.modules.preflight import run_preflight


async def remember_greeting(cache: Cache, user: str) -> str:
    """Note: typed against the port. No backend name appears anywhere."""
    cached = await cache.get(f"greeting:{user}")
    if cached:
        return f"(cached) {cached}"
    greeting = f"Hello, {user}"
    await cache.set(f"greeting:{user}", greeting, ttl_seconds=60)
    return greeting


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await run_preflight()

    cache = cache_registry.default
    print(f"active cache module: {cache.name}")
    print(await remember_greeting(cache, "toby"))
    print(await remember_greeting(cache, "toby"))

    # Capability detection instead of backend branching:
    if isinstance(cache, RawClientProvider):
        print("this backend exposes a raw client:", cache.raw_client())


if __name__ == "__main__":
    asyncio.run(main())
