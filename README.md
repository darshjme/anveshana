# agent-discovery

> Service discovery and agent registry for multi-agent systems. Zero dependencies. Python 3.10+.

[![PyPI version](https://img.shields.io/pypi/v/agent-discovery)](https://pypi.org/project/agent-discovery/)
[![Python](https://img.shields.io/pypi/pyversions/agent-discovery)](https://pypi.org/project/agent-discovery/)

## Problem

In multi-agent systems, agents need to find each other:
- *"Which agent handles payments?"*
- *"Which agent is currently available?"*
- *"Which LLM provider has the lowest latency right now?"*

Hard-coding addresses couples everything. `agent-discovery` gives you a lightweight registry to decouple discovery from execution.

## Install

```bash
pip install agent-discovery
```

## Quick Start — Multi-Agent Dispatch

```python
from agent_discovery import AgentRegistry, HealthAwareRegistry
from agent_discovery.decorators import register, get_global_registry

# ── 1. Global @register decorator ─────────────────────────────────────────
@register("payment-agent", tags=["payment", "billing"])
def process_payment(amount: float, currency: str = "USD") -> dict:
    return {"status": "ok", "amount": amount, "currency": currency}

@register("shipping-agent", tags=["shipping", "logistics"])
def process_shipping(order_id: str) -> dict:
    return {"status": "dispatched", "order": order_id}

# Dispatch by name via the global registry
registry = get_global_registry()
result = registry.call("payment-agent", amount=99.99)
print(result)  # {'status': 'ok', 'amount': 99.99, 'currency': 'USD'}

# ── 2. Tag-based discovery ─────────────────────────────────────────────────
billing_agents = registry.find_by_tag("billing")
print([e.name for e in billing_agents])  # ['payment-agent']

# ── 3. Health-aware registry ───────────────────────────────────────────────
import random

health_reg = HealthAwareRegistry()

health_reg.register(
    "openai-router",
    handler=lambda prompt: f"[openai] {prompt}",
    tags=["llm"],
    health_check=lambda: True,          # always healthy
)
health_reg.register(
    "anthropic-router",
    handler=lambda prompt: f"[anthropic] {prompt}",
    tags=["llm"],
    health_check=lambda: random.random() > 0.5,  # flaky
)
health_reg.register(
    "offline-router",
    handler=lambda prompt: f"[offline] {prompt}",
    tags=["llm"],
    health_check=lambda: False,         # always down
)

# See which LLM providers are healthy right now
print(health_reg.available())  # e.g. ['openai-router', 'anthropic-router']

# Call the *first* healthy LLM handler — automatic failover
response = health_reg.call_available("llm", "What is 2+2?")
print(response)  # '[openai] What is 2+2?'
```

## API Reference

### `RegistryEntry`

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique name |
| `handler` | `Callable` | The callable to dispatch to |
| `tags` | `list[str]` | Searchable tags |
| `metadata` | `dict` | Arbitrary metadata |
| `registered_at` | `float` | Unix timestamp |

`.to_dict()` → serialisable dictionary.

---

### `AgentRegistry`

| Method | Description |
|--------|-------------|
| `register(name, handler, tags, metadata)` | Register a handler |
| `unregister(name)` | Remove an entry |
| `get(name)` | Fetch entry by name (or `None`) |
| `find_by_tag(tag)` | All entries with the given tag |
| `find_by_tags(tags, match_all=False)` | ANY or ALL tag match |
| `list_all()` | List of all names |
| `call(name, *args, **kwargs)` | Dispatch to handler |

---

### `HealthAwareRegistry` *(extends AgentRegistry)*

| Method | Description |
|--------|-------------|
| `register(..., health_check=None)` | Register with optional health check |
| `available()` | Names of currently healthy entries |
| `call_available(tag, *args, **kwargs)` | Dispatch to first healthy handler with tag |

---

### `@register` decorator

```python
from agent_discovery.decorators import register

@register("my-agent", tags=["search"], metadata={"version": "1"})
def my_agent(query: str) -> str:
    ...
```

Registers in the process-level global `AgentRegistry` (retrievable via `get_global_registry()`).

## License

MIT
