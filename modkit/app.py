"""Demo: business logic sees only ports, never a backend name."""
from __future__ import annotations

import asyncio
import logging

from modkit.interfaces import Cache, RawClientProvider
from modkit.modules import cache_registry, vault_registry
from modkit.modules.preflight import run_preflight

logger = logging.getLogger(__name__)


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

    for reg in (cache_registry, vault_registry):
        print(f"active {reg.category} module: {reg.default.name}")

    cache = cache_registry.default
    print(await remember_greeting(cache, "ada"))
    print(await remember_greeting(cache, "ada"))

    if isinstance(cache, RawClientProvider):
        print("this backend exposes a raw client:", type(cache.raw_client()).__name__)
    else:
        print(f"{cache.name} has no raw client to expose")


if __name__ == "__main__":
    asyncio.run(main())
