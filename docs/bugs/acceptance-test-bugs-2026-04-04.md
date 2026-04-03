# Acceptance Test Bugs — 2026-04-04

Collected from live acceptance testing of v1.9.7 against the TESTING vault.

---

## B4 — `__pycache__/*.pyc` files tracked in source config mirror

**Severity:** Medium — causes spurious "updates available" prompts on every run after a Python version change

**Symptom:**
Every fetch run reports 7 "updates available" for custom sources, all pointing to compiled bytecode files:
```
Custom sources: twitter/__pycache__/source.cpython-314.pyc, lb/__pycache__/source.cpython-314.pyc, ...
```
These are Python bytecode cache files, not user-editable config files.

**Root cause:**
`source_config_mirror.py:153` — `_mirror_custom` uses `dest_source.rglob("*")` which recurses into all files including `__pycache__/` subdirectories. Bytecode files get registered in the manifest with their builtin hash. When Python regenerates them (different interpreter version, etc.) the hash changes, triggering the upgrade prompt.

**Affected files:**
- `capcat/core/source_config_mirror.py:153-160` — `_mirror_custom` rglob does not filter `__pycache__`

**Expected behaviour:**
Only user-relevant files (`.py`, `.yaml`, `.yml`, etc.) should be tracked. `__pycache__/` directories must be excluded from mirroring and hash tracking.

**How to reproduce:**
Run `capcat fetch hn -q` after installing with a Python version different from the one that built the wheel. Observe the "updates available" prompt for `.pyc` files.

---

## B5 — Update prompt fires in `-q` (quiet/non-interactive) mode, crashing with EOF

**Severity:** High — any non-interactive run (background, CI, scripting) that encounters an upgrade prompt crashes with `Source config mirror failed: EOF when reading a line`

**Symptom:**
Running `capcat fetch hn -q` in background (no stdin) triggers the source mirror upgrade prompt. With no stdin available, `input("> ")` raises `EOFError`. The mirror fails and the fetch continues, but the upgrade is lost.

**Root cause:**
`source_config_mirror.py:98` — `_prompt` falls back to `print(message); return input("> ")` in non-TUI mode with no check for quiet mode or non-interactive stdin. `unified_source_processor.py:221` passes `tui_mode=is_tui_active()` but there is no quiet-mode flag passed to `SourceConfigMirror`. When `-q` is active, `is_tui_active()` is `False`, so `_prompt` always tries `input()` even in a non-interactive context.

**Affected files:**
- `capcat/core/source_config_mirror.py:92-98` — `_prompt` has no quiet/non-interactive guard
- `capcat/core/unified_source_processor.py:221` — mirror constructed without quiet mode flag

**Expected behaviour:**
In `-q` mode or when stdin is non-interactive (`not sys.stdin.isatty()`), the upgrade prompt must be skipped silently. Upgrades should either be auto-applied or deferred to the next interactive run.

**How to reproduce:**
1. Ensure vault has an outdated source mirror (trigger by upgrading capcat version)
2. Run `capcat fetch hn -q` with stdin redirected: `capcat fetch hn -q < /dev/null`
3. Observe "Source config mirror failed: EOF when reading a line"

---

## B2 — `processing.article_count` in `Global-settings.yaml` never reached for builtin sources

**Severity:** Medium — documented global fallback is dead code in practice; no builtin source has `article_count: null`

**Symptom:**
Setting `processing.article_count: 3` in `Global-settings.yaml` has no effect. Fetching HN still retrieves ~25-30 articles.

**Root cause:**
All builtin sources have `article_count` set in their own `config.yaml` (HN: 30). `_resolve_count` resolution chain is:
`CLI --count > capcat.yml sources list > source config.yaml > Global-settings.yaml default`

The source config.yaml value (30) is always reached before the global fallback. The global default is only reachable if a source has `article_count: null` in its config.yaml — which no builtin source does.

**Affected files:**
- `capcat/sources/builtin/custom/hn/config.yaml` — sets `article_count: 30`, masking global default
- `capcat/core/unified_source_processor.py:74-78` — global fallback unreachable for any builtin source

**Expected behaviour:**
`processing.article_count` in `Global-settings.yaml` should be reachable. Either:
- (a) Remove `article_count` from all builtin source `config.yaml` files so they fall through to the global default, OR
- (b) Document clearly that the global default only applies to user-created sources with no `article_count` in their config

