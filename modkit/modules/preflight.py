"""Startup gate: resolve, start and health-check every selected module."""
from __future__ import annotations

import logging

from modkit.interfaces import Startable
from modkit.modules import REGISTRIES

logger = logging.getLogger(__name__)


async def run_preflight() -> None:
    errors: list[str] = []
    for reg in REGISTRIES:
        try:
            module = reg.default
            if isinstance(module, Startable):
                await module.start()
            result = await module.health_check()
            if not result["healthy"]:
                errors.append(f"{reg.category}: unhealthy {result['checks']}")
        except Exception as exc:
            errors.append(f"{reg.category}: {exc}")

    if errors:
        raise RuntimeError("Preflight failed:\n" + "\n".join(errors))

    logger.info("preflight_passed: %s", [r.category for r in REGISTRIES])
