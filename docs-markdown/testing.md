# Testing Guide

Comprehensive testing procedures and standards for Capcat's hybrid architecture.

## Testing Philosophy

Capcat follows **systematic testing standards** with mandatory procedures for all testing tasks:

1. **Complete Coverage**: Test ALL supported sources, not random subsets
2. **Mandatory Documentation**: Create test-diagnose files for EVERY test
3. **Systematic Analysis**: Read all results and create prioritized fix plans
4. **Universal Success Criteria**: Different criteria for sources vs components vs features

## Testing Types

### 1. Source Testing
**Purpose**: Validate individual source functionality
**Scope**: All 20 production sources
**Frequency**: Before deployment, after changes

### 2. Component Testing
**Purpose**: Validate core system components
**Scope**: Registry, factory, monitor, validation engine
**Frequency**: After component changes

### 3. Integration Testing
**Purpose**: Validate end-to-end workflows
**Scope**: Full system functionality
**Frequency**: Before major releases

### 4. Performance Testing
**Purpose**: Validate system performance characteristics
**Scope**: Speed, memory usage, network efficiency
**Frequency**: Regular monitoring

## Source Testing Procedures

### Mandatory Source Testing Protocol

**MANDATORY**: For ALL source testing tasks, follow this systematic procedure:

#### 1. Pre-Test Setup
```bash
# Activate environment
source venv/bin/activate

# Verify source discovery
python -c "from core.source_system.source_registry import get_source_registry; print(f'{len(get_source_registry().get_available_sources())} sources discovered')"
```

#### 2. Individual Source Testing
Test each source individually with diagnosis file creation:

```bash
# Test each source with output capture
./capcat fetch hn --count 10 2>&1 | tee test-diagnose-hn.txt
./capcat fetch lb --count 10 2>&1 | tee test-diagnose-lb.txt
./capcat fetch iq --count 10 2>&1 | tee test-diagnose-iq.txt
./capcat fetch bbc --count 10 2>&1 | tee test-diagnose-bbc.txt
./capcat fetch cnn --count 10 2>&1 | tee test-diagnose-cnn.txt
./capcat fetch techcrunch --count 10 2>&1 | tee test-diagnose-techcrunch.txt
./capcat fetch theverge --count 10 2>&1 | tee test-diagnose-theverge.txt
./capcat fetch wired --count 10 2>&1 | tee test-diagnose-wired.txt
./capcat fetch nature --count 10 2>&1 | tee test-diagnose-nature.txt
./capcat fetch scientificamerican --count 10 2>&1 | tee test-diagnose-scientificamerican.txt
./capcat fetch mittechreview --count 10 2>&1 | tee test-diagnose-mittechreview.txt
./capcat fetch gizmodo --count 10 2>&1 | tee test-diagnose-gizmodo.txt
./capcat fetch upi --count 10 2>&1 | tee test-diagnose-upi.txt
./capcat fetch tass --count 10 2>&1 | tee test-diagnose-tass.txt
./capcat fetch straitstimes --count 10 2>&1 | tee test-diagnose-straitstimes.txt
./capcat fetch euronews --count 10 2>&1 | tee test-diagnose-euronews.txt
./capcat fetch axios --count 10 2>&1 | tee test-diagnose-axios.txt
./capcat fetch yahoo --count 10 2>&1 | tee test-diagnose-yahoo.txt
./capcat fetch xinhua --count 10 2>&1 | tee test-diagnose-xinhua.txt
./capcat fetch test_source --count 10 2>&1 | tee test-diagnose-test_source.txt
```

#### 3. Media Filtering Verification
After each test, verify media filtering works correctly:

```bash
# Count non-image media files (should be 0 without --media flag)
find "../News/news_*" -name "*.pdf" -o -name "*.mp4" -o -name "*.mp3" | wc -l

# Count image files (should be > 0)
find "../News/news_*" -name "*.jpg" -o -name "*.png" | wc -l
```

#### 4. Test-Diagnose File Creation

**MANDATORY**: Create standardized diagnosis file for each source:

