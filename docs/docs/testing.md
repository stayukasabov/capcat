---
layout: default
render_with_liquid: false
---

# Testing Guide

## Running Tests

```bash
cd ~/capcat && source venv/bin/activate

# Unit tests (fast, no network)
pytest tests/unit/ -q

# Single test file
pytest tests/unit/test_lb_fetch_comments_rate_limit.py -v

# Acceptance tests (requires live network)
pytest tests/acceptance/ -q
```

Current suite: 767 unit tests.

## Test Structure

```
tests/
  unit/           ← pure unit tests, mocked network
  acceptance/     ← live fetch tests against real sources
    tmp/          ← gitignored temporary output
    results/      ← gitignored results
```

## Unit Test Conventions

- Mock all HTTP with `unittest.mock.patch` or `MagicMock`
- No real network calls in unit tests
- Test files: `tests/unit/test_<module_name>.py`
- One `test_` function per behaviour, not per method

## Acceptance Tests (Chain F)

Run after every fix merged to main - mandatory, no exceptions:

```bash
pytest tests/acceptance/ -q
```

Do not push to remote until Chain F passes clean.

## TDD Workflow

Red → Green → Refactor:

1. Write a failing test that describes the behaviour
2. Run it - confirm it fails for the right reason
3. Implement the minimum code to pass
4. Refactor
5. All 767 unit tests must still pass

## Adding Tests for a New Source Fix

Patch at the source module level, not the import level:

```python
from unittest.mock import patch, MagicMock

def test_fetch_enforces_rate_limit(tmp_path):
    with patch("capcat.sources.builtin.custom.lb.source.get_ethical_manager") as mock_mgr:
        mock_manager = MagicMock()
        mock_mgr.return_value = mock_manager
        # ... assert rate limit called before session.get
```

## Coverage

```bash
pytest tests/unit/ --cov=capcat --cov-report=term-missing -q
```
