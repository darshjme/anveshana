"""Tests for the @register decorator and global registry."""

import pytest

# Each test module import creates a fresh module state — but the global registry
# is module-level, so we reset it between tests using monkeypatch.

from agent_discovery import decorators as dec_module
from agent_discovery.decorators import get_global_registry
from agent_discovery.registry import AgentRegistry


@pytest.fixture(autouse=True)
def reset_global_registry(monkeypatch):
    """Provide a fresh global registry for every test."""
    fresh = AgentRegistry()
    monkeypatch.setattr(dec_module, "_global_registry", fresh)
    # Also patch the module-level reference used by the decorator
    yield
    # cleanup automatic via monkeypatch


class TestRegisterDecorator:
    def test_decorator_registers_function(self):
        from agent_discovery.decorators import register

        @register("test-handler")
        def my_handler():
            return "hello"

        reg = get_global_registry()
        assert "test-handler" in reg

    def test_decorator_with_tags(self):
        from agent_discovery.decorators import register

        @register("pay", tags=["payment", "billing"])
        def pay_fn(amount):
            return amount

        reg = get_global_registry()
        entry = reg.get("pay")
        assert entry is not None
        assert "payment" in entry.tags
        assert "billing" in entry.tags

    def test_decorator_with_metadata(self):
        from agent_discovery.decorators import register

        @register("svc", metadata={"version": "2.0"})
        def svc_fn():
            return "ok"

        reg = get_global_registry()
        entry = reg.get("svc")
        assert entry.metadata == {"version": "2.0"}

    def test_decorated_function_still_callable(self):
        from agent_discovery.decorators import register

        @register("add-fn")
        def add(a, b):
            return a + b

        assert add(1, 2) == 3

    def test_decorator_dispatches_via_registry(self):
        from agent_discovery.decorators import register

        @register("greet", tags=["greeting"])
        def greet(name):
            return f"Hi {name}"

        reg = get_global_registry()
        assert reg.call("greet", "Alice") == "Hi Alice"

    def test_get_global_registry_type(self):
        reg = get_global_registry()
        assert isinstance(reg, AgentRegistry)
