# runtime-core (Python)

Deterministic backend engines for the AI Game Mathematics Assistant.

**Status:** Phase M0 scaffold — package layout and tooling only.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
cd packages/runtime_core
uv sync --group dev
```

## Development

```bash
# Tests
uv run pytest

# Coverage
uv run pytest --cov=runtime_core --cov-report=term-missing

# Lint and format
uv run ruff check .
uv run ruff format --check .
uv run black --check .
uv run mypy runtime_core
```

## Package layout

| Package | Responsibility |
|---------|----------------|
| `runtime_core.domain` | Canonical `GameVersion` and domain types |
| `runtime_core.validation` | Validation Engine (M1) |
| `runtime_core.runtime` | Runtime Core execution (M2) |
| `runtime_core.plugins` | Built-in feature plugins |
| `runtime_core.simulation` | Simulation Engine orchestration (M3) |
| `runtime_core.mathematics` | RTP, volatility, statistical aggregation (M3) |
| `runtime_core.common` | Shared utilities, logging, repository paths |

Golden fixtures live at repository root: `tests/golden/`.

## Related documents

- [CURSOR_RULES.md](../../docs/CURSOR_RULES.md)
- [ADR-007 Backend Language: Python](../../docs/adr/ADR-007-backend-language-python.md)
