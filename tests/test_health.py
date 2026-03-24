"""Tests for HealthAwareRegistry."""

import pytest

from agent_discovery import HealthAwareRegistry
from agent_discovery.health import HealthAwareEntry


class TestHealthAwareRegistry:
    def test_register_returns_health_entry(self):
        reg = HealthAwareRegistry()
        entry = reg.register("svc", lambda: None)
        assert isinstance(entry, HealthAwareEntry)

    def test_healthy_by_default(self):
        reg = HealthAwareRegistry()
        reg.register("svc", lambda: None)
        assert "svc" in reg.available()

    def test_unhealthy_excluded_from_available(self):
        reg = HealthAwareRegistry()
        reg.register("sick", lambda: None, health_check=lambda: False)
        assert "sick" not in reg.available()

    def test_healthy_included_in_available(self):
        reg = HealthAwareRegistry()
        reg.register("ok", lambda: None, health_check=lambda: True)
        assert "ok" in reg.available()

    def test_available_mixed(self):
        reg = HealthAwareRegistry()
        reg.register("a", lambda: None, health_check=lambda: True)
        reg.register("b", lambda: None, health_check=lambda: False)
        reg.register("c", lambda: None)  # no health_check → healthy
        avail = reg.available()
        assert "a" in avail
        assert "b" not in avail
        assert "c" in avail

    def test_health_check_exception_means_unhealthy(self):
        def bad_check():
            raise RuntimeError("network down")

        reg = HealthAwareRegistry()
        reg.register("svc", lambda: None, health_check=bad_check)
        assert "svc" not in reg.available()

    def test_call_available_dispatches(self):
        reg = HealthAwareRegistry()
        reg.register("pay", lambda x: x * 2, tags=["payment"], health_check=lambda: True)
        result = reg.call_available("payment", 5)
        assert result == 10

    def test_call_available_skips_unhealthy(self):
        reg = HealthAwareRegistry()
        reg.register("sick", lambda: "sick", tags=["job"], health_check=lambda: False)
        reg.register("well", lambda: "well", tags=["job"], health_check=lambda: True)
        assert reg.call_available("job") == "well"

    def test_call_available_no_healthy_raises(self):
        reg = HealthAwareRegistry()
        reg.register("svc", lambda: None, tags=["job"], health_check=lambda: False)
        with pytest.raises(RuntimeError, match="No healthy handler"):
            reg.call_available("job")

    def test_call_available_no_tag_match_raises(self):
        reg = HealthAwareRegistry()
        with pytest.raises(RuntimeError):
            reg.call_available("nonexistent-tag")

    def test_is_healthy_method(self):
        e = HealthAwareEntry(name="x", handler=lambda: None, health_check=lambda: True)
        assert e.is_healthy() is True
        e2 = HealthAwareEntry(name="y", handler=lambda: None, health_check=lambda: False)
        assert e2.is_healthy() is False

    def test_to_dict_includes_health_check(self):
        hc = lambda: True
        reg = HealthAwareRegistry()
        entry = reg.register("svc", lambda: None, health_check=hc)
        d = entry.to_dict()
        assert "health_check" in d
        assert d["health_check"] is hc
