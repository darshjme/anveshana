# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-24

### Added
- `AgentRegistry` — core in-memory agent/service registry.
- `RegistryEntry` — immutable record with `name`, `handler`, `tags`, `metadata`, `registered_at` fields.
- `HealthAwareRegistry` — extends `AgentRegistry` with per-entry health checks.
- `@register` decorator — auto-registers functions in the global process-level registry.
- `find_by_tags(tags, match_all=False)` — flexible ANY/ALL tag matching.
- `call_available(tag, ...)` — automatic failover to first healthy handler.
- Zero runtime dependencies (Python stdlib only).
- Full pytest test suite (22+ tests).
