"""HealthAwareRegistry — extends AgentRegistry with health-check support."""

from __future__ import annotations

from typing import Any, Callable

from .registry import AgentRegistry, RegistryEntry


class HealthAwareEntry(RegistryEntry):
    """RegistryEntry that also stores an optional health-check callable."""

    def __init__(self, *args: Any, health_check: Callable[[], bool] | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.health_check: Callable[[], bool] | None = health_check

    def is_healthy(self) -> bool:
        """Return True when no health_check is supplied, or when it returns True."""
        if self.health_check is None:
            return True
        try:
            return bool(self.health_check())
        except Exception:
            return False

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["health_check"] = self.health_check
        return d


class HealthAwareRegistry(AgentRegistry):
    """Agent registry with integrated health-check support."""

    # Override register so that an optional health_check can be attached.
    def register(  # type: ignore[override]
        self,
        name: str,
        handler: Callable,
        tags: list[str] | None = None,
        metadata: dict | None = None,
        health_check: Callable[[], bool] | None = None,
    ) -> HealthAwareEntry:
        if not callable(handler):
            raise TypeError(f"handler must be callable, got {type(handler)!r}")
        entry = HealthAwareEntry(
            name=name,
            handler=handler,
            tags=tags,
            metadata=metadata,
            health_check=health_check,
        )
        self._entries[name] = entry
        return entry

    def available(self) -> list[str]:
        """Return names of all currently *healthy* entries."""
        return [
            name
            for name, entry in self._entries.items()
            if isinstance(entry, HealthAwareEntry) and entry.is_healthy()
        ]

    def call_available(self, tag: str, *args: Any, **kwargs: Any) -> Any:
        """Dispatch to the first healthy handler that carries *tag*.

        Raises RuntimeError if no healthy handler is found for the tag.
        """
        candidates = self.find_by_tag(tag)
        for entry in candidates:
            if isinstance(entry, HealthAwareEntry) and entry.is_healthy():
                return entry.handler(*args, **kwargs)
        raise RuntimeError(
            f"No healthy handler found for tag {tag!r}"
        )
