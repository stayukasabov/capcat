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

### CLAUDE.md — Master Controller (~60-80 lines)

Contains only:
1. **Core behavior rules** — Absolute Mode, no emojis, no attribution footers, privacy
2. **Critical constants** — symlink path (`~/capcat`), canonical test command
3. **Git Branching rule** — mandatory, applies universally
4. **Trigger table** — deterministic mapping: task type → context file(s) to read
5. **Meta-rule** — new domain = stop, define trigger + context file before proceeding
6. **Multi-trigger rule** — when multiple triggers match, load ALL matching files

### Trigger Table

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Task type</th>
      <th>Read before starting</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Any git operation</td>
      <td><code>context-engineering/git.md</code></td>
    </tr>
    <tr>
      <td>Writing or running tests</td>
      <td><code>context-engineering/testing.md</code></td>
    </tr>
    <tr>
      <td>Adding/modifying sources</td>
      <td><code>context-engineering/sources.md</code></td>
    </tr>
    <tr>
      <td>PyPI release / version bump</td>
      <td><code>context-engineering/release.md</code></td>
    </tr>
    <tr>
      <td>Bug investigation</td>
      <td><code>context-engineering/debugging.md</code></td>
    </tr>
    <tr>
      <td>Architecture / structural change</td>
      <td><code>context-engineering/architecture.md</code></td>
    </tr>
    <tr>
      <td>CLI design / new commands</td>
      <td><code>context-engineering/cli.md</code></td>
    </tr>
    <tr>
      <td>Plan execution</td>
      <td><code>context-engineering/plan-execution.md</code> (load first, then domain files)</td>
    </tr>
  </tbody>
</table>
</div>

**Precedence rule:** When multiple triggers match, load ALL matching files.
`plan-execution.md` always loads first when plan execution is in scope.
Example: TDD bug fix → load `plan-execution.md`, then `debugging.md`, then `testing.md`.

### context-engineering/ — Gateway Layer

Each file follows this fixed template (all sections required; use "None" if empty):

```markdown
# [Domain]

## Trigger
When: <exact condition that causes this file to be read>

## Pointers
- Primary: `docs/<path>` — <one-line description of what to find there>
- Secondary: `docs/<path>` — <one-line description> (if applicable)

## Critical rules
Rules that are behavioral and not captured in the docs above.
- <rule> (or "None")

## Red flags
Stop and ask the user before proceeding if:
- <condition> (or "None")
```

**Pointer specificity:** Point to the most specific file available. If the target doc has named sections, use `docs/path#section-name`. If the doc does not yet exist, it must be created (see Ordering below) before this file is written.

**Concrete example — `git.md`:**
```markdown
# Git

## Trigger
When: any git operation — commit, push, branch, merge, PR creation, tag

## Pointers
- Primary: `docs/developer/git-workflow.md` — branching model, commit conventions, PR process
- Secondary: `docs/developer/release.md#tagging` — tag format and push sequence for releases

## Critical rules
- Never commit directly to main — always branch first
- Never skip hooks (--no-verify) without explicit user request
- Never force-push without explicit user request
- Branch naming: feat/, fix/, test/, refactor/

