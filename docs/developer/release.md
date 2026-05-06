# Release Process

## Version Scheme

Semver: `MAJOR.MINOR.PATCH`

- **patch** - bug fixes, no new behavior (e.g. `1.0.30` → `1.0.31`)
- **minor** - new features, backwards compatible (e.g. `1.0.x` → `1.1.0`)
- **major** - breaking changes (e.g. `1.x.x` → `2.0.0`)

Do not publish on every commit. Batch related changes, then release when the set is meaningful and tested.

## Pre-Release Checklist

- [ ] All tests pass: `pytest tests/unit/ -v`
- [ ] No linting errors
- [ ] `CHANGELOG` or commit log reflects all changes since last tag
- [ ] Feature branch merged to `main`

## Release Steps

### 1. Bump version

Edit `capcat/__init__.py`:
```python
__version__ = "1.0.31"
```

### 2. Commit

```bash
git add capcat/__init__.py
git commit -m "bump: version to 1.0.31"
```

### 3. Tag

```bash
git tag v1.0.31
```

### 4. Push branch and tag

```bash
git push origin main && git push origin v1.0.31
```

GitHub Actions detects the `v*` tag and publishes to PyPI automatically.

## Verify Publish

After ~2 minutes:

```bash
# macOS (pipx)
pipx upgrade capcat
capcat --version

# Linux / other
pip install --upgrade capcat
capcat --version
```

## Tagging Conventions

- Tags are always `v` + semver: `v1.0.31`, `v1.1.0`, `v2.0.0`
- Never push a tag without a corresponding version bump commit
- Never reuse or move a tag after it's been pushed