```markdown
# test-diagnose-[SOURCE_NAME].md

**Date**: YYYY-MM-DD HH:MM
**Test Type**: SOURCE_TEST
**Command**: ./capcat fetch [source] --count 10
**Status**: [SUCCESS/FAILURE/PARTIAL/ERROR]

## Results Summary
- **Items Requested**: 10
- **Items Successfully Processed**: X/10
- **Success Rate**: X%
- **Media Files Downloaded**: X images
- **Non-Image Media Files**: 0 (should be 0 unless --media used)

## Core Functionality Verification
- +/- Primary function works without errors
- +/- Media filtering works correctly
- +/- Output format/structure is correct
- +/- Error handling works properly
- +/- Performance is acceptable

## Errors Encountered
[List any errors: import issues, network failures, logic errors, etc.]

## Output Structure/Results
```
[Directory structure and file contents]
```

## Recommendations
[Specific fixes needed: import statements, logic changes, performance improvements]

## Priority Level
[HIGH/MEDIUM/LOW] - Based on impact on core functionality
```

### Comprehensive Source Testing Script

```python
#!/usr/bin/env python3
"""
Comprehensive source testing script.
Tests all 20 sources with performance monitoring.
"""

import time
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from core.source_system.source_registry import get_source_registry
from core.source_system.performance_monitor import get_performance_monitor

class SourceTester:
    def __init__(self):
        self.registry = get_source_registry()
        self.monitor = get_performance_monitor()
        self.results = {}

    def test_source(self, source_name: str, count: int = 10) -> dict:
        """Test a single source."""
        print(f"Testing {source_name}...")
        start_time = time.time()

        try:
            # Test source creation
            source = self.registry.get_source(source_name)
            creation_success = True
        except Exception as e:
            return {
                'source_name': source_name,
                'creation_success': False,
                'creation_error': str(e),
                'articles_discovered': 0,
                'processing_time': 0
            }

        try:
            # Test article discovery
            articles = source.get_articles(count)
            articles_discovered = len(articles)
            discovery_success = articles_discovered > 0
        except Exception as e:
            return {
                'source_name': source_name,
                'creation_success': True,
                'discovery_success': False,
                'discovery_error': str(e),
                'articles_discovered': 0,
                'processing_time': time.time() - start_time
            }

        processing_time = time.time() - start_time

        return {
            'source_name': source_name,
            'creation_success': creation_success,
            'discovery_success': discovery_success,
            'articles_discovered': articles_discovered,
            'processing_time': processing_time,
            'avg_time_per_article': processing_time / max(articles_discovered, 1)
        }

    def test_all_sources(self, count: int = 10) -> dict:
        """Test all available sources."""
        sources = self.registry.get_available_sources()
        print(f"Testing {len(sources)} sources...")

        # Parallel testing
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.test_source, source, count): source
                for source in sources
            }

            for future in futures:
                source_name = futures[future]
                try:
                    result = future.result()
                    self.results[source_name] = result
                except Exception as e:
                    self.results[source_name] = {
                        'source_name': source_name,
                        'creation_success': False,
                        'error': str(e),
                        'processing_time': 0
                    }

        return self.results

    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        total_sources = len(self.results)
        successful_creation = sum(1 for r in self.results.values() if r.get('creation_success', False))
        successful_discovery = sum(1 for r in self.results.values() if r.get('discovery_success', False))

        report = f"""# Comprehensive Source Test Report

**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Sources Tested**: {total_sources}
**Creation Success Rate**: {successful_creation}/{total_sources} ({successful_creation/total_sources*100:.1f}%)
**Discovery Success Rate**: {successful_discovery}/{total_sources} ({successful_discovery/total_sources*100:.1f}%)

## Individual Source Results

"""

        for source_name, result in sorted(self.results.items()):
            status = "SUCCESS" if result.get('discovery_success', False) else "FAILED"
            articles = result.get('articles_discovered', 0)
            time_taken = result.get('processing_time', 0)

            report += f"### {source_name}\n"
            report += f"- **Status**: {status}\n"
            report += f"- **Articles Discovered**: {articles}\n"
            report += f"- **Processing Time**: {time_taken:.2f}s\n"

            if 'error' in result or 'creation_error' in result or 'discovery_error' in result:
                error = result.get('error') or result.get('creation_error') or result.get('discovery_error')
                report += f"- **Error**: {error}\n"

            report += "\n"

        # Performance summary
        avg_time = sum(r.get('processing_time', 0) for r in self.results.values()) / total_sources
        total_articles = sum(r.get('articles_discovered', 0) for r in self.results.values())

        report += f"""## Performance Summary

- **Average Processing Time**: {avg_time:.2f}s per source
- **Total Articles Discovered**: {total_articles}
- **Overall Success Rate**: {successful_discovery/total_sources*100:.1f}%

## Recommendations

"""

        # Add recommendations based on results
        failed_sources = [name for name, result in self.results.items()
                         if not result.get('discovery_success', False)]

        if failed_sources:
            report += f"**Failed Sources**: {', '.join(failed_sources)}\n"
            report += "- Review configuration and network connectivity\n"
            report += "- Check for anti-bot protection\n"
            report += "- Validate CSS selectors\n\n"

        slow_sources = [name for name, result in self.results.items()
                       if result.get('processing_time', 0) > 10]

        if slow_sources:
            report += f"**Slow Sources**: {', '.join(slow_sources)}\n"
            report += "- Consider optimization\n"
            report += "- Review timeout settings\n"

        return report

if __name__ == "__main__":
    tester = SourceTester()
    results = tester.test_all_sources(count=10)

    report = tester.generate_report()

    # Save report
    with open('comprehensive_test_report.md', 'w') as f:
        f.write(report)

    print("Test completed. Report saved to comprehensive_test_report.md")
    print(f"Success rate: {sum(1 for r in results.values() if r.get('discovery_success', False))}/{len(results)}")
```

