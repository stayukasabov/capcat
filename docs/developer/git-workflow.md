# Git Workflow

## Branching Model

**Never commit directly to `main`.** All work happens on a feature branch.

Branch naming:
- `feat/<name>` - new feature
- `fix/<name>` - bug fix
- `test/<name>` - tests only
- `refactor/<name>` - refactoring, no behavior change
- `docs/<name>` - documentation only

```bash
git checkout -b feat/my-feature
```

## Commit Conventions

- One logical change per commit
- Imperative mood: `add`, `fix`, `remove`, `update`, not `added` or `adds`
- Prefix: `feat:`, `fix:`, `test:`, `refactor:`, `docs:`, `bump:`
- Keep subject line under 72 characters


Examples:
```
feat: add IEEE source with RSS feed
fix: exclude br from Accept-Encoding header
test: regression tests for bundle expansion
docs: rewrite developer guide for pipx install
bump: version to 1.0.31
```

## PR Process

1. Branch from `main`
2. Make changes, commit frequently
3. Push branch: `git push -u origin feat/my-feature`
4. Open PR against `main` via `gh pr create`
5. All tests must pass before merge
6. Merge locally or via GitHub - delete branch after merge

## Push Rules

- Never force-push `main`
- Never skip hooks (`--no-verify`) without explicit reason
- Never amend a commit that has already been pushed (create a new commit instead)

## Tagging and Releases

Tag format: `v1.2.3`

```bash
git tag v1.0.31
git push origin main && git push origin v1.0.31
```

Pushing a `v*` tag triggers GitHub Actions → PyPI publish automatically.
See `docs/developer/release.md` for full release checklist.

## GitHub Authentication

GitHub remote uses HTTPS. Credentials are stored in macOS Keychain after the first successful push - no password prompt on subsequent pushes.

```bash
git remote -v
# must show: https://github.com/stayukasabov/capcat.git

# If wrong, restore:
git remote set-url origin https://github.com/stayukasabov/capcat.git
```

Credential helper (set once per machine):
```bash
git config --global credential.helper osxkeychain
```


