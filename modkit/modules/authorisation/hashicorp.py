"""
HashiCorp Vault backend for the modkit ``Vault`` port.

Author: Toby Johnson
Date: 01 September 2026
Modified: 02 September 2026
"""

from __future__ import annotations

import asyncio
import logging
from typing import ClassVar

import hvac
import hvac.exceptions
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout

from modkit.interfaces import DynamicCredentialsCapable, ErrorMap, HealthCheck, Module, ServiceHealth

logger = logging.getLogger(__name__)

class HashiCorpVault(DynamicCredentialsCapable):
    """
    HashiCorp Vault implementation of the Vault interface.

    Also implements ``DynamicCredentialsCapable`` via ``dynamic_credentials``,
    returning short-lived usernames/passwords using HashiCorp Vault's database
    secrets engine.
    """
    def __init__(self) -> None:
        super().__init__()
        self._url = str(self.vault_settings.addr)
        self.client = hvac.Client(
            url=self._url,
            token=self.vault_settings.token.get_secret_value()
        )

    health_check_error_map: ClassVar[ErrorMap] = (
        (RequestsTimeout, ServiceHealth.TIMEOUT),
        (RequestsConnectionError, ServiceHealth.UNREACHABLE),
        (hvac.exceptions.Forbidden, ServiceHealth.AUTH_FAILED),
        (hvac.exceptions.Unauthorized, ServiceHealth.AUTH_FAILED),
    ) + Module.health_check_error_map

    async def health_check(self) -> HealthCheck:
        def _authentication_check() -> bool:
            return self.client.is_authenticated()

        async with self.probe("authenticated") as probe:
            if not await asyncio.to_thread(_authentication_check):
                probe.fail(ServiceHealth.AUTH_FAILED)
        return probe.result

    def get(self, path: str, field: str) -> str:
        """
        Return a single field from a secret held in the KV v2 secrets engine.
        :param path: path of the secret within the KV mount
        :param field: name of the field to read from that secret
        """
        secret = self.client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=self.vault_settings.kv_mount_point
        )
        return secret["data"]["data"][field]

    def dynamic_credentials(self, role: str) -> tuple[str, str]:
        """
        Generate a short-lived ``(username, password)`` from Vault.

        :param role: name of the database secrets-engine role to read
        :returns: a ``(username, password)`` pair
        """
        data = self.client.secrets.database.generate_credentials(name=role)["data"]
        return data["username"], data["password"]