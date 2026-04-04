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

---

## B15 — `min_image_dimensions` never checked — `max_image_bytes` routing takes priority

**Severity:** High — `min_image_dimensions` setting has no observable effect even when explicitly configured

**Symptom:**
Setting `min_image_dimensions: 5000` in `Global-settings.yaml` has no effect. Images of any pixel size are downloaded (limited only by `max_image_size_bytes`).

**Root cause:**
`image_processor.py:_download_images_with_checking` uses exclusive `if/elif` branching:
```python
if max_image_bytes > 0:         # ALWAYS True (default is 5242880)
    filename = _download_single_image_with_max_bytes(...)
elif min_pixel_dimension > 0:   # UNREACHABLE — above is always True
    filename = _download_single_image_with_min_pixels(...)
```
Since `max_image_size_bytes` defaults to 5242880 (non-zero), the `max_image_bytes > 0` branch is always taken. `min_pixel_dimension` is never checked.

**Affected files:**
- `capcat/core/image_processor.py:_download_images_with_checking` (lines 353-370) — exclusive branching prevents pixel filter from being applied

**Expected behaviour:**
Both `max_image_size_bytes` and `min_image_dimensions` should be applied as a pipeline: first reject images by byte ceiling (cheap pre-download HEAD check), then reject by pixel dimensions after download.

**How to reproduce:**
Set `min_image_dimensions: 5000` in `Global-settings.yaml`. Run `capcat fetch bbc -q`. Observe images still downloaded despite 5000px minimum.

---

## B16 — `max_filename_length` truncates folders but not markdown filenames

**Severity:** Medium — .md filenames inside article folders are not truncated

**Symptom:**
Setting `max_filename_length: 15` truncates article folder names correctly but the `.md` file inside uses the full title (up to 200 chars).

**Root cause:**
`storage_manager.py:27,36` — `article_md_filename` and `comments_md_filename` hardcode `max_length=200`:
```python
def article_md_filename(title: str) -> str:
    return sanitize_filename(title, max_length=200).replace(" ", "-") + ".md"
```
When `max_length` is explicitly passed to `sanitize_filename`, it overrides the config lookup. Folder creation goes through `sanitize_filename(title)` with no explicit max_length, so it correctly reads the config value.

**Affected files:**
- `capcat/core/storage_manager.py:27` — `article_md_filename` hardcodes `max_length=200`
- `capcat/core/storage_manager.py:36` — `comments_md_filename` hardcodes `max_length=200`

**Expected behaviour:**
Both folder names and markdown filenames should be truncated to `max_filename_length`.

**How to reproduce:**
Set `max_filename_length: 15`. Run `capcat fetch bbc -q`. Folder names are ≤15 chars; `.md` filenames are full length.

---

## B17 — `user_agent` setting ignored — session pool uses rotating UA strings

**Severity:** Medium — user cannot identify their bot or use a custom User-Agent

**Symptom:**
Setting `user_agent: "TestBot/1.0"` in `Global-settings.yaml` has no effect. Verbose output shows a random Mozilla browser UA string.

**Root cause:**
`session_pool.py:92` — `_create_session` always uses `random.choice(USER_AGENTS)` instead of reading `config.network.user_agent`:
```python
user_agent = random.choice(USER_AGENTS)  # ignores config
```

**Affected files:**
- `capcat/core/session_pool.py:92` — UA selection ignores `self.config.network.user_agent`

**Expected behaviour:**
When `user_agent` is set to a non-default value, it should be used. When set to default (`"Capcat/2.0 (Personal news archiver)"`) the existing rotation behaviour is acceptable.

**How to reproduce:**
Set `user_agent: "TestBot/1.0"`. Run `capcat fetch bbc -V`. Debug log shows `Using User-Agent for bbc: Mozilla/5.0...` instead of `TestBot/1.0`.

---

## B18 — `max_retries` ignored — session pool hardcodes `max_retries=3`

**Severity:** Low — user cannot tune retry count via config

**Symptom:**
Setting `max_retries: 0` in `Global-settings.yaml` has no effect. Sessions still retry 3 times on connection failure.

**Root cause:**
`session_pool.py:118` — `HTTPAdapter` is created with `max_retries=3` hardcoded:
```python
adapter = requests.adapters.HTTPAdapter(
    pool_connections=self.config.network.pool_connections,
    pool_maxsize=self.config.network.pool_maxsize,
    max_retries=3,  # hardcoded, ignores config
)
```

