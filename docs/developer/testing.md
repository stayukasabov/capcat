# Testing

## Setup

```bash
cd ~/capcat && source venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
# All unit tests
pytest tests/unit/ -v

# Single file
pytest tests/unit/test_feed_discovery.py -v

# Single test
pytest tests/unit/test_feed_discovery.py::test_validate_rss_feed -v

# With coverage
pytest tests/unit/ --cov=capcat --cov-report=term-missing
```

## Test Structure

```
tests/
└── unit/                    # Unit tests (pytest)
    ├── test_cli.py
    ├── test_feed_discovery.py
    ├── test_feed_parser.py
    ├── test_session_pool.py
    ├── test_bundle_expansion.py
    ├── test_tui_completion.py
    └── ...
```

All tests live under `tests/unit/`. Integration and end-to-end tests are manual (see `docs/troubleshooting.md`).

## TDD Order

1. Write a failing test that describes the expected behavior
2. Run it to confirm it fails (and fails for the right reason)
3. Write the minimal implementation to make it pass
4. Run tests to confirm pass
5. Commit test + implementation together

## Test Design Rules

- One behavior per test function
- Test names describe the behavior: `test_validate_rss_feed`, `test_reject_garbage`
- Use `pytest.raises` for expected exceptions
- Mock at boundaries: HTTP calls, filesystem, `sys.exit`
- Do not mock the production logic under test
- Avoid time-dependent tests; use `tmp_path` fixture for filesystem tests

## Coverage Target

80%+ line coverage on `capcat/` before releasing. Check with:

```bash
pytest tests/unit/ --cov=capcat --cov-report=term-missing
```

## Regression Tests

Each fixed bug must have a corresponding regression test committed before or with the fix. Name the test file after the component: `test_<module>.py`.

Current regression coverage:
- `test_feed_discovery.py` — feedparser-based `validate_feed()` (lxml removed)
- `test_feed_parser.py` — `FeedParserFactory` without lxml
- `test_session_pool.py` — `Accept-Encoding` excludes `br`
- `test_bundle_expansion.py` — `bundle all` / `--all` expands to source IDs
- `test_tui_completion.py` — TUI post-completion screen behavior
