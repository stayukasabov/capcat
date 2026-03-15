# CLAUDE.md

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

## Git Branching (MANDATORY)

Never commit directly to `main`. All work — including single-file changes — happens on a feature branch.

```bash
git checkout -b feat/my-feature   # or fix/, test/, refactor/, docs/
```

Branch, implement, PR, merge. No exceptions.

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

## Subagent Rules

- Never dispatch a subagent to write fully-specified code — write files directly using Write/Edit tools
- Subagents only for tasks requiring research, judgment, or open-ended exploration
