# Tutorials Section Refactor and Logo Tooltip Fix
**Date:** 2026-01-31
**Agent:** Claude Sonnet 4.5
**Project:** Capcat Documentation Website
**Scope:** docs/index.html tutorials grid, logo link accessibility

---

## Executive Summary

Refactored the "Tutorials & Documentation" section on the index page to eliminate duplicated links between the Interactive Menu and CLI Commands cards. Consolidated shared tutorial pages into the CLI Commands card, reduced the Interactive Menu card to its unique content, and added the Source Management Menu doc as the second Interactive Menu link. Fixed a logo hover tooltip caused by `title` attributes on logo links — replaced with `aria-label` across index.html and both include templates.

---

## Context

The previous accessibility session (2026-01-27, commit b4dd7d0) addressed repeated link text (WCAG 2.4.4) by adding `(CLI)` and `(Interactive)` suffixes to differentiate duplicate links pointing to the same pages. This created a second problem: the Interactive Menu card mirrored the CLI Commands card almost entirely, with three of four links resolving to identical URLs. The suffixes added noise without adding navigational value.

---

## Changes Made

### 1. Tutorials Section Restructuring

**File:** `docs/index.html`

#### Interactive Menu card — before (4 links):
| Link Text | URL |
|---|---|
| Interactive Mode Guide | `docs/tutorials/user/03-interactive-mode.html` |
| Daily Workflow (Interactive) | `docs/tutorials/user/02-daily-workflow.html` |
| Managing Sources (Interactive) | `docs/tutorials/user/04-managing-sources.html` |
| Organizing Bundles (Interactive) | `docs/tutorials/user/05-bundles.html` |

#### Interactive Menu card — after (2 links):
| Link Text | URL |
|---|---|
| Interactive Mode Guide | `docs/tutorials/user/03-interactive-mode.html` |
| Source Management Menu | `docs/source-management-menu.html` |

**Rationale:** Three of the four original links (`02`, `04`, `05`) pointed to pages shared with the CLI card — they cover both modes, not interactive-only content. `03-interactive-mode.html` is the only tutorial scoped to the TUI. `source-management-menu.html` (`docs/docs/source-management-menu.html` on disk) is the only other doc in the site that is entirely interactive-menu-specific. It covers the add/remove/configure submenu — content that has no CLI equivalent page.

#### CLI Commands card — before (4 links):
| Link Text | URL |
|---|---|
| First 5 Minutes with Capcat | `docs/tutorials/user/01-getting-started.html` |
| Daily Workflow (CLI) | `docs/tutorials/user/02-daily-workflow.html` |
| Managing Sources (CLI) | `docs/tutorials/user/04-managing-sources.html` |
| Organizing Bundles (CLI) | `docs/tutorials/user/05-bundles.html` |

#### CLI Commands card — after (3 links):
| Link Text | URL |
|---|---|
| First 5 Minutes with Capcat | `docs/tutorials/user/01-getting-started.html` |
| Daily Workflow | `docs/tutorials/user/02-daily-workflow.html` |
| Managing Sources | `docs/tutorials/user/04-managing-sources.html` |

**Rationale:** Removed `(CLI)` and `(Interactive)` suffixes — no longer needed once links are not duplicated across cards. Removed "Organizing Bundles" to bring the count to three. Bundles content is covered by the other tutorials and the Interactive Mode Guide links into bundle usage.

#### Link path fix (post-deploy 404):
Initial commit used `docs/docs/source-management-menu.html`. The index.html is served from site root; files in `docs/docs/` on disk map to `docs/` in URLs (same convention as `docs/architecture.html`, `docs/source-development.html` in the Advanced Topics card). Corrected to `docs/source-management-menu.html`.

---

### 2. Logo Tooltip Fix

**Files:**
- `docs/index.html` (header logo, line 23; footer logo, line 568)
- `docs/_includes/header.html` (line 5)
- `docs/_includes/footer.html` (line 5)

#### Problem:
Logo `<a>` tags had `title="Back to Home"`. The `title` attribute renders as a browser tooltip on hover. On a logo link containing only an SVG (no text content), this tooltip appears as unexplained text.

#### Solution:
Replaced `title` with `aria-label` on all four logo links.

```html
<!-- Before -->
<a href="/" title="Back to Home"><svg ...></svg></a>

<!-- After -->
<a href="/" aria-label="Back to Home"><svg ...></svg></a>
```

**Why `aria-label` not `title`:**
- `aria-label` provides the accessible name for screen readers without producing a visible tooltip.
- `title` is the correct attribute for supplementary info on elements that already have visible text (used correctly on nav links like Features, How It Works). On a logo link with no visible text, `title` is the wrong mechanism — it exposes the accessible name visually when it shouldn't.

**Scope note:** 173 other docs pages have the same `title="Back to Home"` inline in their headers. Only `index.html` and the two include templates were fixed this session. A batch find-replace across all pages remains if needed.

---

## Files Modified

| File | Change |
|---|---|
| `docs/index.html` | Tutorials grid restructured; both logo links fixed |
| `docs/_includes/header.html` | Logo link `title` → `aria-label` |
| `docs/_includes/footer.html` | Logo link `title` → `aria-label` |

---

## Git History

| Commit | Message | Notes |
|---|---|---|
| `6096623` | Refactor tutorials section and fix logo tooltip | 3 files, 12 insertions, 38 deletions |
| `b90df54` | Fix source-management-menu link path | 1 file, path correction after 404 |

**Branch:** main
**Remote:** https://github.com/stayukasabov/capcat.git
**Status:** Pushed and deployed

---

## Relationship to Previous Work

| Previous Session Issue | This Session Action |
|---|---|
| Issue #10 (2026-01-27): Added `(CLI)`/`(Interactive)` suffixes to deduplicate repeated links | Suffixes removed. Deduplication achieved by consolidation instead — shared pages moved to one card, unique content added to the other. |

The previous fix was correct for the constraint it solved (identical link text in the links list). This session's approach addresses the underlying cause: the cards should not contain the same links.

---

## Remaining Work

- Batch replace `title="Back to Home"` → `aria-label="Back to Home"` across 173 remaining docs pages
- Verify `docs/source-management-menu.html` renders correctly at https://capcat.org/docs/source-management-menu.html

---

**Report Completed:** 2026-01-31
**Agent:** Claude Sonnet 4.5
**Status:** Complete
