"""Core registry: AgentRegistry and RegistryEntry."""

from __future__ import annotations

import time
from typing import Any, Callable


class RegistryEntry:
    """Immutable-ish record stored in the registry."""

    def __init__(
        self,
        name: str,
        handler: Callable,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> None:
        self.name = name
        self.handler = handler
        self.tags: list[str] = list(tags) if tags else []
        self.metadata: dict = dict(metadata) if metadata else {}
        self.registered_at: float = time.time()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "handler": self.handler,
            "tags": self.tags,
            "metadata": self.metadata,
            "registered_at": self.registered_at,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"RegistryEntry(name={self.name!r}, tags={self.tags!r})"


class AgentRegistry:
    """Central agent/service registry."""

    def __init__(self) -> None:
        self._entries: dict[str, RegistryEntry] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        handler: Callable,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> RegistryEntry:
        """Register an agent/service handler under *name*."""
        if not callable(handler):
            raise TypeError(f"handler must be callable, got {type(handler)!r}")
        entry = RegistryEntry(name=name, handler=handler, tags=tags, metadata=metadata)
        self._entries[name] = entry
        return entry

    def unregister(self, name: str) -> None:
        """Remove a previously registered entry.  Raises KeyError if not found."""
        if name not in self._entries:
            raise KeyError(f"No entry registered under {name!r}")
        del self._entries[name]

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, name: str) -> RegistryEntry | None:
        """Return the entry for *name*, or None if not registered."""
        return self._entries.get(name)

    def find_by_tag(self, tag: str) -> list[RegistryEntry]:
        """Return all entries that carry *tag*."""
        return [e for e in self._entries.values() if tag in e.tags]

    def find_by_tags(
        self, tags: list[str], match_all: bool = False
    ) -> list[RegistryEntry]:
        """Return entries matching *tags*.

        Parameters
        ----------
        tags:
            Tags to search for.
        match_all:
            If True, an entry must carry **all** supplied tags.
            If False (default), an entry must carry **at least one**.
        """
        if not tags:
            return list(self._entries.values())
        tag_set = set(tags)
        results: list[RegistryEntry] = []
        for entry in self._entries.values():
            entry_tags = set(entry.tags)
            if match_all:
                if tag_set <= entry_tags:
                    results.append(entry)
            else:
                if tag_set & entry_tags:
                    results.append(entry)
        return results

    def list_all(self) -> list[str]:
        """Return a list of all registered entry names."""
        return list(self._entries.keys())

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def call(self, entry_name: str, *args: Any, **kwargs: Any) -> Any:
        """Dispatch a call to the handler registered under *entry_name*."""
        entry = self._entries.get(entry_name)
        if entry is None:
            raise KeyError(f"No entry registered under {entry_name!r}")
        return entry.handler(*args, **kwargs)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, name: str) -> bool:
        return name in self._entries
