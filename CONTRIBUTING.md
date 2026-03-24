# Contributing

Thank you for considering a contribution to **agent-discovery**!

## Development Setup

```bash
git clone https://github.com/example/agent-discovery
cd agent-discovery
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Code Style

- Follow PEP 8.
- Add type annotations to all public symbols.
- Keep zero runtime dependencies.

## Pull Requests

1. Fork the repo and create a feature branch.
2. Add or update tests for any changed behaviour.
3. Ensure `pytest` passes with no failures.
4. Submit a PR with a clear description of the change.

## Reporting Bugs

Open a GitHub issue with a minimal reproducible example.
