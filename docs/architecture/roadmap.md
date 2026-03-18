# Architecture Roadmap

Planned refactors that are documented but not yet scheduled. Each entry captures the motivation, the current state, and the target design so the work can be picked up without re-investigating.

---

## HTML Generation Refactor

**Status:** Not started
**Priority:** High — affects developer experience for every new source
**Trigger:** When adding a 3rd custom source with HTML output, or when `html_generator.py` needs modification for any reason

### Problem

`capcat/core/html_generator.py` (1,828 lines) is a monolith with source knowledge embedded via directory-name string matching. Adding a source requires finding every if/elif chain and inserting a new branch. No enforced interface means source-specific logic can be added anywhere in the file.

### Existing Work

`capcat/htmlgen/` was built as the correct replacement and is archived, not deleted. It provides:

- `BaseHTMLGenerator` (ABC) with four abstract methods that each source must implement: `count_comments`, `should_show_comment_link`, `matches_directory_pattern`, `generate_breadcrumb`
- `HTMLGeneratorFactory` with a registry pattern — generators register themselves at module load; the factory detects the source from a directory name and instantiates the right generator
- `HnGenerator`, `LbGenerator`, `LessWrongGenerator` — source-specific subclasses, each in their own file under `capcat/htmlgen/<source>/`

### Gap

`htmlgen/` uses Jinja2 directly and is not connected to `TemplateRenderer` + `DesignSystemCompiler` (the live template system that reads `Config/themes/design-system.css`). The `HnGenerator` and `LbGenerator` are missing a `generate_directory_index` implementation (stub only).

### Target Design

1. Reconnect `BaseHTMLGenerator` to `TemplateRenderer` and `DesignSystemCompiler` — replace the Jinja2 fallback with the same template pipeline used in `html_generator.py`
2. Complete `generate_directory_index` in the base class (common logic, no source-specific branches)
3. Implement `generate_article_page` and `generate_comments_page` in the base class using the template system; source subclasses override only what differs
4. Wire `html_post_processor.py` to use `HTMLGeneratorFactory.detect_source_from_directory()` → `HTMLGeneratorFactory.create_generator()` instead of the monolithic `HTMLGenerator`
5. Delete `capcat/core/html_generator.py` once all tests pass against the new system

### Files

| File | Action |
|------|--------|
| `capcat/htmlgen/base/base_generator.py` | Connect to `TemplateRenderer` + `DesignSystemCompiler`; complete directory index |
| `capcat/htmlgen/hn/generator.py` | Review and complete |
| `capcat/htmlgen/lb/generator.py` | Review and complete |
| `capcat/htmlgen/lesswrong/generator.py` | Review — LessWrong has no fetch path; keep renderer only |
| `capcat/core/html_post_processor.py` | Switch from `HTMLGenerator` to `HTMLGeneratorFactory` |
| `capcat/core/article_fetcher.py` | Switch from `HTMLGenerator` to `HTMLGeneratorFactory` |
| `capcat/core/html_generator.py` | Delete after switchover |

### Before Starting

Run the brainstorming skill. This refactor touches the full HTML output pipeline and requires a spec before implementation. The `htmlgen/` code is the design intent — read it before proposing anything.
