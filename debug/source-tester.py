#!/usr/bin/env python3
"""
Source Configuration Tester
Tests Capcat source configurations and suggests fixes.
"""

import sys
import json
import yaml
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class SourceTester:
    def __init__(self, capcat_root="/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat-copy/Application"):
        self.capcat_root = Path(capcat_root)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def test_source(self, source_id):
        """Test a specific source configuration."""
        print(f"🧪 Testing source: {source_id}")
        print("=" * 60)

        # Find config file
        config_file = self.find_source_config(source_id)
        if not config_file:
            print(f"❌ Config file not found for source: {source_id}")
            return

        print(f"📁 Config: {config_file}")

        # Load config
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return

        # Test RSS discovery
        self.test_rss_discovery(config)

        # Test article extraction
        self.test_article_extraction(config)

    def find_source_config(self, source_id):
        """Find config file for a source."""
        search_paths = [
            self.capcat_root / "Config" / "sources" / "active" / "config_driven" / "configs" / f"{source_id}.yaml",
            self.capcat_root / "Config" / "sources" / "active" / "custom" / source_id / "config.yaml",
            self.capcat_root / "capcat" / "sources" / "builtin" / f"{source_id}.yaml"
        ]

        for path in search_paths:
            if path.exists():
                return path
        return None

    def test_rss_discovery(self, config):
        """Test RSS feed discovery."""
        print("\n📡 Testing RSS Discovery...")

        discovery = config.get('discovery', {})
        if discovery.get('method') != 'rss':
            print("⚠️  Not an RSS source")
            return

        rss_urls = discovery.get('rss_urls', {})
        primary_url = rss_urls.get('primary')

        if not primary_url:
            print("❌ No primary RSS URL configured")
            return

        print(f"🔗 Testing: {primary_url}")

        try:
            response = self.session.get(primary_url, timeout=10)
            response.raise_for_status()

            print(f"✅ RSS accessible: {response.status_code}")
            print(f"📏 Content length: {len(response.content):,} bytes")

            # Parse RSS to find recent articles
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')[:5]  # Get first 5 items

            if items:
                print(f"📰 Found {len(items)} recent articles:")
                for i, item in enumerate(items, 1):
                    title = item.title.text if item.title else "No title"
                    link = item.link.text if item.link else "No link"
                    print(f"  {i}. {title[:60]}...")
                    print(f"     {link}")

                return items[0].link.text if items[0].link else None
            else:
                print("❌ No articles found in RSS")

        except requests.RequestException as e:
            print(f"❌ RSS fetch failed: {e}")
        except Exception as e:
            print(f"❌ RSS parse failed: {e}")

        return None

    def test_article_extraction(self, config):
        """Test article extraction on a sample article."""
        print("\n🎯 Testing Article Extraction...")

        # Get sample URL from RSS or use base_url
        sample_url = self.get_sample_article_url(config)
        if not sample_url:
            print("❌ No sample URL available")
            return

        print(f"🔗 Testing article: {sample_url}")

        try:
            response = self.session.get(sample_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Test selectors
            selectors = config.get('article_selectors', {})

            # Test title selector
            title_selector = selectors.get('title')
            if title_selector:
                title_elem = soup.select_one(title_selector)
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    print(f"✅ Title: {title_text[:80]}...")
                else:
                    print(f"❌ Title selector failed: {title_selector}")
                    self.suggest_title_selectors(soup)

            # Test content selector
            content_selector = selectors.get('content')
            if content_selector:
                content_elem = soup.select_one(content_selector)
                if content_elem:
                    content_text = content_elem.get_text(strip=True)
                    word_count = len(content_text.split())
                    print(f"✅ Content: {word_count} words, {len(content_text)} chars")
                    if word_count < 50:
                        print("⚠️  Content seems short")
                else:
                    print(f"❌ Content selector failed: {content_selector}")
                    self.suggest_content_selectors(soup)

            # Test date selector if present
            date_selector = selectors.get('date')
            if date_selector:
                date_elem = soup.select_one(date_selector)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    print(f"✅ Date: {date_text}")
                else:
                    print(f"❌ Date selector failed: {date_selector}")

        except Exception as e:
            print(f"❌ Article extraction test failed: {e}")

    def get_sample_article_url(self, config):
        """Get a sample article URL for testing."""
        # Try to get from RSS first
        discovery = config.get('discovery', {})
        if discovery.get('method') == 'rss':
            rss_urls = discovery.get('rss_urls', {})
            primary_url = rss_urls.get('primary')

            if primary_url:
                try:
                    response = self.session.get(primary_url, timeout=10)
                    soup = BeautifulSoup(response.content, 'xml')
                    first_item = soup.find('item')
                    if first_item and first_item.link:
                        return first_item.link.text
                except:
                    pass

        # Fallback: construct sample URL from base_url
        base_url = config.get('base_url')
        if base_url:
            # This is a guess - in practice, you'd need manual sample URLs
            return base_url

        return None

    def suggest_title_selectors(self, soup):
        """Suggest alternative title selectors."""
        print("💡 Suggested title selectors:")

        title_candidates = [
            ('h1', soup.find('h1')),
            ('title', soup.find('title')),
            ('.title', soup.select_one('.title')),
            ('.headline', soup.select_one('.headline')),
            ('.post-title', soup.select_one('.post-title')),
            ('[class*="title"]', soup.select_one('[class*="title"]')),
        ]

        for selector, elem in title_candidates:
            if elem:
                text = elem.get_text(strip=True)[:60]
                print(f"  {selector}: {text}...")

    def suggest_content_selectors(self, soup):
        """Suggest alternative content selectors."""
        print("💡 Suggested content selectors:")

        content_candidates = [
            ('article', soup.find('article')),
            ('.content', soup.select_one('.content')),
            ('.post-content', soup.select_one('.post-content')),
            ('.entry-content', soup.select_one('.entry-content')),
            ('.article-content', soup.select_one('.article-content')),
            ('main', soup.find('main')),
            ('[role="main"]', soup.select_one('[role="main"]')),
        ]

        for selector, elem in content_candidates:
            if elem:
                text_length = len(elem.get_text(strip=True))
                word_count = len(elem.get_text(strip=True).split())
                print(f"  {selector}: {word_count} words, {text_length} chars")

    def test_all_sources(self):
        """Test all configured sources."""
        print("🧪 Testing all sources...")

        # Find all config files
        config_dirs = [
            self.capcat_root / "Config" / "sources" / "active" / "config_driven" / "configs",
            self.capcat_root / "capcat" / "sources" / "builtin"
        ]

        sources = []
        for config_dir in config_dirs:
            if config_dir.exists():
                for config_file in config_dir.glob("*.yaml"):
                    source_id = config_file.stem
                    sources.append(source_id)

        print(f"Found {len(sources)} sources to test")

        results = {}
        for source_id in sources:
            try:
                print(f"\n{'='*20} {source_id} {'='*20}")
                self.test_source(source_id)
                results[source_id] = "✅ PASS"
            except Exception as e:
                print(f"❌ Failed: {e}")
                results[source_id] = f"❌ FAIL: {e}"

        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        for source_id, result in results.items():
            print(f"{source_id:20} {result}")

def main():
    tester = SourceTester()

    if len(sys.argv) > 1:
        source_id = sys.argv[1]
        tester.test_source(source_id)
    else:
        # Test problematic sources from the warnings
        problematic_domains = [
            "percepta.ai",
            "ahwoo.com",
            "forbes.com"
        ]

        print("Testing problematic sources...")
        for domain in problematic_domains:
            # Find source by domain
            config_files = []
            search_dirs = [
                tester.capcat_root / "Config" / "sources" / "active" / "config_driven" / "configs",
                tester.capcat_root / "capcat" / "sources" / "builtin"
            ]

            for search_dir in search_dirs:
                if search_dir.exists():
                    config_files.extend(search_dir.glob("*.yaml"))

            found_source = False
            for config_file in config_files:
                try:
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)

                    if isinstance(config, dict) and 'base_url' in config:
                        if domain in config['base_url']:
                            print(f"\n{'='*60}")
                            tester.test_source(config_file.stem)
                            found_source = True
                            break
                except:
                    continue

            if not found_source:
                print(f"⚠️  No source found for domain: {domain}")

if __name__ == "__main__":
    main()