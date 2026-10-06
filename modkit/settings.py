from __future__ import annotations

import functools

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from modkit.environments import ENVIRONMENTS, DeploymentEnvironment


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    deployment_environment: DeploymentEnvironment | None = None

    cache_backend: str | None = None
    vault_backend: str | None = None

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_ssl: bool = False
    redis_username: str = "default"
    redis_password: SecretStr = SecretStr("")

    vault_addr: str = "http://localhost:8200"
    vault_token: SecretStr = SecretStr("")
    vault_kv_mount_point: str = "secret"

    def model_post_init(self, _ctx: object) -> None:
        """An environment profile overrides per-backend settings, and is authoritative."""
        if self.deployment_environment is None:
            return
        locked = ENVIRONMENTS[self.deployment_environment]
        for field, value in locked.model_dump().items():
            current = getattr(self, field)
            if current is not None and current.upper() != value:
                raise ValueError(
                    f"{field}={current!r} is not permitted in "
                    f"{self.deployment_environment.value}; must be {value!r}"
                )
            object.__setattr__(self, field, value)


@functools.cache
def get_settings() -> Settings:
    return Settings()
