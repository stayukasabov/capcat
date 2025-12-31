# Ethical Scraping Implementation

**Status:** Implemented
**Version:** 2.0
**Last Updated:** October 8, 2025

## Overview

Capcat implements comprehensive ethical scraping practices to ensure respectful and compliant content collection from news sources.

## Core Principles

### 1. Prefer Official APIs > RSS > HTML Scraping

**Implementation Priority:**
1. **Official APIs** - Always preferred when available
2. **RSS/Atom Feeds** - Second choice, widely supported
3. **HTML Scraping** - Last resort, only when no alternatives exist

**Current Source Distribution:**
- Custom sources (10): Use RSS feeds or specialized approaches
- Config-driven sources (1): InfoQ uses RSS

### 2. Robots.txt Compliance

**Implementation:** `core/ethical_scraping.py`

**Features:**
- Automatic robots.txt fetching and parsing
- 15-minute TTL cache to reduce server load
- Crawl-delay extraction and enforcement
- Path validation against disallow rules

**Cache Management:**
```python
from core.ethical_scraping import get_ethical_manager

manager = get_ethical_manager()
parser, crawl_delay = manager.get_robots_txt(base_url)
allowed, reason = manager.can_fetch(url)
```

**Cache Statistics:**
- TTL: 15 minutes
- Auto-cleanup of stale entries
- Per-domain caching

### 3. User-Agent Identification

**Standard User-Agent:**
```
Capcat/2.0 (Personal news archiver)
```

**Implementation Locations:**
- `core/config.py:35` - Global default
- `core/source_system/source_config.py:54` - Source config default
- `core/source_system/config_driven_source.py:119` - RSS requests
- `sources/active/custom/lb/source.py:61,460` - Lobsters custom headers

**Format Guidelines:**
- Product name and version: `Capcat/2.0`
- Purpose description: `(Personal news archiver)`
- No personal information or URLs

### 4. Rate Limiting

**Enforcement:**
- Minimum 1 request per second globally
- Respect robots.txt crawl-delay directives
- Per-domain rate limiting tracking

**Current Rate Limits:**
<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Source</th>
      <th>Rate Limit</th>
      <th>Robots.txt Requirement</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>InfoQ</td>
      <td>20.0s</td>
      <td>20.0s</td>
      <td>Compliant</td>
    </tr>
    <tr>
      <td>BBC</td>
      <td>Custom</td>
      <td>N/A</td>
      <td>Compliant</td>
    </tr>
    <tr>
      <td>HN</td>
      <td>API</td>
      <td>N/A</td>
      <td>Compliant</td>
    </tr>
    <tr>
      <td>Lobsters</td>
      <td>RSS</td>
      <td>N/A</td>
      <td>Compliant</td>
    </tr>
    <tr>
      <td>Others</td>
      <td>1.0-3.0s</td>
      <td>Varies</td>
      <td>Compliant</td>
    </tr>
  </tbody>
</table>
</div>

### 5. Error Handling with Exponential Backoff

**Implementation:** `core/ethical_scraping.py:request_with_backoff()`

**HTTP Status Codes Handled:**
- **429 (Too Many Requests):**
  - Respect `Retry-After` header
  - Exponential backoff if header missing
  - Initial delay: 1.0s, multiplier: 2x

- **503 (Service Unavailable):**
  - Exponential backoff
  - Initial delay: 1.0s, multiplier: 2x
  - Max retries: 3 attempts

**Backoff Strategy:**
```
Attempt 1: 1.0s delay
Attempt 2: 2.0s delay
Attempt 3: 4.0s delay
```

## Implementation Details

### EthicalScrapingManager Class

**Location:** `core/ethical_scraping.py`

**Key Methods:**

```python
class EthicalScrapingManager:
    def __init__(self, user_agent: str = "Capcat/2.0")

    def get_robots_txt(self, base_url: str, timeout: int = 10) -> Tuple[RobotFileParser, float]

    def can_fetch(self, url: str) -> Tuple[bool, str]

    def enforce_rate_limit(self, domain: str, crawl_delay: float, min_delay: float = 1.0)

    def request_with_backoff(
        self, session: requests.Session, url: str,
        method: str = "GET", max_retries: int = 3,
        initial_delay: float = 1.0, **kwargs
    ) -> requests.Response

    def validate_source_config(self, base_url: str, rate_limit: float) -> Tuple[bool, str]

    def get_cache_stats(self) -> Dict[str, any]

    def clear_stale_cache(self)
```

### Usage Example

```python
from core.ethical_scraping import get_ethical_manager

# Get global manager instance
manager = get_ethical_manager()

# Validate source configuration
is_valid, message = manager.validate_source_config(
    base_url="https://example.com/news/",
    rate_limit=2.0
)

if not is_valid:
    print(f"Configuration issue: {message}")

# Make ethical request with backoff
response = manager.request_with_backoff(
    session=requests.Session(),
    url="https://example.com/article",
    timeout=30
)
```

## Compliance Audit Process

