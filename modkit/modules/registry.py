"""Generic, filesystem-driven discovery for one module category."""
from __future__ import annotations

import functools
import importlib
import inspect
import logging
import pathlib
from typing import Generic, TypeVar

from modkit.interfaces import Module

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Module)


class Registry(Generic[T]):
    """Discovers adapters in `modules/<category>/` and returns them typed as `T`.

    Exactly one adapter per category is active. You cannot have two caches.

    :param interface: the port this registry serves (its ``category`` picks the folder)
    :param backend: name of the adapter to activate, usually read straight from settings.
        ``None`` means "not configured yet" - the registry can still be imported and
        inspected (``available``), it just refuses to resolve a default.
    """

    def __init__(self, interface: type[T], backend: str | None) -> None:
        self._interface = interface
        self._category = interface.category
        self._backend = backend
        folder = pathlib.Path(__file__).parent / self._category
        self._available = sorted(self._discover(folder)) if folder.is_dir() else []

    def _discover(self, folder: pathlib.Path) -> list[str]:
        """Return the module names in ``folder``; a filename *is* a module name."""
        names = []
        for f in folder.iterdir():
            if f.suffix != ".py" or f.stem.startswith("_"):
                continue
            if not f.stem.isidentifier():
                raise ValueError(f"{f.name!r} in {self._category}/ is not a valid module name")
            names.append(f.stem.upper())
        return names

    @functools.cache
    def get_class(self, name: str) -> type[T]:
        """Import `modules/<category>/<name>.py` and return its `interface` subclass."""
        mod = importlib.import_module(f"{__package__}.{self._category}.{name.lower()}")
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if (issubclass(cls, self._interface)
                    and cls is not self._interface
                    and cls.__module__ == mod.__name__):
                return cls
        raise LookupError(f"no {self._interface.__name__} implementation in {self._category}/{name}")

    @functools.cache
    def __getitem__(self, name: str) -> T:
        return self.get_class(name=name)()

    @property
    def category(self) -> str:
        return self._category

    @property
    def available(self) -> list[str]:
        """Names discovered in the category folder, e.g. `["MEMORY", "REDIS"]`."""
        return list(self._available)

    @property
    def DEFAULT(self) -> str:
        """Name of the active adapter, resolved from the backend given at construction."""
        if self._backend is None:
            raise RuntimeError(
                f"{self._category} must be selected in settings (one of {self._available})"
            )
        name = self._backend.upper()
        if name not in self._available:
            raise LookupError(
                f"{self._backend!r} is not a discovered {self._category} module {self._available}"
            )
        return name

    @property
    def default(self) -> T:
        return self[self.DEFAULT]
