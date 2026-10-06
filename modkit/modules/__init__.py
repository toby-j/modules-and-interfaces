"""Composition root. Adding a category = one line here + a port + a folder."""
from __future__ import annotations

from modkit.interfaces import Cache
from modkit.interfaces import Vault
from modkit.modules.registry import Registry
from modkit.settings import get_settings

_settings = get_settings()

cache_registry: Registry[Cache] = Registry(Cache, _settings.cache_backend)
vault_registry: Registry[Vault] = Registry(Vault,    _settings.vault_backend)

REGISTRIES = [cache_registry, vault_registry]
