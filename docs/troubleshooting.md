# Troubleshooting

## Import Errors on Startup

**Symptom**: `capcat` fails with an `ImportError` or `ModuleNotFoundError`.

**Fix**: Reinstall via pipx:
```bash
pipx reinstall capcat
```

Or upgrade to latest:
```bash
pipx upgrade capcat
```

---

## Source Failures

**Symptom**: A source returns 0 articles or fails silently.

**Common causes:**
- Feed URL changed — check source YAML config under `capcat/sources/builtin/config_driven/configs/`
- Anti-bot protection (Cloudflare) — use the RSS feed URL instead of the HTML page
- DNS/network issue — test the feed URL in a browser

**Check feed validity:**
```bash
capcat list sources   # confirm source is registered
```

---

## Brotli / Garbled Content

**Symptom**: Article content is binary garbage or unreadable characters.

**Cause**: This was a known issue in versions prior to v1.0.25 where the `Accept-Encoding: br` header was sent but brotli decompression was unavailable. Fixed in v1.0.25 — upgrade:
```bash
pipx upgrade capcat
```

---

## Bundle Expansion Errors

**Symptom**: `"Source 'techpro' is not configured"` when running `capcat bundle all`.

**Cause**: Bundle names were passed as source IDs in versions prior to v1.0.27. Fixed in v1.0.27 — upgrade:
```bash
pipx upgrade capcat
```

---

## TUI Post-Completion Freeze

**Symptom**: After a fetch/bundle completes in the TUI (`capcat catch`), the terminal freezes or the menu does not return.

**Cause**: Fixed in v1.0.30. The completion screen now shows status, optional HTML link, and "Back to Menu" / "Exit" options. Upgrade:
```bash
pipx upgrade capcat
```

---

## Other Common Issues

For dependency and module issues not covered above, see `docs/developer/guide.md`.
