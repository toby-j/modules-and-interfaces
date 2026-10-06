"""Locked module sets per deployment topology.

Prevents a restricted environment being configured with a backend it may not use.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class DeploymentEnvironment(str, Enum):
    """Selected via the `DEPLOYMENT_ENVIRONMENT` environment variable."""

    PRODUCTION = "PRODUCTION"


class ModuleSet(BaseModel):
    """The one-backend-per-category selection for a deployment environment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cache_backend: str
    vault_backend: str


ENVIRONMENTS: dict[DeploymentEnvironment, ModuleSet] = {
    DeploymentEnvironment.PRODUCTION: ModuleSet(
        cache_backend="REDIS",
        vault_backend="HASHICORP",
    ),
}
