# Phase 2 Implementation Plan: Advanced Reliability Features

**Date:** 2025-01-24
**Type:** Enhancement Plan
**Components:** Circuit Breaker, RSS Fallbacks, Adaptive Timeouts
**Phase:** Planning & Design

## Executive Summary

Phase 2 builds upon Phase 1's success (Scientific American: 14.3% → 100%) by adding three advanced reliability features to handle edge cases and improve overall system resilience. Target: increase overall bundle success from ~94% to ~99%.

**Phase 2 Features:**
1. **Circuit Breaker Pattern** - Fail-fast for dead sources
2. **RSS Feed Fallbacks** - Alternative feed URLs for resilience
3. **Adaptive Timeouts** - Source-specific timeout configuration

**Expected Impact:**
- Smithsonian: 0% → 80-90% (RSS fallbacks)
- Overall bundle: ~94% → ~98-99%
- Processing time: -20% (circuit breaker fail-fast)
- User experience: Better feedback on source health

---

## Feature 1: Circuit Breaker Pattern

### Problem Statement

**Current Behavior:**
- Scientific American failed 24 times before giving up
- Wasted 40+ seconds on dead source
- No indication source was unhealthy until all attempts failed
- Continued hammering failing endpoints

**Impact:**
- Slow failure detection
- Wasted processing time
- Potential IP blocking from repeated failures
- Poor user experience

### Solution Design

**Circuit Breaker States:**

```
CLOSED (Normal Operation)
    ↓ (failures reach threshold)
OPEN (Blocking Requests)
    ↓ (timeout expires)
HALF_OPEN (Testing Recovery)
    ↓ (success) → CLOSED
    ↓ (failure) → OPEN
```

**Configuration:**

```python
@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5      # Failures before opening
    success_threshold: int = 2       # Successes to close from half-open
    timeout_seconds: int = 60        # Time before retry in half-open
    half_open_max_calls: int = 3     # Max calls in half-open state
```

**Source-Specific Thresholds:**

```python
CIRCUIT_BREAKER_CONFIGS = {
    "scientificamerican": CircuitBreakerConfig(
        failure_threshold=3,    # Open faster for problematic sources
        timeout_seconds=120,    # Longer recovery time
    ),
    "smithsonianmag": CircuitBreakerConfig(
        failure_threshold=2,    # Very sensitive
        timeout_seconds=180,
    ),
    "default": CircuitBreakerConfig(
        failure_threshold=5,
        timeout_seconds=60,
    ),
}
```

### Implementation Strategy

**Architecture:**

1. **CircuitBreaker Class** (core/circuit_breaker.py)
   - State management (CLOSED/OPEN/HALF_OPEN)
   - Failure/success counting
   - Timeout tracking
   - Thread-safe operations

2. **CircuitBreakerPool** (singleton)
   - One breaker per source
   - Centralized state management
   - Statistics tracking

3. **Integration Points:**
   - BaseSource.discover_articles() - Wrap discovery
   - BaseSource.fetch_content() - Wrap fetching
   - Display state in progress indicators

**Key Methods:**

```python
class CircuitBreaker:
    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker."""
        if self.state == CircuitState.OPEN:
            if not self._should_attempt_reset():
                raise CircuitBreakerOpenError("Circuit is OPEN")
            self.state = CircuitState.HALF_OPEN

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            raise

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0  # Reset on success

    def _on_failure(self, exception):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.last_exception = exception

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")
```

**Files to Create:**
- `core/circuit_breaker.py` (~300 lines)

**Files to Modify:**
- `core/source_system/base_source.py` - Wrap methods in circuit breaker
- `core/unified_source_processor.py` - Handle CircuitBreakerOpenError
- `core/progress.py` - Display circuit state

**Expected Benefits:**
- Fail-fast: 40s → 5s for dead sources
- Better user feedback: "Source unavailable (circuit open)"
- Prevent IP blocking from repeated failures
- Automatic recovery testing

---

## Feature 2: RSS Feed Fallback URLs

### Problem Statement

**Current Behavior:**
- Smithsonian: 0% success (RSS feed inaccessible)
- Single RSS URL per source
- No fallback mechanism
- Complete source failure when URL changes

