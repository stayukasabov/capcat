# Source Development Guide

Complete guide for developing new sources in the Capcat hybrid architecture. Choose between config-driven (simple) or custom implementation (complex) based on your requirements.

## Decision Matrix: Config-Driven vs Custom

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Factor</th>
      <th>Config-Driven</th>
      <th>Custom Implementation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>**Development Time**</td>
      <td>15-30 minutes</td>
      <td>2-4 hours</td>
    </tr>
    <tr>
      <td>**Coding Required**</td>
      <td>None (YAML only)</td>
      <td>Python development</td>
    </tr>
    <tr>
      <td>**Flexibility**</td>
      <td>Limited to standard patterns</td>
      <td>Full control</td>
    </tr>
    <tr>
      <td>**Best For**</td>
      <td>Standard news sites</td>
      <td>Complex sites, APIs, comments</td>
    </tr>
    <tr>
      <td>**Maintenance**</td>
      <td>Configuration updates</td>
      <td>Code changes</td>
    </tr>
    <tr>
      <td>**Examples**</td>
      <td>InfoQ, Euronews, Straits Times</td>
      <td>Hacker News, BBC, TechCrunch</td>
    </tr>
  </tbody>
</table>
</div>

## RSS-First Development Rule

**MANDATORY**: When adding sources, check RSS feeds first and use the links to access content. RSS-based extraction often provides cleaner, more reliable content than HTML scraping, especially for React/SPA websites.

**RSS-First Benefits**:
- Bypasses bot protection and JavaScript rendering issues
- Provides clean, structured content
- Often includes full article text in descriptions
- More reliable than HTML selectors that frequently change

**Implementation**: Configure `rss_config` in source YAML with `use_rss_content: true` to extract content directly from RSS descriptions.

## Config-Driven Sources

**Use When**: Standard news website with straightforward article listing and content structure, or RSS-based content extraction.

### 1. Create Configuration File

```yaml
# sources/active/config_driven/configs/newsource.yaml
display_name: "News Source"
base_url: "https://newsource.com/"
category: "general"  # tech, science, business, general
timeout: 10.0
rate_limit: 1.0

# RSS-based content extraction (preferred method)
rss_config:
  feed_url: "https://newsource.com/feed.xml"
  use_rss_content: true
  content_field: "description"  # Extract content from RSS description field

# Required: Article discovery selectors
article_selectors:
  - ".headline a"
  - ".article-title a"
  - "h2.title a"

# Required: Content extraction selectors
content_selectors:
  - ".article-content"
  - ".post-body"
  - "div.content"

# Optional: Skip patterns (URLs to ignore)
skip_patterns:
  - "/about"
  - "/contact"
  - "/advertising"
  - "?utm_"

# Optional: Comment support
supports_comments: false

# Image processing configuration
image_processing:
  selectors:
    - "img"
    - ".content img"
    - "article img"

  url_patterns:
    - "newsource.com/"
    - "cdn.newsource.com/"
    - "images.newsource.com/"

  # Allow URLs without traditional extensions for modern CDNs
  allow_extensionless: true

  skip_selectors:
    - ".sidebar img"
    - ".navigation img"
    - ".header img"
    - ".avatar img"

  # Advanced filtering: limit number of images
  max_images: 10  # Optional: limit to first N images (after skip_selectors)

  # Advanced filtering: minimum image size in bytes
  min_image_size: 10240  # Optional: 10KB minimum (filters small icons/thumbnails)

# Optional: Additional configuration
custom_config:
  user_agent: "Custom User Agent"
  headers:
    Accept: "text/html,application/xhtml+xml"
```

### 2. Test Configuration
```bash
# Test source discovery
python -c "from core.source_system.source_registry import get_source_registry; print('newsource' in get_source_registry().get_available_sources())"

# Test source functionality
./capcat fetch newsource --count 3
```

### 3. Validation
```bash
# Run validation
python -c "
from core.source_system.source_registry import get_source_registry
registry = get_source_registry()
errors = registry.validate_all_sources(deep_validation=True)
print(f'newsource errors: {errors.get(\"newsource\", [])}')
"
```

## Template System Integration

**Universal HTML Generation**: All sources can leverage the template system for consistent navigation and professional output.

### Adding Template Support to Sources

```yaml
# Add to your source config.yaml (both config-driven and custom)
template:
  variant: "article-with-comments"  # or "article-no-comments"
  navigation:
    back_to_news_url: "../../news.html"
    back_to_news_text: "Back to News"
    has_comments: true              # false for news sources without comments
    comments_url: "comments.html"   # only if has_comments: true
    comments_text: "View Comments"  # only if has_comments: true
```

### Template Variants

- **`article-with-comments`**: For sources like HN, Lobsters, LessWrong with comment systems
- **`article-no-comments`**: For news sources like BBC, CNN, Nature without comments
- **`comments-with-navigation`**: Automatically used for all comments pages

### Benefits

- **Automatic HTML Generation**: Professional navigation without custom HTML code
- **Consistent Experience**: Same navigation patterns across all sources
- **Conditional Comments**: Comments links only shown when comments exist
- **Responsive Design**: Mobile-friendly with dark/light theme support