## Red flags
Stop and ask the user before proceeding if:
- About to force-push to main
- About to amend a previously pushed commit
```

Files to create:
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

## Implementation Ordering (strict)

Steps must be executed in this order. A later step cannot start until its prerequisite is complete.

1. **Backup** — copy current CLAUDE.md to `Archive/CLAUDE.md.2026-03-15.bak` (`Archive/` at repo root, created if absent)
2. **Audit stale docs** — verify and update the following files to remove pre-pipx content before any context-engineering files point to them:
   - `docs/developer/guide.md` — remove `capcat.py`, `run_capcat.py`, `cli.py`, `./capcat` wrapper references; update to pipx-installed package
   - `docs/architecture/system.md` — remove Bash wrapper and `capcat.py` references; update to current package structure
   - `docs/troubleshooting.md` — remove `pynput` as required dep, remove `./capcat` wrapper commands, remove `-9` exit code from wrapper
3. **Create missing docs** — the following must exist before context-engineering files point to them:
   - `docs/developer/git-workflow.md` (create) — branching model, commit conventions, PR process, push rules
   - `docs/developer/testing.md` (create) — pytest usage, unit structure, TDD order, coverage targets
   - `docs/developer/release.md` (create) — semver rules, PyPI publish workflow, tagging sequence
   - `docs/reference/quick-reference.md` (create) — minimum content: source IDs by category, bundle names and their source lists, output path patterns for batch and single modes
4. **Clean docs/plans/** — remove or archive all Remotion/Video/Advertising plan docs. Enumerate: `2026-03-05-capcat-video-design.md`, `2026-03-05-capcat-video-implementation.md`, `2026-03-08-capcat-ad-design.md`, `2026-03-08-capcat-ad-implementation.md`, `2026-03-08-video-brainstorm-notes.md`. Also remove any files matching: `ls docs/plans/ | grep -iE 'video|remotion|ad-design|ad-impl|brainstorm'`
5. **Create context-engineering/** — write all 8 files using the template; every `## Pointers` entry must resolve to an existing file at time of writing
6. **Rewrite CLAUDE.md** — slim master controller per design above
7. **Verify** — run success criteria checks

---

## Cleanup Scope

### Remove from CLAUDE.md (stale)
- `## Git Workflow: Synology Drive` section — wrong user (`xpro`), wrong paths (`~/Projects/capcat/`)
- Architecture Overview diagram — references deleted `run_capcat.py`, `cli.py`, `capcat.py`
- Unified Article Processing section — belongs in `docs/architecture/`
- Common Issues > Wrapper Issues — references deleted `run_capcat.py`
- Essential Commands using `./capcat` wrapper — stale post-pipx migration
- Key Files `sources/active/bundles.yml` — wrong path post-packaging
- Line 44: `npx tsc --noEmit runs from ~/capcat/Video/` — Remotion artifact in Path and Shell Rules

### Remove from CLAUDE.md (abandoned project)
- All Remotion / Video / Advertising references (including `npx tsc` line)

### Disposition of currently unlisted sections
- `## PRIORITY RULE: Task Execution Protocol` — move to `context-engineering/plan-execution.md` Critical rules
- `## Quick Reference` (source list, bundle list, output paths) — move to `docs/reference/quick-reference.md`; remove from CLAUDE.md (changes too frequently to maintain here)

### Keep in CLAUDE.md (universal)
- Absolute Mode rules
- Git Branching mandatory rule
- Symlink path constant (`~/capcat`)
- Trigger table + multi-trigger precedence rule
- Meta-rule for new domains
- No emojis, no attribution footers
- Privacy rule (usernames → Anonymous)
- Versioning semver rules (patch/minor/major definitions only)

---

## Success Criteria

Measurable checks after implementation:

1. `wc -l CLAUDE.md` ≤ 80
2. `grep -r "xpro\|run_capcat\|capcat\.py\|cli\.py\|Projects/capcat\|Remotion\|remotion\|Video/" CLAUDE.md` → zero matches
3. `ls context-engineering/` → exactly 8 files present, each non-empty
4. Every `## Pointers` entry in all 8 context-engineering files resolves to a file that exists (anchors stripped before check): `for f in $(grep -h 'docs/' context-engineering/*.md | grep -o 'docs/[^# ]*' | sed 's/#.*//'); do test -f "$f" || echo "MISSING: $f"; done`
5. Every context-engineering file has all 4 required sections (Trigger, Pointers, Critical rules, Red flags)
6. `docs/plans/` contains zero Remotion/Video/Advertising files
7. `Archive/CLAUDE.md.2026-03-15.bak` exists
8. `pytest tests/unit/ -q` → exit code 0, zero failures (CLAUDE.md changes are non-code, suite must remain green regardless of test count)
