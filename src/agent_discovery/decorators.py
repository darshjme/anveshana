"""@register decorator — auto-registers functions in the global registry."""

from __future__ import annotations

from typing import Callable

from .registry import AgentRegistry

_global_registry = AgentRegistry()


def get_global_registry() -> AgentRegistry:
    """Return the module-level global registry."""
    return _global_registry


def register(
    name: str,
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> Callable:
    """Decorator that registers the decorated function in the global registry.

    Usage::

        @register("payment-handler", tags=["payment", "billing"])
        def handle_payment(amount: float) -> str:
            return f"processed ${amount}"
    """
    def decorator(fn: Callable) -> Callable:
        _global_registry.register(name=name, handler=fn, tags=tags, metadata=metadata)
        return fn  # return the original function unchanged

    return decorator
