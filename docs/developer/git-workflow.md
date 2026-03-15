# Git Workflow

## Branching Model

**Never commit directly to `main`.** All work happens on a feature branch.

Branch naming:
- `feat/<name>` — new feature
- `fix/<name>` — bug fix
- `test/<name>` — tests only
- `refactor/<name>` — refactoring, no behavior change
- `docs/<name>` — documentation only

```bash
git checkout -b feat/my-feature
```

## Commit Conventions

- One logical change per commit
- Imperative mood: `add`, `fix`, `remove`, `update`, not `added` or `adds`
- Prefix: `feat:`, `fix:`, `test:`, `refactor:`, `docs:`, `bump:`
- Keep subject line under 72 characters
- No Claude Code attribution footers (`Co-Authored-By`, `🤖 Generated with`)

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
6. Merge locally or via GitHub — delete branch after merge

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

## SSH Authentication (Required)

All git operations must use SSH, not HTTPS. HTTPS requires a password on every push.

### Check current remote

```bash
git remote -v
```

If it shows `https://github.com/...`, switch it to SSH:

```bash
git remote set-url origin git@github.com:stayukasabov/capcat.git
```

### Set up SSH key (one-time)

```bash
# Generate key (skip if ~/.ssh/id_ed25519 already exists)
ssh-keygen -t ed25519 -C "your@email.com"

# Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub | pbcopy
```

Paste it in GitHub → Settings → SSH and GPG keys → New SSH key.

### Verify

```bash
ssh -T git@github.com
# Expected: Hi stayukasabov! You've successfully authenticated...
```

After this, all pushes work without a password.

## Working with the Synology Symlink

The repo is symlinked: `~/capcat` → Synology Drive path.

Always use `~/capcat/` in bash commands — never the raw Synology path.
