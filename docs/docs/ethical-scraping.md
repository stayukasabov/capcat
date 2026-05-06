---
layout: default
render_with_liquid: false
---

# Ethical Scraping

Capcat enforces ethical scraping practices across all sources. The `EthicalScrapingManager` is the single point of control — no source bypasses it.

## Core Rules

1. **Robots.txt is always checked** before fetching any URL (15-minute TTL cache)
2. **Rate limiting is mandatory** — minimum 1 second between requests to any domain
3. **Exponential backoff** on 429/503 responses — never hammers a server
4. **User-agent disclosure** — identifies as `Capcat/2.0`

## EthicalScrapingManager API

```python
from capcat.core.ethical_scraping import get_ethical_manager

manager = get_ethical_manager()
```

### enforce_rate_limit

Thread-safe slot reservation. Blocks until the minimum delay has elapsed since the last request to the domain.

```python
manager.enforce_rate_limit(domain, crawl_delay, min_delay=1.0)
```

Used by all sources before calling `session.get()`. Required — do not skip.

### can_fetch

Checks robots.txt for the given URL.

```python
allowed, reason = manager.can_fetch(url)
```

### request_with_backoff

Full ethical fetch: robots.txt check + rate limiting + exponential backoff on 429/503.

```python
response = manager.request_with_backoff(session, url, max_retries=3)
```

Not suitable for sites with `Disallow: /` in robots.txt (use `enforce_rate_limit` only in that case).

### request_hn_api

HN-specific Firebase API wrapper with backoff. Returns parsed JSON or None.

```python
data = manager.request_hn_api(session, url)
```

## Robots.txt Cache

- TTL: 15 minutes
- Per-domain
- `get_cache_stats()` returns hit/miss counts
- `clear_stale_cache()` removes expired entries

## Rate Limit Enforcement

Each domain has a thread-safe last-access timestamp. With 8 concurrent workers, all requests to a domain are serialized through the slot — only one worker proceeds at a time.

Default minimum delay: 1.0 second. Sources override via `rate_limit` in their YAML config or `self.config.rate_limit` in Python sources.

## Lobsters Note

`lobste.rs/robots.txt` has `Disallow: /` for `User-agent: *`. Capcat uses `enforce_rate_limit()` only (not `request_with_backoff()`) for Lobsters comment fetching to avoid the robots.txt block while still respecting rate limits.