### Integration

## UTF-8 Encoding Handling

**Native UTF-8 Support**: Capcat uses Python's built-in UTF-8 handling and BeautifulSoup's automatic encoding detection for reliable character processing.

### Encoding Best Practices

- All content is processed using proper UTF-8 encoding
- BeautifulSoup automatically detects and handles various character encodings
- No additional text processing needed - modern websites use proper UTF-8
- Special characters (é, ñ, ö, etc.) are preserved correctly

## Custom Sources

**Use When**: Complex scraping logic, API integration, comment systems, or anti-bot protection handling required.

### 1. Create Source Structure
```bash
mkdir -p sources/active/custom/newsource
touch sources/active/custom/newsource/source.py
touch sources/active/custom/newsource/config.yaml
```

### 2. Basic Configuration
```yaml
# sources/active/custom/newsource/config.yaml
display_name: "News Source"
base_url: "https://newsource.com/"
category: "general"
timeout: 10.0
rate_limit: 1.0
supports_comments: true  # If implementing comment system
```

### 3. Source Implementation
```python
# sources/active/custom/newsource/source.py
from typing import List, Dict, Optional
from core.source_system.base_source import BaseSource, SourceConfig
from core.logging_config import get_logger

class NewsSourceSource(BaseSource):
    """Custom implementation for News Source."""

    def __init__(self, config: SourceConfig, session=None):
        super().__init__(config, session)
        self.logger = get_logger(__name__)

    def get_articles(self, count: int = 30) -> List[Dict]:
        """
        Get articles from the source.

        Args:
            count: Number of articles to fetch

        Returns:
            List of article dictionaries with keys: title, url, summary
        """
        try:
            self.logger.info(f"Fetching {count} articles from {self.config.display_name}")

            # Step 1: Get main page
            response = self.session.get(
                self.config.base_url,
                timeout=self.config.timeout,
                headers=self._get_headers()
            )
            response.raise_for_status()

            # Step 2: Parse articles
            soup = self._get_soup(response.text)
            articles = []

            # Custom parsing logic
            for article_elem in soup.select('.article-item'):
                title_elem = article_elem.select_one('.title a')
                summary_elem = article_elem.select_one('.summary')

                if title_elem and title_elem.get('href'):
                    article = {
                        'title': title_elem.get_text(strip=True),
                        'url': self._resolve_url(title_elem['href']),
                        'summary': summary_elem.get_text(strip=True) if summary_elem else ''
                    }
                    articles.append(article)

                    if len(articles) >= count:
                        break

            self.logger.info(f"Successfully fetched {len(articles)} articles")
            return articles

        except Exception as e:
            self.logger.error(f"Error fetching articles: {e}")
            return []

    def get_article_content(self, url: str) -> Optional[str]:
        """
        Get full content for a specific article.

        Args:
            url: Article URL

        Returns:
            Article content as HTML string
        """
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()

            soup = self._get_soup(response.text)

            # Try multiple content selectors
            for selector in ['.article-content', '.post-body', 'div.content']:
                content_elem = soup.select_one(selector)
                if content_elem:
                    return str(content_elem)

            self.logger.warning(f"No content found for {url}")
            return None

        except Exception as e:
            self.logger.error(f"Error fetching content for {url}: {e}")
            return None

    def get_comments(self, url: str) -> List[Dict]:
        """
        Get comments for an article (if supported).

        Args:
            url: Article URL

        Returns:
            List of comment dictionaries
        """
        if not self.config.supports_comments:
            return []

        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()

            soup = self._get_soup(response.text)
            comments = []

            # Custom comment parsing logic
            for comment_elem in soup.select('.comment'):
                author_elem = comment_elem.select_one('.author')
                text_elem = comment_elem.select_one('.comment-text')

                if author_elem and text_elem:
                    comment = {
                        'author': author_elem.get_text(strip=True),
                        'text': text_elem.get_text(strip=True),
                        'timestamp': self._extract_timestamp(comment_elem)
                    }
                    comments.append(comment)

            return comments

        except Exception as e:
            self.logger.error(f"Error fetching comments for {url}: {e}")
            return []

    def validate_config(self) -> List[str]:
        """Validate source-specific configuration."""
        errors = []

        # Add custom validation logic
        if not self.config.base_url.startswith('https://'):
            errors.append("base_url must use HTTPS")

        return errors

    def _get_headers(self) -> Dict[str, str]:
        """Get custom headers for requests."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Capcat/2.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        # Add custom headers from config
        custom_headers = self.config.custom_config.get('headers', {})
        headers.update(custom_headers)

        return headers

    def _extract_timestamp(self, element) -> Optional[str]:
        """Extract timestamp from comment element."""
        # Custom timestamp extraction logic
        time_elem = element.select_one('.timestamp, .date, time')
        if time_elem:
            return time_elem.get('datetime') or time_elem.get_text(strip=True)
        return None
```

### 4. Advanced Custom Features