## Component Testing

### Registry Testing
```python
# test_registry.py
import unittest
from core.source_system.source_registry import SourceRegistry, get_source_registry

class TestSourceRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = SourceRegistry()

    def test_source_discovery(self):
        """Test source discovery functionality."""
        sources = self.registry.discover_sources()
        self.assertGreater(len(sources), 0)
        self.assertIn('hn', sources)
        self.assertIn('bbc', sources)

    def test_source_creation(self):
        """Test source instance creation."""
        source = self.registry.get_source('hn')
        self.assertIsNotNone(source)
        self.assertEqual(source.config.name, 'hn')

    def test_validation(self):
        """Test source validation."""
        errors = self.registry.validate_all_sources()
        # Should be minimal errors in production system
        error_count = sum(len(errs) for errs in errors.values())
        self.assertLessEqual(error_count, 5)  # Allow some minor issues

if __name__ == '__main__':
    unittest.main()
```

### Performance Monitor Testing
```python
# test_performance_monitor.py
import unittest
import time
from core.source_system.performance_monitor import PerformanceMonitor

class TestPerformanceMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = PerformanceMonitor()

    def test_metrics_recording(self):
        """Test metrics recording."""
        self.monitor.record_request('test_source', True, 1.5)
        self.monitor.record_request('test_source', False, 2.0)

        metrics = self.monitor.get_source_metrics('test_source')
        self.assertEqual(metrics.total_requests, 2)
        self.assertEqual(metrics.successful_requests, 1)
        self.assertEqual(metrics.success_rate, 50.0)

    def test_performance_report(self):
        """Test report generation."""
        self.monitor.record_request('test', True, 1.0)
        report = self.monitor.generate_performance_report()
        self.assertIn('test', report)
        self.assertIn('100.0%', report)

if __name__ == '__main__':
    unittest.main()
```

## Integration Testing

### End-to-End Workflow Test
```python
# test_e2e_workflow.py
import unittest
import tempfile
import shutil
from pathlib import Path
from core.source_system.source_registry import get_source_registry

class TestE2EWorkflow(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.registry = get_source_registry()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_article_fetch_workflow(self):
        """Test complete article fetching workflow."""
        # Get source
        source = self.registry.get_source('hn')

        # Fetch articles
        articles = source.get_articles(count=3)
        self.assertGreater(len(articles), 0)

        # Fetch content for first article
        if articles:
            content = source.get_article_content(articles[0]['url'])
            self.assertIsNotNone(content)

    def test_config_driven_vs_custom(self):
        """Test both source types work."""
        # Config-driven source
        config_source = self.registry.get_source('iq')
        config_articles = config_source.get_articles(count=3)

        # Custom source
        custom_source = self.registry.get_source('hn')
        custom_articles = custom_source.get_articles(count=3)

        self.assertGreater(len(config_articles), 0)
        self.assertGreater(len(custom_articles), 0)

if __name__ == '__main__':
    unittest.main()
```

## Performance Testing

