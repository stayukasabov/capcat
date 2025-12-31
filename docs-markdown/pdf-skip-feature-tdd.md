# PDF Download Skip Feature - TDD Implementation

## Overview

Implemented PDF download skip feature using strict Test-Driven Development methodology. Feature allows users to skip downloading large PDF files (>5MB) by pressing ESC within 20 seconds.

## TDD Process Summary

### RED Phase (Tests First)

Created comprehensive test suite in `tests/test_pdf_skip_prompt.py` with 11 test cases:

1. `test_check_pdf_size_small_file` - Small PDFs proceed without prompt
2. `test_check_pdf_size_large_file_user_skips` - Large PDFs with ESC press skip
3. `test_check_pdf_size_large_file_timeout` - Large PDFs without ESC proceed
4. `test_check_pdf_size_head_request_fails` - HEAD failures proceed safely
5. `test_check_pdf_size_no_content_length_header` - Missing header proceeds
6. `test_prompt_user_skip_esc_pressed` - ESC key detection works
7. `test_prompt_user_skip_timeout` - Timeout behavior correct
8. `test_fetch_web_content_skips_pdf_on_esc` - Integration: skip on ESC
9. `test_fetch_web_content_downloads_pdf_on_timeout` - Integration: proceed on timeout
10. `test_fetch_web_content_non_pdf_bypasses_check` - Non-PDFs bypass check
11. `test_constants_defined` - Required constants exist

All tests initially failed (RED phase confirmed).

### GREEN Phase (Minimal Implementation)

Implemented minimal code to pass all tests:

**1. Added Dependencies**
- Added `pynput>=1.7.6` to `requirements.txt`
- Installed keyboard listener library

**2. Added Constants** (`core/article_fetcher.py:38-41`)
```python
LARGE_PDF_THRESHOLD_MB = 5
SKIP_PROMPT_TIMEOUT_SECONDS = 20
BYTES_TO_MB = 1024 * 1024
```

**3. Added Imports** (`core/article_fetcher.py:9-19`)
```python
import sys
import threading
from pynput import keyboard
```

**4. Implemented `_check_pdf_size_and_prompt()`** (`core/article_fetcher.py:551-610`)
- Makes HEAD request to get Content-Length
- Converts bytes to MB
- Returns False for small files (< 5MB)
- Calls `_prompt_user_skip()` for large files
- Handles errors gracefully (proceeds on failure)

**5. Implemented `_prompt_user_skip()`** (`core/article_fetcher.py:612-662`)
- Starts keyboard listener in background thread
- Displays countdown prompt (20 seconds)
- Listens for ESC key press
- Returns True if ESC pressed, False on timeout
- Cleans up listener properly

**6. Integrated with `_fetch_web_content()`** (`core/article_fetcher.py:663-668`)
```python
# Check for PDF files and prompt user for large files
if url.lower().endswith('.pdf'):
    should_skip = self._check_pdf_size_and_prompt(url, title)
    if should_skip:
        self.logger.info(f"User skipped PDF download: {title}")
        return False, None, None
```

All 11 tests passed after implementation.

### REFACTOR Phase (Code Quality)

Applied code improvements while maintaining green tests:

**1. Extracted Magic Numbers**
- Created `BYTES_TO_MB` constant for 1024 * 1024
- Used constant in size calculation

**2. Removed Unused Code**
- Removed `start_time` variable (was not used)

**3. Improved Exception Handling**
- Split generic Exception into specific catches:
  - `ValueError, KeyError` for invalid headers
  - `requests.exceptions.RequestException` for network errors
  - Generic `Exception` as fallback
- Better error messages for each case

**4. Maintained Test Coverage**
- All 11 tests still passing after refactoring
- No regressions in existing functionality

## Test Results