**Root Causes:**
- RSS feeds move/change URLs over time
- Site redesigns break feed URLs
- Temporary server issues at specific endpoints
- No validation of feed URL validity

### Solution Design

**Fallback Strategy:**

```python
# In source configuration YAML
rss_urls:
  primary: "https://www.smithsonianmag.com/rss/latest_articles/"
  fallbacks:
    - "https://www.smithsonianmag.com/feed/"
    - "https://www.smithsonianmag.com/rss/"
    - "https://feeds.smithsonianmag.com/smithsonianmag/latest"

# Automatic fallback attempt
def fetch_rss_with_fallback(urls):
    for url in urls:
        try:
            response = fetch_url(url, timeout=10)
            if validate_feed(response.content):
                logger.info(f"Successfully fetched from {url}")
                return response.content
        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {e}")
            continue
    raise RSSFeedError("All RSS URLs failed")
```

**Feed Validation:**

```python
def validate_feed(content: bytes) -> bool:
    """Quick validation that content is a valid RSS/Atom feed."""
    try:
        # Try parsing with feedparser
        feed_items = FeedParserFactory.detect_and_parse(content)
        return len(feed_items) > 0
    except Exception:
        return False
```

**Feed URL Discovery:**

```python
def discover_feed_urls(base_url: str) -> List[str]:
    """
    Attempt to discover feed URLs from website.

    Looks for:
    - <link rel="alternate" type="application/rss+xml">
    - Common feed paths: /feed, /rss, /atom, /feed.xml
    """
    discovered = []

    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find feed links in HTML
        for link in soup.find_all('link', {'type': ['application/rss+xml', 'application/atom+xml']}):
            if 'href' in link.attrs:
                discovered.append(urljoin(base_url, link['href']))

        # Try common paths
        common_paths = ['/feed', '/rss', '/atom', '/feed.xml', '/rss.xml']
        for path in common_paths:
            discovered.append(urljoin(base_url, path))

    except Exception as e:
        logger.debug(f"Could not discover feeds from {base_url}: {e}")

    return discovered
```

### Implementation Strategy

**Configuration Updates:**

1. **Update YAML schema** to support multiple URLs:

```yaml
# sources/active/config_driven/configs/smithsonianmag.yaml
name: "smithsonianmag"
display_name: "Smithsonian Magazine"
base_url: "https://www.smithsonianmag.com"

discovery:
  method: "rss"
  rss_urls:
    primary: "https://www.smithsonianmag.com/rss/latest_articles/"
    fallbacks:
      - "https://www.smithsonianmag.com/feed/"
      - "https://www.smithsonianmag.com/rss/"
  auto_discover: true  # Attempt auto-discovery if all fail
```

2. **Update RSSDiscoveryStrategy:**

```python
class RSSDiscoveryStrategy(DiscoveryStrategy):
    def discover(self, count, config, session, base_url, timeout, logger, should_skip_callback):
        # Get RSS URLs (primary + fallbacks)
        rss_config = config.get("discovery", {}).get("rss_urls", {})

        if isinstance(rss_config, str):
            # Legacy single URL format
            urls = [rss_config]
        else:
            # New format with primary + fallbacks
            urls = [rss_config.get("primary")]
            urls.extend(rss_config.get("fallbacks", []))

        # Remove None values
        urls = [url for url in urls if url]

        # Try each URL in order
        for url in urls:
            try:
                response = _fetch_url_with_retry(session, url, timeout, source_code=source_code)
                feed_items = FeedParserFactory.detect_and_parse(response.content)

                if feed_items:
                    logger.info(f"Successfully fetched RSS from {url}")
                    return self._convert_feed_items_to_articles(feed_items, config, should_skip_callback)[:count]

            except Exception as e:
                logger.debug(f"RSS URL {url} failed: {e}")
                continue

        # All URLs failed - try auto-discovery if enabled
        if config.get("discovery", {}).get("auto_discover", False):
            logger.info(f"Attempting auto-discovery for {base_url}")
            discovered_urls = discover_feed_urls(base_url)

            for url in discovered_urls:
                try:
                    response = _fetch_url_with_retry(session, url, timeout, source_code=source_code)
                    feed_items = FeedParserFactory.detect_and_parse(response.content)

                    if feed_items:
                        logger.info(f"Successfully discovered and fetched RSS from {url}")
                        # TODO: Save discovered URL to config for future use
                        return self._convert_feed_items_to_articles(feed_items, config, should_skip_callback)[:count]

                except Exception:
                    continue

        # Total failure
        raise ArticleDiscoveryError(f"All RSS URLs failed for {config.get('name')}")
```