**Tool:** `audit_ethical_compliance.py` (temporary, created on-demand)

**Audit Checks:**
1. Robots.txt fetching and parsing
2. Crawl-delay requirement extraction
3. Path allowance validation
4. RSS feed availability detection
5. Rate limit compliance verification
6. Bundle membership verification

**Last Audit:** October 8, 2025
**Result:** All active sources compliant

**Findings:**
- 1 active config-driven source (InfoQ)
- 5 orphaned sources moved to inactive
- 0 active violations

## Source Compliance Status

### Active Sources (11)

**Config-Driven (1):**
- InfoQ - RSS feed, 20.0s rate limit, compliant

**Custom Sources (10):**
- Hacker News - Official API
- Lobsters - RSS feed
- BBC - Custom implementation
- Gizmodo - RSS feed
- Futurism - RSS feed
- IEEE Spectrum - RSS feed
- Nature - RSS feed
- Scientific American - RSS feed
- LessWrong - GraphQL API
- MIT Tech Review - RSS feed (inactive in bundles)

### Inactive Sources (5)

Moved to `sources/inactive/config_driven/`:
- Axios - Blocked by robots.txt
- TASS - Orphaned, not in bundles
- UPI - Blocked by robots.txt, RSS available
- Xinhua - Orphaned, not in bundles
- Yahoo News - Blocked by robots.txt, RSS available

## Red Flags to Avoid

### Never Do:
- Ignore robots.txt directives
- Bypass anti-bot protection
- Scrape paths explicitly blocked
- Use aggressive rate limits (<1s without permission)
- Impersonate browser User-Agents deceptively
- Scrape authentication-required content
- Access paywalled content
- Ignore 429/503 error responses

### Always Do:
- Check robots.txt before scraping
- Respect crawl-delay directives
- Use RSS/API when available
- Identify as "Capcat/2.0 (Personal news archiver)"
- Handle errors gracefully with backoff
- Cache robots.txt to reduce load
- Rate limit: minimum 1 req/s
- Document scraping methodology

## Configuration Reference

### Rate Limit Configuration

**File:** `sources/active/config_driven/configs/iq.yaml`

```yaml
# Request configuration
timeout: 15
rate_limit: 20.0  # Must be >= robots.txt crawl-delay
```

### User-Agent Configuration

**File:** `core/config.py`

```python
@dataclass
class NetworkConfig:
    user_agent: str = "Capcat/2.0 (Personal news archiver)"
```

### RSS Discovery Configuration

**File:** `sources/active/config_driven/configs/iq.yaml`

```yaml
# Discovery method - use RSS for latest news articles only
discovery:
  method: "rss"
  rss_url: "https://feed.infoq.com"
  max_articles: 30
```

## Testing Compliance

### Manual Testing

```bash
# Test InfoQ RSS implementation
./capcat fetch iq --count 5

# Test with verbose logging
./capcat -L compliance.log fetch iq --count 5

# View logs
tail -f compliance.log
```

### Automated Validation

```python
from core.ethical_scraping import get_ethical_manager

manager = get_ethical_manager()

# Validate all sources
sources = ["iq", "hn", "lb", "bbc"]
for source_id in sources:
    config = load_source_config(source_id)
    is_valid, message = manager.validate_source_config(
        config.base_url,
        config.rate_limit
    )
    print(f"{source_id}: {message}")
```

## Future Enhancements

### Planned Features:
1. Integration with source system for automatic validation
2. Real-time compliance monitoring
3. Automatic rate limit adjustment based on robots.txt
4. Quarterly automated compliance audits
5. RSS feed discovery automation
6. Enhanced backoff strategies (jitter, adaptive delays)

### Under Consideration:
- Sitemap.xml support for discovery
- API key management for official APIs
- Circuit breaker pattern for failing sources
- Distributed rate limiting (multi-instance support)

## References

### Documentation
- [Robots.txt Specification](https://www.robotstxt.org/)
- [HTTP 429 Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)
- [RSS 2.0 Specification](https://www.rssboard.org/rss-specification)
- [Atom Syndication Format](https://datatracker.ietf.org/doc/html/rfc4287)

### Internal Documentation
- `ETHICAL_COMPLIANCE_REPORT.md` - October 2025 audit results
- `docs/architecture.md` - System architecture
- `docs/source-development.md` - Adding new sources

## Maintenance

### Regular Tasks

**Monthly:**
- Review rate limits for new sources
- Check for RSS feed availability
- Update User-Agent if needed

**Quarterly:**
- Run full compliance audit
- Review and update robots.txt cache
- Validate all active sources

**As Needed:**
- Update when adding new sources
- Respond to robots.txt changes
- Handle 429/503 rate limit errors

### Contact

For questions about ethical scraping implementation:
1. Review this documentation
2. Check `ETHICAL_COMPLIANCE_REPORT.md`
3. Review source-specific configs in `sources/active/`

---

**Last Compliance Audit:** October 8, 2025
**Status:** All active sources compliant
**Next Review:** January 2026
