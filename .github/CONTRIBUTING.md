# Contributing to Capcat

## Getting started

```bash
git clone https://github.com/<owner>/capcat
cd capcat
pip install -e ".[dev]"
```

## Running tests

```bash
pytest tests/ -x -q
```

## Code style

This project uses [ruff](https://docs.astral.sh/ruff/) (line length 79).

```bash
ruff check capcat/
ruff format capcat/
```

## Submitting changes

1. Fork the repo and create a branch from `main`.
2. Add tests for any new behaviour.
3. Ensure `pytest` and `ruff check` pass locally.
4. Open a pull request - the CI suite must be green before merge.

## Reporting bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

## Requesting features

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).
