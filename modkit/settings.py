from __future__ import annotations

import functools

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
    cache_backend: str = "HASHICORP"
    vault_backend: str = "REDIS"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_ssl: bool = False
    redis_username: str = "default"
    redis_password: SecretStr = SecretStr("password")
    vault_addr: str = "http://localhost:8200"
    vault_token: SecretStr = SecretStr("myroot")
    vault_kv_mount_point: str = "secret"

@functools.cache
def get_settings() -> Settings:
    return Settings()