**Affected files:**
- `capcat/core/session_pool.py:118` — `max_retries` hardcoded

**Expected behaviour:**
`max_retries` should use `self.config.network.max_retries`.

**How to reproduce:**
Set `max_retries: 0`. Observe fetch still retries on transient failures.

---

## B19 — `use_colors: false` ignored — ANSI codes always emitted

**Severity:** Medium — cannot disable color output via config; piped output contains raw escape sequences

**Symptom:**
Setting `use_colors: false` in `Global-settings.yaml` has no effect. Terminal and piped output still contains ANSI color escape sequences (`\033[38;5;230m` etc.).

**Root cause:**
`progress.py` hardcodes `use_colors = True` at 18+ sites. None of them reads `get_config().ui.use_colors`. Example at line 200:
```python
use_colors = True  # hardcoded — never reads config
```

**Affected files:**
- `capcat/core/progress.py` — `use_colors = True` hardcoded throughout

**Expected behaviour:**
`use_colors: false` should suppress all ANSI escape sequences from terminal output.

**How to reproduce:**
Set `use_colors: false`. Run `capcat fetch bbc 2>&1 | cat`. Output still contains `\033[` sequences.

---

## B20 — `progress.py:1104` references removed `UIConfig.show_progress_animations`

**Severity:** Low — dead code; `get_progress_indicator` is never called, so no runtime crash

**Symptom:**
`progress.py` function `get_progress_indicator` references `config.ui.show_progress_animations`, which was removed from `UIConfig` in v1.9.15. This would `AttributeError` if called.

**Root cause:**
`get_progress_indicator` was not updated when `show_progress_animations` was removed from `UIConfig`.

**Affected files:**
- `capcat/core/progress.py:1104` — stale attribute reference

**How to reproduce:**
`python3 -c "from capcat.core.progress import get_progress_indicator; get_progress_indicator('test', 3)"` → `AttributeError`

---

## B21 — `progress_spinner_style` only affects PDF spinner, not main article fetch spinner

**Severity:** Low — setting has no visible effect for most users (PDF download spinner is rarely seen)

**Symptom:**
Setting `progress_spinner_style: wave` has no visible effect on the main article fetch display. The "CATCHING ▶" activity spinner is always shown.

**Root cause:**
`get_batch_progress` in `progress.py:1109` instantiates `BatchProgress` without passing `spinner_style`. `BatchProgress` defaults to `"activity"` spinner. The config value is only passed to the PDF download `ProgressIndicator` at `article_fetcher.py:2364`.

**Affected files:**
- `capcat/core/progress.py:1127-1130` — `get_batch_progress` does not pass `spinner_style` to `BatchProgress`

**Expected behaviour:**
`progress_spinner_style` should affect the main article fetch spinner.

**How to reproduce:**
Set `progress_spinner_style: wave`. Observe no change in spinner during fetch.



## B22 — `min_image_dimensions` silently skipped for WebP images

**Severity:** High — the dominant image format from BBC/Guardian is WebP; the filter has no effect in practice

**Symptom:**
Setting `min_image_dimensions: 5000` downloads all WebP images regardless of their pixel dimensions. Images at 1536×864px survive when they should be rejected.

**Root cause:**
`_read_image_dimensions` in `image_processor.py` only parsed PNG and JPEG headers. For any unrecognised format it returns `None`. The filter in `_download_single_image_filtered` skips the check when `dims is None`:
```python
if dims is not None:   # ← webp hits this as None → check silently bypassed
    ...delete if below threshold
```

**Affected files:**
- `capcat/core/image_processor.py:112-161` — `_read_image_dimensions` missing WebP (VP8, VP8L, VP8X) header parsers

**Expected behaviour:**
All three WebP chunk variants (VP8 lossy, VP8L lossless, VP8X extended) should return correct `(width, height)` so the pixel floor filter applies.

**How to reproduce:**
Set `min_image_dimensions: 5000`. Run `capcat fetch bbc guardian -q`. Images appear in `images/` folders despite being 1536×864px.

**Fix:** Extended `_read_image_dimensions` with VP8/VP8L/VP8X header parsing. Header read increased from 26 to 30 bytes.
