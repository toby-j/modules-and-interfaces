"""
Application entry point.

Performs preflight checks, which loads each module into available interfaces and performs health checks on each.
"""
from __future__ import annotations

import asyncio
import logging

from modkit.interfaces import Cache, Vault
from modkit.modules import cache_registry, vault_registry
from modkit.modules.preflight import run_preflight

logger = logging.getLogger(__name__)

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await run_preflight()

    # The selected modules are now ready to be used
    cache: Cache = cache_registry.default
    vault: Vault = vault_registry.default

    logger.info(await cache.health_check())
    logger.info(await vault.health_check())

if __name__ == "__main__":
    asyncio.run(main())
