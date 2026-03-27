# Capcat Debug Tools

Debug toolkit for diagnosing content extraction issues, bot protection, and source configuration problems.

## Quick Diagnosis (Start Here)

The three errors you're seeing have clear causes:

### 1. Empty Markdown Warnings
```
WARNING: Empty markdown for https://percepta.ai/blog/constructing-llm-computer
WARNING: Empty markdown for https://ahwoo.com/news/.../planetary-rings
```

**Cause:** HTML was fetched but content extraction yielded no usable text
**Why:** Content extraction selectors don't match current site structure

### 2. Access Forbidden Warnings
```
WARNING: Access forbidden for article https://www.forbes.com/.../google-just-patented... - anti-bot protection detected
```

**Cause:** Site is blocking Capcat with anti-bot protection (Cloudflare/CAPTCHA)
**Why:** Forbes has aggressive bot detection

### 3. Content Fetch Failed Warnings
```
WARNING: Content fetch failed for: Constructing an LLM-Computer
```

**Cause:** Downstream failure from empty content extraction
**Why:** If markdown is empty, article processing fails

## Debug Tools

### 1. Quick Troubleshoot (Immediate Diagnosis)
```bash
python3 debug/quick-troubleshoot.py
```
Tests the three failing URLs and provides immediate recommendations.

### 2. Content Extraction Debugger (Deep Analysis)
```bash
python3 debug/content-extraction-debugger.py <URL>
```
Comprehensive analysis of why content extraction fails for a URL:
- Tests connectivity and headers
- Finds source configuration
- Analyzes HTML structure
- Tests extraction patterns
- Checks for anti-bot protection

### 3. Source Configuration Tester
```bash
python3 debug/source-tester.py <source-id>
python3 debug/source-tester.py  # Test all sources
```
Tests source configurations:
- RSS feed accessibility
- Extraction selector validation
- Sample article testing
- Suggests alternative selectors

### 4. Log Analyzer
```bash
python3 debug/log-analyzer.py [log-file]
python3 debug/log-analyzer.py --recommendations
```
Analyzes Capcat logs for patterns:
- Categorizes error types
- Identifies failing domains
- Generates recommendations
- Timeline analysis

## Common Solutions

### Empty Markdown Issues
1. **Update extraction selectors**: Sites change their HTML structure
2. **Check for dynamic content**: Some sites load content via JavaScript
3. **Verify source configuration**: Ensure selectors match current structure

### Access Forbidden Issues
1. **Implement request delays**: Add delays between requests
2. **Rotate user agents**: Use different browser identities
3. **Consider headless browser**: For JavaScript-heavy sites
4. **Respect robots.txt**: Some sites explicitly block scrapers

### General Troubleshooting
1. **Check internet connectivity**
2. **Verify DNS resolution**
3. **Test with different user agents**
4. **Monitor rate limiting**

## Understanding the Output

### Quick Troubleshoot Results
- ✅ OK: Site is accessible and has content
- ❌ PROBLEM: Site has issues (protection, low content, errors)
- 🛡️: Anti-bot protection detected
- 📝: Low content (extraction issue)

### Content Words Threshold
- **>200 words**: Likely good content
- **50-200 words**: May be partial content or summary
- **<50 words**: Likely extraction failure or blocked content

## Next Steps

1. **Run quick troubleshoot** to confirm current status
2. **For empty markdown**: Use content extraction debugger to analyze selectors
3. **For access forbidden**: Implement delays and different user agents
4. **Update source configs** based on analysis recommendations

## Manual Testing

Test a source manually:
```bash
# Test specific source
python3 -c "
import sys
sys.path.insert(0, 'capcat')
from capcat.cli import run_app
run_app(['fetch', 'percepta-ai', '--count', '1', '--verbose'])
"
```

## Production Monitoring

Set up monitoring for these warning patterns:
```bash
# Monitor logs for patterns
tail -f /path/to/capcat.log | grep -E "WARNING: (Empty markdown|Access forbidden|Content fetch failed)"
```

The debug tools will help you identify exactly why each source is failing and provide specific fixes.