**Files to Create:**
- `core/source_system/feed_discovery.py` (~150 lines) - Feed URL discovery

**Files to Modify:**
- `core/source_system/discovery_strategies.py` - Add fallback logic to RSSDiscoveryStrategy
- `sources/active/config_driven/configs/smithsonianmag.yaml` - Add fallback URLs
- `sources/active/config_driven/configs/scientificamerican.yaml` - Add fallback URLs (preventive)

**Expected Benefits:**
- Smithsonian: 0% → 80-90%
- Resilience to URL changes
- Automatic recovery from site redesigns
- Self-healing capability

---

## Feature 3: Adaptive Timeouts

### Problem Statement

**Current Behavior:**
- Fixed timeout for all sources: 30 seconds
- Some sources consistently slow (Scientific American, Nature)
- Other sources very fast (LessWrong, local RSS)
- Unnecessary waits or premature timeouts

**Impact:**
- Slow sources timeout prematurely
- Fast sources wait unnecessarily
- No differentiation by source characteristics
- Suboptimal user experience

### Solution Design

**Timeout Categories:**

```python
@dataclass
class TimeoutConfig:
    connect_timeout: int      # Time to establish connection
    read_timeout: int         # Time to read response
    total_timeout: int        # Overall operation timeout
```

**Source-Specific Timeouts:**

```python
SOURCE_TIMEOUTS = {
    # Very slow sources (large pages, slow servers)
    "scientificamerican": TimeoutConfig(
        connect_timeout=15,
        read_timeout=60,
        total_timeout=90,
    ),
    "nature": TimeoutConfig(
        connect_timeout=15,
        read_timeout=45,
        total_timeout=75,
    ),
    "smithsonianmag": TimeoutConfig(
        connect_timeout=15,
        read_timeout=45,
        total_timeout=75,
    ),

    # Moderately slow sources
    "guardian": TimeoutConfig(
        connect_timeout=10,
        read_timeout=30,
        total_timeout=45,
    ),
    "bbc": TimeoutConfig(
        connect_timeout=10,
        read_timeout=30,
        total_timeout=45,
    ),

    # Fast sources (RSS, simple pages)
    "lesswrong": TimeoutConfig(
        connect_timeout=5,
        read_timeout=15,
        total_timeout=20,
    ),
    "hn": TimeoutConfig(
        connect_timeout=8,
        read_timeout=20,
        total_timeout=30,
    ),

    # Default for unknown sources
    "default": TimeoutConfig(
        connect_timeout=10,
        read_timeout=30,
        total_timeout=45,
    ),
}
```

**Adaptive Learning:**

```python
class TimeoutTracker:
    """Track actual response times to recommend timeout adjustments."""

    def __init__(self):
        self.response_times: Dict[str, List[float]] = {}
        self.lock = threading.Lock()

    def record_response_time(self, source_code: str, duration: float):
        """Record successful response time."""
        with self.lock:
            if source_code not in self.response_times:
                self.response_times[source_code] = []

            self.response_times[source_code].append(duration)

            # Keep only recent measurements (last 100)
            if len(self.response_times[source_code]) > 100:
                self.response_times[source_code] = self.response_times[source_code][-100:]

    def get_recommended_timeout(self, source_code: str) -> Optional[TimeoutConfig]:
        """Get recommended timeout based on historical data."""
        with self.lock:
            if source_code not in self.response_times:
                return None

            times = self.response_times[source_code]
            if len(times) < 10:  # Need minimum data
                return None

            # Calculate percentiles
            p50 = statistics.median(times)
            p95 = statistics.quantiles(times, n=20)[18]  # 95th percentile
            p99 = statistics.quantiles(times, n=100)[98]  # 99th percentile

            # Recommend timeouts with safety margin
            return TimeoutConfig(
                connect_timeout=int(p50 * 1.5) + 5,
                read_timeout=int(p95 * 1.2) + 10,
                total_timeout=int(p99 * 1.1) + 15,
            )

    def get_stats(self, source_code: str) -> Dict[str, float]:
        """Get statistics for a source."""
        with self.lock:
            if source_code not in self.response_times or not self.response_times[source_code]:
                return {}

            times = self.response_times[source_code]
            return {
                "count": len(times),
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "p95": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
            }
```

