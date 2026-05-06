# Acceptance Test Bugs - 2026-04-03

Collected from live acceptance testing of v1.9.6 against the TESTING vault.

---

## B1 - `article_count` in `capcat.yml` sources list is silently ignored

**Severity:** High - user-facing config option has no effect

**Symptom:**
Configured `article_count: 5` for `hn` in `capcat.yml`:
```yaml
sources:
  - name: hn
    article_count: 5
```
Result: 24 articles fetched (the builtin default of 30, minus blocked/JS pages).

**Root cause:**
Two-part failure:

1. `ConfigManager._load_settings_file` explicitly strips the `sources` key before merging
   (`capcat/core/config.py:223` - `data.pop("sources", None)`), so the capcat.yml
   sources list never reaches the config object.

2. `SourceRegistry` loads `article_count` from the builtin source's own
   `capcat/sources/builtin/custom/hn/config.yaml` (value: 30), with no mechanism
   to accept a per-source override from the vault's `capcat.yml` sources list.

The resolution chain `_resolve_count` (CLI > source YAML > global config) never
sees the vault-level value because it is stripped before any resolver runs.

**Affected files:**
- `capcat/core/config.py:223` - strips sources key
- `capcat/core/source_system/source_registry.py:173` - article_count loaded from
  builtin config only
- `capcat/core/unified_source_processor.py:53-74` - `_resolve_count` has no
  vault-capcat.yml tier

**Expected behaviour:**
`article_count` in the `capcat.yml` sources list should override the builtin
source's default. Resolution chain should be:
CLI `--count` > `capcat.yml` sources list > source's own `config.yaml` > `Global-settings.yaml` global default.

**How to reproduce:**
```yaml
# capcat.yml
sources:
  - name: hn
    article_count: 5
```
Run `capcat fetch hn -q`. Observe more than 5 articles fetched.

---

## B2 - Global `processing.article_count` in `Global-settings.yaml` not tested end-to-end

**Severity:** Medium - untested code path; may work correctly but unverified

**Symptom:**
`Global-settings.yaml` documents `processing.article_count: 30` as the fallback
when no per-source or CLI count is set. This path was not directly verified during
acceptance testing because the builtin source config.yaml (30) masks the global
default (also 30 - identical values).

To confirm the global default is respected, the builtin source's `article_count`
would need to be `None` or absent. Currently it is always populated (30).

**Root cause:**
Not confirmed as a bug - may be working correctly. Needs an isolated test where
`Global-settings.yaml` sets a different value from the builtin source default.

**Affected files:**
- `capcat/core/unified_source_processor.py:70-73` - fallback to `config.processing.article_count`
- `capcat/sources/builtin/custom/hn/config.yaml` - always provides article_count: 30,
  so global fallback is never reached in practice

**Test needed:**
Set `processing.article_count: 3` in `Global-settings.yaml`, remove (or set to null)
`article_count` from the builtin hn source config, run fetch, verify 3 articles.

---

## Notes from T1 Baseline Run

| Metric | Value |
|--------|-------|
| Version | 1.9.6 |
| Source | hn |
| Articles fetched | 24 (of 30 attempted) |
| Comments files | 22/24 |
| Images downloaded | 162 |
| PDFs downloaded | 1 |
| Fetch duration | 11m 42s |
| Blocked (403/anti-bot) | 2 articles |
| JS-only pages | 1 article |
| Frontmatter | Correct (title, url, source, source_code, category, captured, tags) |

**Findings:**
- Frontmatter structure is correct
- Comments files created for all accessible articles
- Image download works (162 images across 24 articles = ~6.75 avg)
- PDF download working (1 PDF found)
- Error messages for blocked/JS pages printed to stdout in quiet mode (should go to stderr or log only)