### Performance Benchmarking Script
```python
# benchmark_performance.py
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from core.source_system.source_registry import get_source_registry

class PerformanceBenchmark:
    def __init__(self):
        self.registry = get_source_registry()

    def benchmark_source(self, source_name: str, iterations: int = 5) -> dict:
        """Benchmark a single source."""
        times = []
        article_counts = []

        for _ in range(iterations):
            start_time = time.time()

            source = self.registry.get_source(source_name)
            articles = source.get_articles(count=10)

            duration = time.time() - start_time
            times.append(duration)
            article_counts.append(len(articles))

        return {
            'source_name': source_name,
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'avg_articles': statistics.mean(article_counts),
            'consistency': statistics.stdev(article_counts) if len(article_counts) > 1 else 0
        }

    def benchmark_all_sources(self, iterations: int = 3) -> dict:
        """Benchmark all sources."""
        sources = self.registry.get_available_sources()[:5]  # Test subset for speed
        results = {}

        for source in sources:
            try:
                results[source] = self.benchmark_source(source, iterations)
            except Exception as e:
                results[source] = {'error': str(e)}

        return results

    def generate_performance_report(self, results: dict) -> str:
        """Generate performance report."""
        report = "# Performance Benchmark Report\n\n"

        successful_results = {k: v for k, v in results.items() if 'error' not in v}

        if successful_results:
            avg_times = [r['avg_time'] for r in successful_results.values()]
            overall_avg = statistics.mean(avg_times)

            report += f"**Overall Average Time**: {overall_avg:.2f}s\n"
            report += f"**Sources Tested**: {len(successful_results)}\n\n"

            report += "## Individual Source Performance\n\n"

            for source, data in sorted(successful_results.items(), key=lambda x: x[1]['avg_time']):
                report += f"### {source}\n"
                report += f"- Average Time: {data['avg_time']:.2f}s\n"
                report += f"- Range: {data['min_time']:.2f}s - {data['max_time']:.2f}s\n"
                report += f"- Articles Found: {data['avg_articles']:.1f} avg\n"
                report += f"- Consistency: {data['std_dev']:.2f}s std dev\n\n"

        # Failed sources
        failed_sources = {k: v for k, v in results.items() if 'error' in v}
        if failed_sources:
            report += "## Failed Sources\n\n"
            for source, data in failed_sources.items():
                report += f"- **{source}**: {data['error']}\n"

        return report

if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    results = benchmark.benchmark_all_sources(iterations=3)

    report = benchmark.generate_performance_report(results)

    with open('performance_benchmark.md', 'w') as f:
        f.write(report)

    print("Performance benchmark completed. Report saved to performance_benchmark.md")
```

## Success Criteria

### Source Testing Success Criteria
- Command executes without import/syntax errors
- Successfully processes at least 80% of requested articles
- Media filtering works correctly (only images without --media flag)
- Proper directory structure created
- Articles saved in readable Markdown format

### Component Testing Success Criteria
- Component initializes without errors
- Core functionality works as designed
- Error handling works properly
- Performance meets acceptable standards
- Integration with other components works

### Performance Testing Success Criteria
- Average response time < 6 seconds per source
- Success rate > 85% across all sources
- Memory usage remains stable during batch operations
- No memory leaks during extended operation

## Debugging and Troubleshooting

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues and Solutions

#### Import Errors
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify virtual environment
which python
pip list | grep -E "(requests|beautifulsoup4|yaml)"
```

#### Network Issues
```python
# Test network connectivity
import requests
response = requests.get('https://httpbin.org/get', timeout=5)
print(f"Status: {response.status_code}")
```

#### Source Discovery Issues
```python
# Debug source discovery
from core.source_system.source_registry import SourceRegistry
registry = SourceRegistry()
registry.logger.setLevel(logging.DEBUG)
sources = registry.discover_sources()
```

### Test Data Validation
```python
# Validate test output structure
import os
from pathlib import Path

def validate_test_output(base_path="../News"):
    """Validate test output structure."""
    news_dirs = list(Path(base_path).glob("news_*"))

    if not news_dirs:
        print("No news directories found")
        return False

    latest_dir = max(news_dirs, key=os.path.getctime)
    print(f"Found news directory: {latest_dir}")

    source_dirs = list(latest_dir.glob("*_*"))
    print(f"Source directories: {len(source_dirs)}")

    for source_dir in source_dirs:
        article_dirs = list(source_dir.glob("*_*"))
        print(f"  - {source_dir.name}: {len(article_dirs)} articles")

        if article_dirs:
            sample_article = article_dirs[0]
            article_md = sample_article / "article.md"
            if article_md.exists():
                print(f"    {sample_article.name}/article.md exists")
            else:
                print(f"    {sample_article.name}/article.md missing")

if __name__ == "__main__":
    validate_test_output()
```

---

*This testing guide ensures comprehensive validation of all Capcat components with systematic procedures and clear success criteria.*