"""Base contract shared by every module category."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import StrEnum
from types import TracebackType
from typing import ClassVar, TypedDict
from modkit.settings import get_settings

logger = logging.getLogger(__name__)

class ServiceHealth(StrEnum):
    OK = "ok"
    TIMEOUT = "timeout"
    UNREACHABLE = "unreachable"
    AUTH_FAILED = "auth_failed"
    UNKNOWN = "unknown"

ErrorMap = tuple[tuple[type[BaseException], ServiceHealth], ...]

class HealthCheck(TypedDict):
    healthy: bool
    checks: dict[str, ServiceHealth]

class HealthProbe:
    """Async context manager: run a named check, classify anything it raises."""

    def __init__(self, module: Module, name: str) -> None:
        self._module = module
        self.name = name
        self.result: HealthCheck = {"healthy": True, "checks": {name: ServiceHealth.OK}}

    def fail(self, code: ServiceHealth) -> None:
        self.result = {"healthy": False, "checks": {self.name: code}}

    async def __aenter__(self) -> "HealthProbe":
        """
        Entry method for setup. Returns instance to be used.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        """
        For cleanup and exception management when HealthProbe is async called
        :return: Boolean -> true which suppresses exception, false which unwinds any caught
        """
        # BaseException (CancelledError etc.) is not a health signal: let it unwind.
        if not isinstance(exc, Exception):
            return False
        code = self._module.classify_health_check_error(exc)
        logger.warning("%s health check failed: %s", type(self._module).__name__, code)
        self.fail(code)
        return True  # suppressed: the failure is now data, not an exception


class Module(ABC):
    """Marker base shared by every module category."""

    name: ClassVar[str]      # derived from the filename
    category: ClassVar[str]  # set by the port (e.g. "cache")

    health_check_error_map: ClassVar[ErrorMap] = (
        (TimeoutError, ServiceHealth.TIMEOUT),
        (ConnectionError, ServiceHealth.UNREACHABLE),
    )

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Registry name is the filename, runs once per subclass when it's initialised"""
        super().__init_subclass__(**kwargs)
        cls.name = cls.__module__.rsplit(".", 1)[-1].upper()

    def __init__(self) -> None:
        assert self.health_check_error_map, f"{type(self).__name__} needs a health_check_error_map"

    @property
    def settings(self):
        return get_settings()

    def classify_health_check_error(self, exc: BaseException) -> ServiceHealth:
        for exc_type, code in self.health_check_error_map:
            if isinstance(exc, exc_type):
                return code
        return ServiceHealth.UNKNOWN

    def probe(self, name: str) -> HealthProbe:
        return HealthProbe(self, name)

    @abstractmethod
    async def health_check(self) -> HealthCheck:
        """Probe dependencies. Failures must raise; the probe classifies them."""
        ...


class Startable(Module):
    """Capability: needs async init (open a connection, etc.)."""

    @abstractmethod
    async def start(self) -> None: ...