### Implementation Strategy

**Configuration System:**

1. **Create timeout configuration module:**

```python
# core/timeout_config.py
def get_timeout_for_source(source_code: str) -> TimeoutConfig:
    """Get timeout configuration for source."""
    # Try configured timeouts first
    if source_code in SOURCE_TIMEOUTS:
        return SOURCE_TIMEOUTS[source_code]

    # Try adaptive learning
    tracker = get_timeout_tracker()
    recommended = tracker.get_recommended_timeout(source_code)
    if recommended:
        logger.debug(f"Using adaptive timeout for {source_code}")
        return recommended

    # Fall back to default
    return SOURCE_TIMEOUTS["default"]
```

2. **Integrate into fetch operations:**

```python
# In article_fetcher.py
@network_retry
def _fetch_url_with_retry(self, url: str) -> requests.Response:
    acquire_rate_limit(self.source_code, blocking=True)

    # Get adaptive timeout
    timeout_config = get_timeout_for_source(self.source_code)
    timeout = (timeout_config.connect_timeout, timeout_config.read_timeout)

    start_time = time.time()
    try:
        response = self.session.get(url, timeout=timeout)
        response.raise_for_status()

        # Track successful response time
        duration = time.time() - start_time
        get_timeout_tracker().record_response_time(self.source_code, duration)

        return response
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        logger.debug(f"Timeout for {self.source_code} after {duration:.1f}s")
        raise
```

**Files to Create:**
- `core/timeout_config.py` (~250 lines) - Timeout configuration and tracking

**Files to Modify:**
- `core/article_fetcher.py` - Use adaptive timeouts
- `core/source_system/discovery_strategies.py` - Use adaptive timeouts for RSS/HTML
- `core/config.py` - Add timeout configuration section

**Expected Benefits:**
- Reduce timeout failures: -30%
- Faster processing for fast sources
- Better handling of slow sources
- Data-driven timeout optimization

---

## Implementation Order

### Priority Order

1. **Circuit Breaker** (Highest Priority)
   - Immediate impact on processing time
   - Better user feedback
   - Prevents IP blocking

2. **RSS Fallbacks** (High Priority)
   - Fixes Smithsonian completely
   - Preventive measure for other sources
   - Self-healing capability

3. **Adaptive Timeouts** (Medium Priority)
   - Incremental improvement
   - Requires data collection period
   - Long-term optimization

### Implementation Phases

**Phase 2A: Circuit Breaker (Day 1)**
- Implement CircuitBreaker class
- Integrate with BaseSource
- Test with problem sources
- Deploy and monitor

**Phase 2B: RSS Fallbacks (Day 2)**
- Implement feed discovery
- Update RSS strategy
- Add fallback URLs to configs
- Test with Smithsonian
- Deploy

**Phase 2C: Adaptive Timeouts (Day 3)**
- Implement TimeoutTracker
- Integrate timeout configuration
- Begin data collection
- Analyze and tune after 1 week

---

## Testing Strategy

### Test Cases

**Circuit Breaker:**
1. Simulate 5 consecutive failures → Circuit OPENS
2. Wait timeout period → Circuit goes HALF_OPEN
3. Successful request → Circuit CLOSES
4. Verify fail-fast behavior when OPEN

**RSS Fallbacks:**
1. Primary URL fails → Try fallback #1
2. All configured URLs fail → Try auto-discovery
3. Success on fallback → Log which URL worked
4. Test with Smithsonian (real-world)