#### API Integration Example
```python
def get_articles(self, count: int = 30) -> List[Dict]:
    """API-based article fetching."""
    api_url = f"{self.config.base_url}/api/articles"

    response = self.session.get(
        api_url,
        params={'limit': count, 'format': 'json'},
        headers=self._get_api_headers()
    )

    data = response.json()
    return [
        {
            'title': item['title'],
            'url': item['permalink'],
            'summary': item.get('excerpt', '')
        }
        for item in data.get('articles', [])
    ]

def _get_api_headers(self) -> Dict[str, str]:
    """API-specific headers."""
    return {
        'Accept': 'application/json',
        'User-Agent': 'Capcat/2.0 API Client'
    }
```

#### Anti-Bot Protection Handling
```python
def _handle_anti_bot_protection(self, response):
    """Handle CloudFlare or similar protection."""
    if 'cloudflare' in response.text.lower():
        self.logger.warning("CloudFlare protection detected")
        # Implement CloudFlare bypass logic
        # Or use alternative endpoints

    return response
```

#### Dynamic Content Loading
```python
def _wait_for_dynamic_content(self, soup):
    """Handle JavaScript-loaded content."""
    # Check for loading indicators
    if soup.select('.loading, .spinner'):
        time.sleep(2)  # Wait for content to load
        # Re-fetch or use selenium for complex cases
```

## Testing Your Source

### 1. Basic Functionality Test
```python
# test_newsource.py
import unittest
from core.source_system.source_registry import get_source_registry

class TestNewsSource(unittest.TestCase):
    def setUp(self):
        self.registry = get_source_registry()
        self.source = self.registry.get_source('newsource')

    def test_get_articles(self):
        articles = self.source.get_articles(count=5)
        self.assertGreater(len(articles), 0)
        self.assertIn('title', articles[0])
        self.assertIn('url', articles[0])

    def test_get_content(self):
        articles = self.source.get_articles(count=1)
        if articles:
            content = self.source.get_article_content(articles[0]['url'])
            self.assertIsNotNone(content)

if __name__ == '__main__':
    unittest.main()
```

### 2. Integration Test
```bash
# Test with actual command
./capcat fetch newsource --count 3

# Verify output structure
ls "../News/news_$(date +%d-%m-%Y)/NewsSource_$(date +%d-%m-%Y)/"
```

### 3. Performance Test
```python
import time
from core.source_system.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
start_time = time.time()

source = registry.get_source('newsource')
articles = source.get_articles(count=10)

duration = time.time() - start_time
print(f"Fetched {len(articles)} articles in {duration:.2f} seconds")
```

## Best Practices

### Code Quality
- **Follow PEP 8**: Use flake8 for linting
- **Type Hints**: Include type annotations
- **Documentation**: Google-style docstrings
- **Error Handling**: Comprehensive exception management
- **Logging**: Use structured logging

### Performance
- **Reuse Sessions**: Use provided session instance
- **Rate Limiting**: Respect site rate limits
- **Caching**: Cache expensive operations
- **Timeouts**: Always set request timeouts

### Security
- **User Agents**: Use realistic user agent strings
- **Headers**: Include standard browser headers
- **Respect robots.txt**: Check site crawling policies
- **Rate Limiting**: Avoid overwhelming servers

### Maintainability
- **Configuration**: Use config for all site-specific values
- **Selectors**: Make CSS selectors configurable
- **Validation**: Implement thorough config validation
- **Testing**: Create comprehensive test suites

## Debugging

### Enable Debug Logging
```python
import logging
logging.getLogger('core.source_system').setLevel(logging.DEBUG)
```

### Test Selectors
```python
from bs4 import BeautifulSoup
import requests

# Test selectors manually
response = requests.get('https://newsource.com/')
soup = BeautifulSoup(response.text, 'html.parser')

# Test article selectors
articles = soup.select('.headline a')
print(f"Found {len(articles)} articles")

# Test content selectors
for selector in ['.article-content', '.post-body']:
    elements = soup.select(selector)
    print(f"Selector '{selector}': {len(elements)} elements")
```

### Performance Debugging
```python
import time
from core.source_system.performance_monitor import get_performance_monitor

monitor = get_performance_monitor()

# Check source metrics
metrics = monitor.get_source_metrics('newsource')
print(f"Success rate: {metrics.success_rate:.1f}%")
print(f"Avg response time: {metrics.avg_response_time:.2f}s")
```

## Checklist

### Config-Driven Source Checklist
- [ ] YAML configuration created
- [ ] Article selectors defined and tested
- [ ] Content selectors defined and tested
- [ ] Skip patterns configured (if needed)
- [ ] Source discoverable by registry
- [ ] Basic fetch test successful
- [ ] Validation passes

### Custom Source Checklist
- [ ] Source directory structure created
- [ ] BaseSource subclass implemented
- [ ] get_articles() method implemented
- [ ] get_article_content() method implemented
- [ ] get_comments() method implemented (if applicable)
- [ ] validate_config() method implemented
- [ ] Error handling comprehensive
- [ ] Logging implemented
- [ ] Unit tests created
- [ ] Integration test successful
- [ ] Performance acceptable

---

*Following this guide ensures your source integrates seamlessly with the Capcat hybrid architecture while maintaining high quality and performance standards.*