### Final Test Run
```
tests/test_pdf_skip_prompt.py::TestPDFSkipPrompt::test_check_pdf_size_head_request_fails PASSED
tests/test_pdf_skip_prompt.py::TestPDFSkipPrompt::test_check_pdf_size_large_file_timeout PASSED
tests/test_pdf_skip_prompt.py::TestPDFSkipPrompt::test_check_pdf_size_large_file_user_skips PASSED
tests/test_pdf_skip_prompt.py::TestPDFSkipPrompt::test_check_pdf_size_no_content_length_header PASSED
tests/test_pdf_skip_prompt.py::TestPDFSkipPrompt::test_check_pdf_size_small_file PASSED
tests/test_pdf_skip_prompt.py::TestPDFSkipPrompt::test_fetch_web_content_downloads_pdf_on_timeout PASSED
tests/test_pdf_skip_prompt.py::TestPDFSkipPrompt::test_fetch_web_content_non_pdf_bypasses_check PASSED
tests/test_pdf_skip_prompt.py::TestPDFSkipPrompt::test_fetch_web_content_skips_pdf_on_esc PASSED
tests/test_pdf_skip_prompt.py::TestPDFSkipPrompt::test_prompt_user_skip_esc_pressed PASSED
tests/test_pdf_skip_prompt.py::TestPDFSkipPrompt::test_prompt_user_skip_timeout PASSED
tests/test_pdf_skip_prompt.py::TestPDFSkipConstants::test_constants_defined PASSED

11 passed in 2.26s
```

## Feature Behavior

### User Experience

When Capcat encounters a PDF URL during article fetching:

1. **Small PDF (< 5MB)**: Downloads immediately, no prompt
2. **Large PDF (>= 5MB)**:
   - Shows prompt: "Large PDF detected (X.X MB): [title]"
   - Shows countdown: "Press ESC within 20 seconds to skip..."
   - Updates countdown every second: "20 seconds remaining... 19... 18..."
   - If ESC pressed: "Skipping PDF download." (article skipped)
   - If timeout: "Proceeding with PDF download." (downloads PDF)

### Error Handling

Feature fails safely in all error cases:
- HEAD request fails → proceeds with download
- Missing Content-Length header → proceeds with download
- Invalid Content-Length value → proceeds with download
- Network errors → proceeds with download

This ensures the feature never blocks article fetching.

## Implementation Files

### Core Implementation
- `core/article_fetcher.py` (lines 9-19, 38-41, 551-668)
  - Added imports and constants
  - Implemented `_check_pdf_size_and_prompt()`
  - Implemented `_prompt_user_skip()`
  - Integrated with `_fetch_web_content()`

### Test Suite
- `tests/test_pdf_skip_prompt.py` (390 lines)
  - 11 comprehensive test cases
  - Mock-based testing for keyboard input
  - Integration tests for `_fetch_web_content()`

### Dependencies
- `requirements.txt` (added `pynput>=1.7.6`)

## Configuration

Constants can be modified in `core/article_fetcher.py`:

```python
LARGE_PDF_THRESHOLD_MB = 5              # File size threshold
SKIP_PROMPT_TIMEOUT_SECONDS = 20        # Countdown duration
BYTES_TO_MB = 1024 * 1024              # Conversion factor
```

## Usage

Feature activates automatically when:
1. URL ends with `.pdf`
2. File size >= 5MB (determined via HEAD request)

No configuration or command-line flags required.

## Testing

Run test suite:
```bash
source venv/bin/activate
python -m pytest tests/test_pdf_skip_prompt.py -v
```

Run with coverage:
```bash
python -m pytest tests/test_pdf_skip_prompt.py --cov=core.article_fetcher --cov-report=term
```

## TDD Lessons Applied

1. **Write Tests First**: All 11 tests written before implementation
2. **Red-Green-Refactor**: Followed strict TDD cycle
3. **Minimal Implementation**: Only wrote code to pass tests
4. **Refactor Safely**: Improved code quality while maintaining green tests
5. **Test Edge Cases**: Covered error scenarios, boundary conditions
6. **Integration Tests**: Verified feature works in context
7. **Mock External Dependencies**: Used mocks for keyboard, network I/O
8. **Fast Tests**: Mocked time.sleep for quick test execution

## Future Enhancements

Potential improvements (would require new tests first):

1. Configuration options in `capcat.yml`:
   - Adjustable threshold size
   - Adjustable timeout duration
   - Disable feature flag

2. Different key options:
   - Multiple keys (ESC, Q, N)
   - Configurable skip key

3. Progress indicator:
   - Visual progress bar
   - Estimated download time

4. Batch mode handling:
   - "Skip all large PDFs" option
   - "Remember choice" for session
