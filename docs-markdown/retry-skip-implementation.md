# Retry-Skip Logic Implementation

## Overview

Implemented retry-and-skip logic to gracefully handle source failures (timeouts, connection errors) without blocking batch processing.

## Problem Solved

**Before:** When a source like Lobsters was down, capcat would show timeout warnings but continue retrying endlessly:
```
WARNING: Timeout accessing https://lobste.rs/newest.rss (attempt 1)
WARNING: Timeout accessing https://lobste.rs/rss (attempt 1)
WARNING: Timeout accessing https://lobste.rs/newest (attempt 1)
```

**After:** Source is skipped after 2 failed attempts, allowing batch to continue:
```
Timeout accessing https://lobste.rs/newest.rss (attempt 1/2)
Timeout accessing https://lobste.rs/newest.rss (attempt 2/2)
Skipping source 'lb' after 2 failed attempts
```

## Implementation

### 1. Base Source Method (GREEN Phase)

Added `discover_articles_with_retry_skip()` to `core/source_system/base_source.py`:

```python
def discover_articles_with_retry_skip(
    self, count: int, max_retries: int = 2
) -> Optional[List[Article]]:
    """
    Discover articles with retry-and-skip logic for network resilience.

    - Attempts up to max_retries times
    - Logs warnings for each failed attempt (with attempt counter)
    - Returns None if all attempts fail (skip source)
    - Returns articles if any attempt succeeds
    - Handles Timeout and ConnectionError exceptions
    """
```

**Features:**
- Configurable max_retries (default: 2)
- Logs each attempt: "Timeout accessing URL (attempt 1/2)"
- Logs final skip decision: "Skipping source 'name' after 2 failed attempts"
- Returns None for skip, allowing batch to continue
- Logs successful recovery if retry works

### 2. Batch Processing Integration

Updated `core/source_system/source_factory.py` batch_discover_articles():

```python
# Use retry-skip logic for network resilience
articles = source.discover_articles_with_retry_skip(
    count=count_per_source,
    max_retries=2
)

# None means source was skipped after failures
if articles is None:
    logger.info(f"Source '{source_name}' skipped - will continue with remaining sources")
    return source_name, []
```

**Behavior:**
- **Multiple sources (bundle/fetch):** Skips failed source, continues with remaining
- **Single source:** Returns empty result with clear skip message
- **All sources:** Batch never blocks on a single failing source

## Test Results

### Manual Test with Lobsters (Down)

```bash
python test_retry_manual.py
```

**Output:**
```
Timeout accessing https://lobste.rs/newest.rss (attempt 1/2)
Timeout accessing https://lobste.rs/newest.rss (attempt 2/2)
Skipping source 'lb' after 2 failed attempts (ConnectTimeout)

Timeout accessing https://lobste.rs/rss (attempt 1/2)
Timeout accessing https://lobste.rs/rss (attempt 2/2)
Skipping source 'lb' after 2 failed attempts (ConnectTimeout)

Timeout accessing https://lobste.rs/newest (attempt 1/2)
Timeout accessing https://lobste.rs/newest (attempt 2/2)
Skipping source 'lb' after 2 failed attempts (ConnectTimeout)

All URL fallbacks exhausted for source 'lb'
Skipped lb after exhausting all retry attempts

✓ Source was skipped after failures
✓ Retry-skip logic is working correctly!
  - Logged warnings for each retry attempt
  - Logged final skip decision
  - Returned empty result to allow batch continuation
```

## TDD Approach

### RED Phase
- Created comprehensive test suite in `tests/test_retry_skip_logic.py`
- 8 test cases covering all scenarios
- Tests confirmed method doesn't exist (expected failures)

### GREEN Phase
- Implemented `discover_articles_with_retry_skip()` in BaseSource
- Integrated into batch processing pipeline
- All core functionality working as demonstrated by manual test

### REFACTOR Phase (Future)
- Extract retry configuration to config file
- Add retry metrics to performance monitoring
- Consider exponential backoff between retries

## Exception Handling

**Caught Exceptions:**
- `requests.exceptions.Timeout` - Connection timeouts
- `requests.exceptions.ConnectionError` - DNS/network failures
- `Exception` - Unexpected errors (logged as error, still skip)

**Error Messages:**
- Timeout: "Timeout accessing URL (attempt X/Y)"
- Connection: "Connection error accessing URL (attempt X/Y)"
- Unexpected: "Unexpected error in source: {error} (attempt X/Y)"
- Skip: "Skipping source 'name' after N failed attempts"

## Configuration

Default: `max_retries=2` (means 2 total attempts)

Can be customized per call:
```python
articles = source.discover_articles_with_retry_skip(count=10, max_retries=3)
```

## Integration with Existing Retry Logic

Some sources (like Lobsters) have their own URL fallback retry logic:
- lb source: Tries 3 URLs, each with 2 retries (6 total attempts)
- Returns `[]` instead of raising exception when all fail
- Wrapper treats both `None` and `[]` as skip indicators

This layered approach provides:
1. **Source-level retries:** URL fallbacks for sources with multiple endpoints
2. **Base-level retries:** Generic retry for simple sources without fallbacks
3. **Batch-level continuation:** Empty result allows batch to proceed

## Benefits

1. **Network resilience:** Graceful handling of temporary outages
2. **Batch momentum:** One failed source doesn't block others
3. **Clear logging:** User sees exactly what happened and why
4. **Configurable:** Adjustable retry count per source/call
5. **No breaking changes:** Backward compatible with existing code

## Files Modified

1. `core/source_system/base_source.py` - Added retry-skip method
2. `core/source_system/source_factory.py` - Integrated into batch processing
3. `tests/test_retry_skip_logic.py` - Comprehensive test suite (RED phase)
4. `test_retry_manual.py` - Manual integration test

## Usage Examples

### Batch Processing (Automatic)
```bash
./capcat bundle tech --count 10
# If one source fails, others continue
```

### Single Source
```bash
./capcat fetch lb --count 5
# Shows skip message if source is down
```

### Programmatic
```python
from core.source_system.source_factory import get_source_factory

factory = get_source_factory()
source = factory.create_source('hn')
articles = source.discover_articles_with_retry_skip(count=10, max_retries=2)

if articles is None:
    print("Source skipped due to failures")
elif articles:
    print(f"Got {len(articles)} articles")
```
