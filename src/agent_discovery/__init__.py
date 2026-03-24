"""agent-discovery: Service discovery and agent registry for multi-agent systems."""

from .registry import AgentRegistry, RegistryEntry
from .health import HealthAwareRegistry
from .decorators import register, get_global_registry

__all__ = [
    "AgentRegistry",
    "RegistryEntry",
    "HealthAwareRegistry",
    "register",
    "get_global_registry",
]

__version__ = "1.0.0"
