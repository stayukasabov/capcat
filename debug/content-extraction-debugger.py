#!/usr/bin/env python3
"""
Content Extraction Debugging Tool for Capcat
Helps diagnose why articles return empty markdown or fail to fetch.
"""

import requests
import json
import sys
import re
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import yaml

class ContentExtractionDebugger:
    def __init__(self, capcat_root="/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat-copy/Application"):
        self.capcat_root = Path(capcat_root)
        self.session = requests.Session()
        self.setup_session()

    def setup_session(self):
        """Setup session with realistic headers."""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def debug_url(self, url):
        """Debug content extraction for a specific URL."""
        print(f"\n🔍 Debugging: {url}")
        print("=" * 80)

        # Step 1: Basic connectivity
        self.test_connectivity(url)

        # Step 2: Find source configuration
        source_config = self.find_source_config(url)
        if source_config:
            print(f"📁 Found source config: {source_config}")
        else:
            print("❌ No source config found - URL might not be configured")
            return

        # Step 3: Fetch raw HTML
        html_content = self.fetch_raw_html(url)
        if not html_content:
            return

        # Step 4: Analyze HTML structure
        self.analyze_html_structure(html_content, url)

        # Step 5: Test extraction patterns
        self.test_extraction_patterns(html_content, source_config, url)

        # Step 6: Anti-bot detection check
        self.check_anti_bot_protection(html_content, url)

    def test_connectivity(self, url):
        """Test basic connectivity to the URL."""
        print("🌐 Testing connectivity...")

        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Final URL: {response.url}")

            # Check important headers
            headers_to_check = ['content-type', 'server', 'cf-ray', 'cloudflare', 'x-robots-tag']
            for header in headers_to_check:
                if header in response.headers:
                    print(f"🏷️  {header}: {response.headers[header]}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Connectivity failed: {e}")
            return False

        return True

    def find_source_config(self, url):
        """Find the source configuration for this URL."""
        domain = urlparse(url).netloc.replace('www.', '')

        # Search in config directories
        config_paths = [
            self.capcat_root / "Config" / "sources" / "active" / "config_driven" / "configs",
            self.capcat_root / "Config" / "sources" / "active" / "custom",
            self.capcat_root / "capcat" / "sources" / "builtin",
        ]

        for config_path in config_paths:
            if not config_path.exists():
                continue

            # Look for YAML files
            for yaml_file in config_path.glob("**/*.yaml"):
                try:
                    with open(yaml_file, 'r') as f:
                        config = yaml.safe_load(f)

                    if isinstance(config, dict) and 'base_url' in config:
                        config_domain = urlparse(config['base_url']).netloc.replace('www.', '')
                        if config_domain == domain:
                            return yaml_file

                except Exception:
                    continue

        return None

    def fetch_raw_html(self, url):
        """Fetch raw HTML content."""
        print("📡 Fetching HTML...")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            content_length = len(response.content)
            print(f"✅ Fetched {content_length:,} bytes")
            print(f"🎭 Content-Type: {response.headers.get('content-type', 'unknown')}")

            # Save raw HTML for inspection
            debug_file = Path("debug_html.html")
            with open(debug_file, 'wb') as f:
                f.write(response.content)
            print(f"💾 Saved raw HTML to: {debug_file.absolute()}")

            return response.text

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch HTML: {e}")
            return None

    def analyze_html_structure(self, html_content, url):
        """Analyze HTML structure for common content patterns."""
        print("🔬 Analyzing HTML structure...")

        soup = BeautifulSoup(html_content, 'html.parser')

        # Check for common article containers
        article_selectors = [
            'article',
            '[role="main"]',
            '.article',
            '.post',
            '.content',
            '.entry-content',
            '.post-content',
            '.article-content',
            'main'
        ]

        print("📋 Potential article containers:")
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    text_length = len(elem.get_text(strip=True))
                    print(f"  ✅ {selector} ({i+1}): {text_length} chars")

        # Check for title
        title_selectors = ['h1', 'title', '.title', '.headline', '.post-title']
        print("\n📰 Potential titles:")
        for selector in title_selectors:
            elements = soup.select(selector)
            if elements:
                title_text = elements[0].get_text(strip=True)[:100]
                print(f"  ✅ {selector}: {title_text}...")

        # Check page length and content density
        total_text = soup.get_text(strip=True)
        print(f"\n📏 Total text length: {len(total_text):,} chars")

        # Look for pagination or lazy loading indicators
        pagination_indicators = [
            'data-lazy', 'loading="lazy"', 'nextpage', 'pagination',
            'load-more', 'infinite-scroll'
        ]

        for indicator in pagination_indicators:
            if indicator in html_content.lower():
                print(f"⚠️  Found pagination/lazy loading: {indicator}")

    def test_extraction_patterns(self, html_content, config_file, url):
        """Test extraction patterns from source config."""
        print("🎯 Testing extraction patterns...")

        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return

        soup = BeautifulSoup(html_content, 'html.parser')

        # Test article selectors
        if 'article_selectors' in config:
            selectors = config['article_selectors']

            print("🎯 Testing article selectors:")
            if 'content' in selectors:
                content_selector = selectors['content']
                content_elements = soup.select(content_selector)
                if content_elements:
                    content_text = content_elements[0].get_text(strip=True)
                    print(f"  ✅ content: Found {len(content_text)} chars")
                else:
                    print(f"  ❌ content: No elements found for '{content_selector}'")

            if 'title' in selectors:
                title_selector = selectors['title']
                title_elements = soup.select(title_selector)
                if title_elements:
                    title_text = title_elements[0].get_text(strip=True)
                    print(f"  ✅ title: '{title_text[:50]}...'")
                else:
                    print(f"  ❌ title: No elements found for '{title_selector}'")

    def check_anti_bot_protection(self, html_content, url):
        """Check for anti-bot protection indicators."""
        print("🛡️  Checking for anti-bot protection...")

        bot_indicators = [
            ('Cloudflare', ['checking your browser', 'cloudflare', 'cf-ray']),
            ('Incapsula', ['incapsula', '_incap_ses']),
            ('reCAPTCHA', ['recaptcha', 'g-recaptcha']),
            ('hCaptcha', ['hcaptcha', 'h-captcha']),
            ('Access Denied', ['access denied', 'forbidden', '403 forbidden']),
            ('Rate Limited', ['rate limit', 'too many requests', '429']),
            ('Bot Detection', ['bot detected', 'automated traffic', 'suspicious activity'])
        ]

        content_lower = html_content.lower()

        for protection_type, indicators in bot_indicators:
            for indicator in indicators:
                if indicator in content_lower:
                    print(f"  ⚠️  {protection_type}: Found '{indicator}'")
                    break

        # Check for JavaScript challenges
        if 'challenge-form' in content_lower or 'jschl_vc' in content_lower:
            print("  ⚠️  JavaScript Challenge: Cloudflare challenge detected")

        # Check for extremely short content (sign of blocking)
        if len(html_content.strip()) < 1000:
            print(f"  ⚠️  Suspiciously short content: {len(html_content)} chars")

def main():
    if len(sys.argv) < 2:
        print("Usage: python content-extraction-debugger.py <URL>")
        sys.exit(1)

    debugger = ContentExtractionDebugger()

    urls = [
        "https://percepta.ai/blog/constructing-llm-computer",
        "https://www.forbes.com/sites/joetoscano1/2026/03/06/google-just-patented-the-end-of-your-website/",
        "https://ahwoo.com/news/4807024/kitten-space-agency/planetary-rings"
    ]

    for url in urls:
        debugger.debug_url(url)
        print()

if __name__ == "__main__":
    main()