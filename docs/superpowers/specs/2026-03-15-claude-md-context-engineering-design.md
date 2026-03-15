# CLAUDE.md Context Engineering Redesign

**Date:** 2026-03-15
**Status:** Approved
**Scope:** Restructure CLAUDE.md into a slim master controller with a deterministic trigger system routing to a `context-engineering/` folder of thin pointer files.

---

## Problem

Current CLAUDE.md is 429 lines. Every session loads everything regardless of relevance:
- Stale references to deleted files (`run_capcat.py`, `cli.py`, `capcat.py`)
- Wrong paths (`/Users/xpro/`, `~/Projects/capcat/`) predating pipx migration
- Architecture details that belong in `docs/`
- Remotion/Advertising project content (abandoned)
- No mechanism to stay current as the project evolves

Result: context rot, wasted tokens, and Claude making mistakes from stale instructions.

---

## Design

### CLAUDE.md — Master Controller (~60 lines)

Contains only:
1. **Core behavior rules** — Absolute Mode, no emojis, no attribution footers, privacy
2. **Critical constants** — symlink path (`~/capcat`), canonical test command
3. **Git Branching rule** — mandatory, applies universally
4. **Trigger table** — deterministic mapping: task type → context file to read
5. **Meta-rule** — new domain = stop, define trigger + context file before proceeding

### Trigger Table

| Task type | Read before starting |
|-----------|----------------------|
| Any git operation | `context-engineering/git.md` |
| Writing or running tests | `context-engineering/testing.md` |
| Adding/modifying sources | `context-engineering/sources.md` |
| PyPI release / version bump | `context-engineering/release.md` |
| Bug investigation | `context-engineering/debugging.md` |
| Architecture / structural change | `context-engineering/architecture.md` |
| CLI design / new commands | `context-engineering/cli.md` |
| Plan execution | `context-engineering/plan-execution.md` |

### context-engineering/ — Gateway Layer

Each file follows a fixed template:

```
# [Domain]
## Trigger
When: <exact condition>

## Pointers
- Primary: docs/<path>#<section>
- Secondary: docs/<path>#<section>

## Critical rules (behavioral, not in docs)
- <rule>

## Red flags (stop and ask user)
- <condition>
```

Files:
- `git.md` — branching, commits, merge, push, PR workflow
- `testing.md` — pytest, unit structure, TDD order, coverage
- `sources.md` — config-driven vs custom, specialized sources
- `release.md` — semver, PyPI workflow, tagging
- `debugging.md` — investigation order, docs-first rule
- `architecture.md` — package structure, core systems, import paths
- `cli.md` — clig.dev rules, flag conventions
- `plan-execution.md` — branch first, executing-plans skill, worktrees

### Meta-Rule (self-maintenance)

> When adding a new domain, feature area, or behavioral pattern — stop and ask the user to define the trigger rule and create the corresponding context-engineering file before proceeding.

This prevents silent expansion of behavior without updating the routing layer.

---

## Cleanup Scope

### Remove from CLAUDE.md (stale)
- Git Workflow: Synology Drive section (wrong user, wrong paths)
- Architecture Overview diagram (references deleted files)
- Unified Article Processing section (belongs in `docs/architecture/`)
- Common Issues > Wrapper Issues (references deleted `run_capcat.py`)
- Essential Commands using `./capcat` wrapper (stale post-pipx)
- Key Files `sources/active/bundles.yml` (wrong path post-packaging)

### Remove from CLAUDE.md (abandoned project)
- All Remotion / Video / Advertising references

### Relocate (already in docs/ or should be)
- Adding New Sources examples → `docs/source-development.md`
- Testing flow details → `docs/developer/testing.md`
- PyPI publish workflow → `docs/developer/release.md`

### Keep in CLAUDE.md (universal)
- Absolute Mode rules
- Git Branching mandatory rule
- Symlink path constant (`~/capcat`)
- Trigger table
- Meta-rule for new domains
- No emojis, no attribution footers
- Privacy rule (usernames → Anonymous)
- CLI Standards (clig.dev reference)
- Versioning semver rules

---

## Docs/ Gaps to Fill

Before context-engineering files can point to docs/, these docs need to exist or be verified:
- `docs/developer/git-workflow.md`
- `docs/developer/testing.md`
- `docs/developer/release.md`
- `docs/architecture/` (current post-pipx structure)
- `docs/troubleshooting.md` (already exists, verify currency)
- `docs/source-development.md` (already exists, verify currency)

---

## Archive

Current CLAUDE.md backed up to `Archive/CLAUDE.md.2026-03-15.bak` before any changes.

---

## Success Criteria

- CLAUDE.md ≤ 80 lines
- Zero stale references (no deleted files, no wrong paths, no xpro user)
- Zero Remotion/Advertising content
- All 8 context-engineering files created with valid doc pointers
- Meta-rule enforced: new domain triggers user prompt before implementation
- `pytest tests/unit/` still 99/99 after changes (CLAUDE.md changes are non-code)
