"""
Authorisation module interface for the modkit backend.

Author: Toby Johnson
Date: 01 September 2026
Modified: 03 September 2026
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from redis import CredentialProvider

from modkit.interfaces.module import Module


class Authorisation(Module):
    """
    Return the credentials for connecting to a service.
    These functions are then called from within other modules to connect.
    """

    category = "authorisation"


class RedisCredentialsProvider(Authorisation):
    """
    Redis is an optional resource. An authorisation backend that supports Redis
    will implement both ``Authorisation`` and this class.
    """

    @abstractmethod
    def redis_credentials_provider(self) -> CredentialProvider:
        """
        Return a redis-py ``CredentialProvider`` for authenticating to Redis.

        redis-py invokes the provider on every (re)connect, so short-lived or
        rotated credentials are always current.
        """
        ...


class PostgresCredentialsProvider(Authorisation):
    """
    Postgres is an optional resource. An authorisation backend that supports
    Postgres will implement both ``Authorisation`` and this class.
    """

    @abstractmethod
    def postgres_credentials(self) -> tuple[str, str]:
        """
        Return a fresh ``(username, password)`` pair for connecting to Postgres.

        Called on every (re)connect so short-lived or rotated credentials are
        always current.
        """
        ...