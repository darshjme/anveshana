"""Tests for AgentRegistry and RegistryEntry."""

import time
import pytest

from agent_discovery import AgentRegistry, RegistryEntry


# ---------------------------------------------------------------------------
# RegistryEntry
# ---------------------------------------------------------------------------

class TestRegistryEntry:
    def test_basic_fields(self):
        handler = lambda: "ok"
        entry = RegistryEntry(name="svc", handler=handler, tags=["a", "b"], metadata={"k": 1})
        assert entry.name == "svc"
        assert entry.handler is handler
        assert entry.tags == ["a", "b"]
        assert entry.metadata == {"k": 1}
        assert isinstance(entry.registered_at, float)

    def test_defaults(self):
        entry = RegistryEntry(name="x", handler=lambda: None)
        assert entry.tags == []
        assert entry.metadata == {}

    def test_to_dict_keys(self):
        entry = RegistryEntry(name="x", handler=lambda: None)
        d = entry.to_dict()
        assert set(d.keys()) == {"name", "handler", "tags", "metadata", "registered_at"}

    def test_registered_at_is_recent(self):
        before = time.time()
        entry = RegistryEntry(name="x", handler=lambda: None)
        after = time.time()
        assert before <= entry.registered_at <= after

    def test_tags_are_copied(self):
        tags = ["a"]
        entry = RegistryEntry(name="x", handler=lambda: None, tags=tags)
        tags.append("b")
        assert entry.tags == ["a"]  # mutation doesn't affect entry

    def test_metadata_is_copied(self):
        meta = {"a": 1}
        entry = RegistryEntry(name="x", handler=lambda: None, metadata=meta)
        meta["b"] = 2
        assert entry.metadata == {"a": 1}


# ---------------------------------------------------------------------------
# AgentRegistry — registration
# ---------------------------------------------------------------------------

class TestAgentRegistryRegistration:
    def test_register_returns_entry(self):
        reg = AgentRegistry()
        entry = reg.register("svc", lambda: None)
        assert isinstance(entry, RegistryEntry)

    def test_register_non_callable_raises(self):
        reg = AgentRegistry()
        with pytest.raises(TypeError):
            reg.register("svc", "not-callable")  # type: ignore

    def test_register_overwrites(self):
        reg = AgentRegistry()
        reg.register("svc", lambda: 1)
        reg.register("svc", lambda: 2)
        assert reg.call("svc") == 2

    def test_unregister(self):
        reg = AgentRegistry()
        reg.register("svc", lambda: None)
        reg.unregister("svc")
        assert reg.get("svc") is None

    def test_unregister_missing_raises(self):
        reg = AgentRegistry()
        with pytest.raises(KeyError):
            reg.unregister("ghost")

    def test_len(self):
        reg = AgentRegistry()
        assert len(reg) == 0
        reg.register("a", lambda: None)
        reg.register("b", lambda: None)
        assert len(reg) == 2

    def test_contains(self):
        reg = AgentRegistry()
        reg.register("a", lambda: None)
        assert "a" in reg
        assert "z" not in reg


# ---------------------------------------------------------------------------
# AgentRegistry — lookup
# ---------------------------------------------------------------------------

class TestAgentRegistryLookup:
    def test_get_existing(self):
        reg = AgentRegistry()
        reg.register("svc", lambda: None, tags=["x"])
        entry = reg.get("svc")
        assert entry is not None
        assert entry.name == "svc"

    def test_get_missing_returns_none(self):
        reg = AgentRegistry()
        assert reg.get("nope") is None

    def test_list_all(self):
        reg = AgentRegistry()
        reg.register("a", lambda: None)
        reg.register("b", lambda: None)
        assert sorted(reg.list_all()) == ["a", "b"]

    def test_find_by_tag(self):
        reg = AgentRegistry()
        reg.register("pay", lambda: None, tags=["payment", "billing"])
        reg.register("ship", lambda: None, tags=["shipping"])
        results = reg.find_by_tag("payment")
        assert len(results) == 1
        assert results[0].name == "pay"

    def test_find_by_tag_no_match(self):
        reg = AgentRegistry()
        reg.register("svc", lambda: None, tags=["a"])
        assert reg.find_by_tag("z") == []

    def test_find_by_tags_any(self):
        reg = AgentRegistry()
        reg.register("a", lambda: None, tags=["x", "y"])
        reg.register("b", lambda: None, tags=["y", "z"])
        reg.register("c", lambda: None, tags=["z"])
        results = reg.find_by_tags(["x", "z"], match_all=False)
        names = {e.name for e in results}
        assert names == {"a", "b", "c"}

    def test_find_by_tags_all(self):
        reg = AgentRegistry()
        reg.register("a", lambda: None, tags=["x", "y"])
        reg.register("b", lambda: None, tags=["y"])
        results = reg.find_by_tags(["x", "y"], match_all=True)
        assert len(results) == 1
        assert results[0].name == "a"

    def test_find_by_tags_empty_returns_all(self):
        reg = AgentRegistry()
        reg.register("a", lambda: None)
        reg.register("b", lambda: None)
        assert len(reg.find_by_tags([])) == 2


# ---------------------------------------------------------------------------
# AgentRegistry — dispatch
# ---------------------------------------------------------------------------

class TestAgentRegistryCall:
    def test_call_handler(self):
        reg = AgentRegistry()
        reg.register("add", lambda x, y: x + y)
        assert reg.call("add", 3, 4) == 7

    def test_call_with_kwargs(self):
        reg = AgentRegistry()
        reg.register("greet", lambda name="world": f"Hello {name}")
        assert reg.call("greet", name="Alice") == "Hello Alice"

    def test_call_missing_raises(self):
        reg = AgentRegistry()
        with pytest.raises(KeyError):
            reg.call("ghost")
