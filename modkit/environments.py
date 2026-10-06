"""Locked module sets per deployment topology.

Prevents a restricted environment being configured with a backend it may not use.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class DeploymentEnvironment(str, Enum):
    LOCAL = "LOCAL"
    SECURE = "SECURE"


class ModuleSet(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    cache_backend: str


ENVIRONMENTS: dict[DeploymentEnvironment, ModuleSet] = {
    DeploymentEnvironment.LOCAL:  ModuleSet(cache_backend="MEMORY"),
    DeploymentEnvironment.SECURE: ModuleSet(cache_backend="FAKEREDIS"),
}