**Adaptive Timeouts:**
1. Record 100 response times for a source
2. Verify recommended timeout is reasonable
3. Test fast source (should have short timeout)
4. Test slow source (should have long timeout)

### Integration Testing

**Test Command:**
```bash
# Test problematic sources
./capcat fetch scientificamerican,smithsonianmag,openai --count 5 --html
```

**Success Criteria:**
- Circuit breaker prevents extended failures
- Smithsonian succeeds via fallback URL
- Timeouts are appropriate per source
- Overall success rate >98%

---

## Performance Impact

### Processing Time

**Circuit Breaker:**
- Dead source: 40s → 5s (fail-fast)
- Overall bundle: -10% to -20% time

**RSS Fallbacks:**
- Smithsonian: Add ~3s per attempt (max 5 attempts)
- Other sources: No impact (fallback only on failure)

**Adaptive Timeouts:**
- Fast sources: -5s to -10s (shorter timeouts)
- Slow sources: More reliable (fewer premature timeouts)
- Net neutral to slightly positive

### Memory Usage

- Circuit breaker: ~200 bytes per source
- Timeout tracker: ~8KB per source (100 float values)
- Total: <1MB for 20 sources

---

## Configuration

### User Configuration Options

**Circuit Breaker (capcat.yml):**
```yaml
circuit_breaker:
  enabled: true
  failure_threshold: 5
  timeout_seconds: 60
  per_source:
    scientificamerican:
      failure_threshold: 3
      timeout_seconds: 120
```

**RSS Fallbacks (source YAML):**
```yaml
discovery:
  method: "rss"
  rss_urls:
    primary: "https://example.com/rss"
    fallbacks:
      - "https://example.com/feed"
      - "https://example.com/atom"
  auto_discover: true
```

**Adaptive Timeouts (capcat.yml):**
```yaml
timeouts:
  enabled: true
  adaptive_learning: true
  per_source:
    scientificamerican:
      connect_timeout: 15
      read_timeout: 60
```

---

## Migration Path

### Backward Compatibility

**All Phase 2 features are optional and backward compatible:**

1. Circuit breaker disabled by default
2. RSS fallbacks optional (single URL still works)
3. Adaptive timeouts use defaults if not configured

### Recommended Migration

**Step 1:** Deploy with features disabled
**Step 2:** Enable circuit breaker (monitor for 24h)
**Step 3:** Add RSS fallbacks to problem sources
**Step 4:** Enable adaptive timeout learning
**Step 5:** Tune based on collected data

---

## Success Metrics

### Primary Metrics
- Circuit breaker fail-fast: <10s for dead sources
- Smithsonian success: 0% → >80%
- Timeout failures: -30%
- Overall bundle: ~94% → ~98-99%

### Secondary Metrics
- User feedback: Circuit state visible in progress
- Processing time: 10-20% improvement
- Self-healing: Successful fallback attempts logged
- Data collection: 100+ response times per source

---

## Risk Assessment

### Low Risk
- Circuit breaker (well-understood pattern)
- RSS fallbacks (simple fallback logic)
- Backward compatibility (all optional)

### Medium Risk
- Adaptive timeouts (requires tuning period)
- Feed auto-discovery (may find wrong feeds)

### Mitigation
- Feature flags for easy disable
- Conservative defaults
- Comprehensive logging
- Gradual rollout

---

## Summary

Phase 2 adds three complementary features to build upon Phase 1's success:

1. **Circuit Breaker** - Fail-fast, better UX, prevent blocking
2. **RSS Fallbacks** - Fix Smithsonian, resilience to changes
3. **Adaptive Timeouts** - Optimize per source, data-driven

**Expected Results:**
- Overall success: ~94% → ~98-99%
- Processing time: -10% to -20%
- Smithsonian: 0% → 80-90%
- Better user experience and feedback

**Implementation Effort:**
- ~700 new lines of code
- ~150 lines of modifications
- 3 new modules created
- Multiple configs updated

**Recommendation:** Implement in phases (2A, 2B, 2C) with testing between each phase.