"""Ports: every interface a module category exposes to the rest of the app."""
from __future__ import annotations

from modkit.interfaces.module import (
    ErrorMap, HealthCheck, Module, ServiceHealth, Startable,
)
from modkit.interfaces.cache import Cache, RawClientProvider
from modkit.interfaces.vault import DynamicCredentialsCapable, Vault

__all__ = [
    "Cache",
    "DynamicCredentialsCapable",
    "ErrorMap",
    "HealthCheck",
    "Module",
    "RawClientProvider",
    "ServiceHealth",
    "Startable",
    "Vault",
]
