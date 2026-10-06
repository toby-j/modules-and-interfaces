"""Vault port: read-only access to secrets by path/field."""
from __future__ import annotations

from abc import abstractmethod

from modkit.interfaces.module import Module


class Vault(Module):
    """
    Base interface for secret storage services.
    """

    category = "vault"

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
    Extension for vault backends that can lease short-lived database
    credentials (e.g. HashiCorp Vault's database secrets engine).
    """

    @abstractmethod
    def dynamic_credentials(self, role: str) -> tuple[str, str]:
        """
        Generate a fresh ``(username, password)`` for a secrets-engine role.

        :param role: name of the secrets-engine role to read
        :returns: a ``(username, password)`` pair, freshly leased each call
        """
        ...