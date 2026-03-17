# CLAUDE.md

# Global Claude Instructions

## File Paths
- Always output **absolute file paths** when referencing saved files, plans, reports, or any created/modified files.
- Never use relative paths in output messages (e.g. use `/Users/xmac/project/docs/plan.md` not `docs/plan.md`).
- This ensures file links are clickable in WezTerm via `Cmd+Click`.

## Absolute Mode

- No emojis, filler, hype, soft asks, conversational transitions, or call-to-action appendixes
- Blunt, directive phrasing — no tone-matching, no sentiment-boosting
- No questions, offers, suggestions, motivational content
- No Claude Code attribution footers (`Co-Authored-By`, `🤖 Generated with`)
- Terminate reply immediately after delivering info — no closures
- Usernames → "Anonymous" in all output — never store personal data

## Critical Constants

- Symlink: `~/capcat` → full Synology Drive project path — use for all bash commands
- Never `cd` into the raw Synology path
- Canonical test command: `cd ~/capcat && source venv/bin/activate && pytest tests/unit/ -v`

## Git Authentication

GitHub remote uses HTTPS. macOS Keychain stores credentials — no password after first push.

```bash
git remote -v  # must show https://github.com/stayukasabov/capcat.git
git config --global credential.helper osxkeychain  # set once per machine
```

The `id_ed25519` SSH key is for the VPS (`stayux-vps`), not GitHub. Use rsync to deploy to VPS for Ubuntu/pipx testing. See `docs/developer/git-workflow.md#vps-deployment-rsync`.

## Git Branching (MANDATORY)

Never commit directly to `main`. All work — including single-file changes — happens on a feature branch.

```bash
git checkout -b feat/my-feature   # or fix/, test/, refactor/, docs/
```

Branch, implement, PR, merge. No exceptions.

## Git Worktrees (MANDATORY for multi-step development)

All plan execution and multi-step feature work must use a git worktree for isolation. Never implement a plan directly in the main working tree.

```bash
# Create worktree for a feature branch
cd ~/capcat && git worktree add ../capcat-feat-my-feature -b feat/my-feature

# Work inside the worktree
cd ~/capcat-feat-my-feature

# Remove worktree after merging/PR (Options 1, 2, 4 of finishing-a-development-branch)
git worktree remove ../capcat-feat-my-feature
```

- One worktree per feature branch
- Worktree path: `~/capcat-<branch-slug>` (e.g. `~/capcat-fix-double-nesting`)
- Always remove the worktree after the branch is merged or discarded
- Use the `superpowers:using-git-worktrees` skill when setting up a worktree

## Versioning

Semver: patch = bug fix | minor = new feature | major = breaking change.
Do not tag/publish on every commit. Tag format: `v1.2.3`.

## Trigger Table

Read the listed file(s) **before starting** any work in that domain.

| Task type | Read before starting |
|-----------|----------------------|
| Any git operation | `context-engineering/git.md` |
| Writing or running tests | `context-engineering/testing.md` |
| Adding/modifying sources | `context-engineering/sources.md` |
| PyPI release / version bump | `context-engineering/release.md` |
| Bug investigation | `context-engineering/debugging.md` |
| Architecture / structural change | `context-engineering/architecture.md` |
| CLI design / new commands | `context-engineering/cli.md` |
| Plan execution | `context-engineering/plan-execution.md` (load first, then domain files) |

**Multi-trigger rule:** When multiple triggers match, load ALL matching files.
`plan-execution.md` always loads first when plan execution is in scope.
Example: TDD bug fix → load `plan-execution.md`, then `debugging.md`, then `testing.md`.

## PRIORITY RULE: Task Execution Protocol

Before starting any multi-step task:
1. List all steps in order
2. Show clear task breakdown
3. Execute sequentially
4. Report completion status

## Meta-Rule (self-maintenance)

When adding a new domain, feature area, or behavioral pattern — stop and ask the user to define the trigger rule and create the corresponding `context-engineering/` file before proceeding.

## Context Engineering: Local Only (MANDATORY)

The `context-engineering/`, `docs/superpowers/`, and `Archive/` directories are **local-only**.

- Never `git add` any file from these directories
- Never commit them — they are in `.gitignore` for this reason
- They exist only on the working machine to guide Claude; they must never appear in the remote repo or its history
- If you accidentally stage one, run `git rm --cached <file>` before committing

## Session Reports

Use the `/save-report` skill when the user says "Save Report" or `/save-report`.

- Reports are saved to `Reports/YYYY-MM-DD_HH-MM.md` in the project root
- The `Reports/` directory is created on first use
- Content is inferred from the conversation — goals, accomplishments, files changed, open TODOs, resume context
- `Reports/` is local-only — never `git add` any file from it

## Subagent Rules

- Never dispatch a subagent to write fully-specified code — write files directly using Write/Edit tools
- Subagents only for tasks requiring research, judgment, or open-ended exploration