**How to reproduce:**
Set `processing.article_count: 3` in `Global-settings.yaml`. Run `capcat fetch hn -q`. Observe more than 3 articles fetched.

---

## Notes from T2 Baseline Run (v1.9.7)

| Metric | Value |
|--------|-------|
| Version | 1.9.7 |
| Source | hn |
| Articles fetched | 25 (of 30 attempted; crawl_delay: 1.0) |
| `processing.article_count: 3` respected | No — B2 confirmed |
| Update prompt in `-q` mode | Yes — B5 confirmed |
| `__pycache__` in update list | Yes — B4 confirmed |
| Blocked (403/anti-bot) | 2 articles |
| JS-only pages | 1 article |

---

## B7 — `create_comments_file: false` ignored — comments always written

**Severity:** Medium — config setting has no effect; vault always accumulates comments files even when disabled

**Symptom:**
Setting `create_comments_file: false` in `Global-settings.yaml` has no effect. Comments files are written for every article that has a `comment_url`.

**Root cause:**
`unified_source_processor.py:487-492` — the `if` guard that triggers `fetch_comments` checks for `article.comment_url` but never checks `self.config.processing.create_comments_file`. The config field is defined in `ProcessingConfig` and loaded correctly but is never read at the point where comments fetching is decided.

**Affected files:**
- `capcat/core/unified_source_processor.py:487-492` — missing `self.config.processing.create_comments_file` guard

**Fix:**
Added `and self.config.processing.create_comments_file` to the comments block guard. Fixed in v1.9.11.

**How to reproduce:**
Set `create_comments_file: false` in `Global-settings.yaml`. Run `capcat fetch hn -q`. Observe `*-Comments.md` files in output.

---

## B8 — `download_images: false` ignored — images always downloaded

**Severity:** Medium — cannot disable image downloads via config

**Symptom:**
Setting `download_images: false` in `Global-settings.yaml` has no effect. Images are downloaded for all articles.

**Root cause:**
Two separate code paths both ignored the flag:
1. `article_fetcher.py:_process_embedded_media_efficiently` — no check on `get_config().processing.download_images` before adding image links to `quick_filtered_links`
2. `unified_media_processor.py:process_article_media` — no check before calling `image_processor.process_article_images`

**Fix:**
Added `_download_images = get_config().processing.download_images` guard before the filtering loop in `article_fetcher.py`, and early return in `unified_media_processor.py`. Fixed in v1.9.12.

---

## B9-B14 — Multiple processing/UI/logging config keys are dead code

**Severity:** Medium — documented, user-configurable settings have no effect

**Dead config keys (defined in ProcessingConfig, UIConfig, or LoggingConfig but never read by the code that should act on them):**

| Key | Type | Expected effect | Actual state |
|-----|------|-----------------|--------------|
| `min_image_dimensions` | `processing` | Skip images below N pixels | Never read; `_MIN_PIXEL_DIMENSION` (hardcoded 150px) used instead |
| `max_image_size_bytes` | `processing` | Skip images larger than N bytes | Never read anywhere |
| `markdown_line_breaks` | `processing` | Control trailing `\` in markdown | Never read anywhere |
| `remove_script_tags` | `processing` | Strip `<script>` from HTML | Only referenced in fallback config stub |
| `remove_style_tags` | `processing` | Strip `<style>` from HTML | Only referenced in fallback config stub |
| `remove_nav_tags` | `processing` | Strip `<nav>` from HTML | Only referenced in fallback config stub |
| `batch_spinner_style` | `ui` | Changes batch spinner animation | Never read anywhere |
| `progress_bar_width` | `ui` | Changes progress bar width | Never read anywhere |
| `show_detailed_progress` | `ui` | Per-article progress detail | Never read anywhere |
| `include_timestamps` | `logging` | Timestamps in log output | Never read; logger always includes them |
| `include_module_names` | `logging` | Module names in log output | Never read anywhere |
| `console_level` | `logging` | Terminal log verbosity | Never read; only DEBUG/INFO/ERROR affected by --verbose/-q flags |
| `use_emojis` | `ui` | Emoji in terminal output | Never read; `use_colors` read instead from `logging.use_colors` |
| `use_colors` | `ui` | ANSI colors in output | Hardcoded to True in progress.py; `logging.use_colors` read by logging setup |
