"""
Vault (generic secrets) module interface for the modkit backend.

To surely access and manage sensitive secrets by key name.

Author: Toby Johnson
Date: 01 September 2026
Modified: 02 September 2026
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from modkit.interfaces.module import Module

if TYPE_CHECKING:
    from modkit.settings import VaultSettings


class Vault(Module):
    """
    Base interface for Vault storage services.
    """

    category = "vault"

    @property
    def vault_settings(self) -> VaultSettings:
        return self.settings.vault

    @abstractmethod
    def get(self, path: str, field: str) -> str:
        """
        Return a single field value from a secret held in the vault.

        :param path: path/name of the secret to fetch
        :param field: name of the field within that secret to return
        """
        ...


class DynamicCredentialsCapable(Vault):
    """
    Capability mixin for vault backends that can lease short-lived database
    credentials (e.g. HashiCorp Vault's database secrets engine).

    Vault modules that need this optional functionality import this.

    Kept separate from ``Vault`` since not every secret store supports dynamic
    credentials (e.g. static stores like Azure Key Vault).
    """

    @abstractmethod
    def dynamic_credentials(self, role: str) -> tuple[str, str]:
        """
        Generate a fresh ``(username, password)`` for a secrets-engine role.

        :param role: name of the secrets-engine role to read
        :returns: a ``(username, password)`` pair, freshly leased each call
        """
        ...