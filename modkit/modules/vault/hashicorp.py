"""HashiCorp Vault adapter for the `Vault` port.

Needs a reachable Vault server - selected by `DEPLOYMENT_ENVIRONMENT=SECURE`.
Demonstrates `DynamicCredentialsCapable`: leasing short-lived credentials
instead of reading a static secret.
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


class HashiCorp(DynamicCredentialsCapable):
    """Vault backend using HashiCorp Vault's KV v2 and database secrets engines."""

    _health_timeout: float = 5.0

    health_check_error_map: ClassVar[ErrorMap] = (
        (RequestsTimeout, ServiceHealth.TIMEOUT),
        (RequestsConnectionError, ServiceHealth.UNREACHABLE),
        (hvac.exceptions.Forbidden, ServiceHealth.AUTH_FAILED),
        (hvac.exceptions.Unauthorized, ServiceHealth.AUTH_FAILED),
    ) + Module.health_check_error_map

    def __init__(self) -> None:
        super().__init__()
        settings = self.settings
        self._mount_point = settings.vault_kv_mount_point
        self._client = hvac.Client(url=settings.vault_addr, token=settings.vault_token.get_secret_value())

    async def health_check(self) -> HealthCheck:
        async with self.probe("authenticated") as probe:
            async with asyncio.timeout(self._health_timeout):
                authenticated = await asyncio.to_thread(self._client.is_authenticated)
            if not authenticated:
                probe.fail(ServiceHealth.AUTH_FAILED)
        return probe.result

    def get(self, path: str, field: str) -> str:
        """
        Return a single field from a secret held in the KV v2 secrets engine.
        """
        secret = self._client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=self._mount_point
        )
        return secret["data"]["data"][field]

    def dynamic_credentials(self, role: str) -> tuple[str, str]:
        """
        Generate a short-lived `(username, password)` from Vault's database
        secrets engine.
        """
        data = self._client.secrets.database.generate_credentials(name=role)["data"]
        return data["username"], data["password"]
