# Acceptance Test — 2026-04-12

**Scope:** PR #31 — PDF downloads now respect the `--media` flag
**Version tested:** 1.9.22 (local dev build, `pipx install . --force`)
**Test vault:** `~/Desktop/TESTING/`
**Sources:** `hn` (article_count: 10)
**crawl_delay:** 0.1

---

## Findings

### PDF behaviour — `--media` flag gate

| Test | Command | Expected | Actual | Result |
|------|---------|----------|--------|--------|
| No PDFs without flag | `capcat fetch hn -q --count 10` | 0 `.pdf` files in vault | 0 `.pdf` files | PASS |
| PDFs with flag | `capcat fetch hn --media -q --count 10` | ≥1 `.pdf` file in vault | 1 `.pdf` file (`Countries100Pct.pdf`) | PASS |

### Interactive note text

| Check | Expected | Actual | Result |
|-------|----------|--------|--------|
| Note text | "Choosing Yes downloads PDFs, videos, audio, and documents" | Confirmed present in installed binary | PASS |

---

## Bugs Found

None. All acceptance criteria met.

---

## Notes

- Interactive PDF prompt (`catch` mode) cannot be automated — note text verified via source inspection of installed binary
- Two articles failed to fetch due to anti-bot protection (researchgate.net) and timeout (phyphox.org) — unrelated to this fix
