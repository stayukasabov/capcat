# Task List

_Last updated: 2026-03-19_

---

## Backlog

### HTML Generation Refactor
**Priority:** High
**Status:** Not started
**Ref:** `docs/architecture/roadmap.md#html-generation-refactor`

Replace `capcat/core/html_generator.py` (1,828-line monolith) with the `htmlgen/` factory pattern.

- The replacement code exists in `capcat/htmlgen/` but is not wired up
- Must connect `BaseHTMLGenerator` to `TemplateRenderer` + `DesignSystemCompiler`
- Must complete `generate_directory_index` in base class
- Must switch `html_post_processor.py` and `article_fetcher.py` to use `HTMLGeneratorFactory`
- Delete `html_generator.py` once all tests pass

**Before starting:** Run brainstorming skill. Read `htmlgen/` code in full before proposing anything.

---

## Completed (this session, 2026-03-19)

- [x] Merged `test/image-anchor-removal` — PR #11 — regression tests for `_remove_image_anchor_wrappers()`
- [x] Merged `test/cli-validation` — PR #12 — regression tests for `CLIValidator`, `EnhancedArgumentParser`, `CLIRecovery`
- [x] Merged `fix/comments-breadcrumb-article-link` — PR #13 — re-fixed reverted breadcrumb bug (`article.html` 0 levels up, not 1)
- [x] Deleted all stale local branches (10 branches)
- [x] Released `v1.1.5` to PyPI
