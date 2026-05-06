# Acceptance Test Bugs - 2026-04-13
## Feature tested: media: config section (4-level hierarchy)

---

## B1 - Source mirror upgrade permanently suppressed after non-interactive run

**Severity:** Medium

**Symptom:** `--pdfs` CLI flag produces 0 PDFs when the vault has a stale `hn/source.py` mirror. The vault mirror is missing `download_pdfs` parameter added in v1.9.22. Even after running `capcat fetch hn --pdfs -q` multiple times, the mirror never updates.

**Root cause:** `capcat/core/source_config_mirror.py`, `_step2_3_changed_builtins`, else branch (line ~329):

```python
else:
    for key, _, new_builtin_hash in override_candidates:
        manifest[key]["builtin_hash"] = new_builtin_hash
```

When the upgrade prompt runs non-interactively (`-q`, background task, stdin not a tty), `self._prompt()` returns `'n'` silently. The code then hits the `else` branch, which updates `manifest.builtin_hash` to the new builtin hash WITHOUT updating the vault file. On the next run, `current_builtin_hash == stored_builtin_hash` so no upgrade is detected or offered - ever.

**Affected files:**
- `capcat/core/source_config_mirror.py` - `_step2_3_changed_builtins`

**Expected behaviour:** When user declines (or prompt is silently skipped), `manifest.builtin_hash` must NOT be updated. The next interactive run should re-offer the upgrade. Only after the user accepts and the file is actually overwritten should the hash be updated.

**How to reproduce:**
1. Create a fresh test vault: `cd ~/Desktop/TESTING && capcat settings --force`
2. Run `capcat fetch hn -q` (non-interactive, triggers silent decline)
3. Run `grep builtin_hash ~/Desktop/TESTING/.capcat/source_hashes.json`  
   - `builtin_hash` now equals hash of new installed package, vault file still old
4. Run `capcat fetch hn --pdfs -q`  
   - 0 PDFs despite `--pdfs` flag  
5. Run `diff ~/Desktop/TESTING/Config/sources/active/custom/hn/source.py ~/.local/pipx/venvs/capcat/lib/python3.14/site-packages/capcat/sources/builtin/custom/hn/source.py`  
   - diff shows `download_pdfs` missing in vault but present in installed package

**Note:** The `--pdfs` regression is caused entirely by this mirror bug, not by the new `_resolve_media` logic. The 4-level media config feature tests (A-D) all pass correctly.

---

## Test results summary

| Test | Setting | Expected | Actual | Status |
|------|---------|----------|--------|--------|
| A | `media.download_images: false` in Global-settings.yaml | 0 images in bbc+guardian articles | 0 images | PASS |
| B | `media.download_pdfs: true` in Global-settings.yaml | PDFs auto-downloaded for hn without `--pdfs` | 7 PDFs downloaded | PASS |
| C | `media.download_pdfs: true` in source `config.yaml` (hn) | hn downloads PDFs, no global flag needed | 3 PDFs downloaded | PASS |
| D | `capcat.yml` source entry `media.download_pdfs: true` for hn | hn gets PDFs, bbc does not | hn: 2 PDFs, bbc: 0 | PASS |
| E | `--pdfs` CLI flag | PDFs downloaded via CLI override | 0 PDFs (stale vault mirror) | FAIL - B1 |
