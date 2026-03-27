#!/usr/bin/env python3
"""
Source Fix Tool
Automatically suggests and applies fixes for problematic sources.
"""

import yaml
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class SourceFixer:
    def __init__(self, capcat_root="/Volumes/DRIVE B/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat-copy/Application"):
        self.capcat_root = Path(capcat_root)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fix_percepta_ai(self):
        """Fix percepta.ai source configuration."""
        print("🔧 Fixing percepta.ai source...")

        # Test URL to analyze structure
        test_url = "https://percepta.ai/blog/constructing-llm-computer"

        try:
            response = self.session.get(test_url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            print("   📡 Fetched page for analysis")

            # Find actual selectors that work
            title_candidates = [
                ('h1', soup.find('h1')),
                ('title', soup.find('title')),
                ('.title', soup.select_one('.title')),
                ('.post-title', soup.select_one('.post-title')),
                ('h1.title', soup.select_one('h1.title')),
                ('h2', soup.find('h2')),
            ]

            working_title_selector = None
            for selector, elem in title_candidates:
                if elem and len(elem.get_text(strip=True)) > 10:
                    working_title_selector = selector
                    title_text = elem.get_text(strip=True)
                    print(f"   ✅ Found working title selector: {selector}")
                    print(f"      Title: {title_text[:60]}...")
                    break

            content_candidates = [
                ('article', soup.find('article')),
                ('main', soup.find('main')),
                ('.content', soup.select_one('.content')),
                ('.post-content', soup.select_one('.post-content')),
                ('.entry-content', soup.select_one('.entry-content')),
                ('div.content', soup.select_one('div.content')),
                ('section', soup.find('section')),
            ]

            working_content_selector = None
            for selector, elem in content_candidates:
                if elem:
                    text_length = len(elem.get_text(strip=True))
                    word_count = len(elem.get_text(strip=True).split())
                    if word_count > 100:  # Good content threshold
                        working_content_selector = selector
                        print(f"   ✅ Found working content selector: {selector}")
                        print(f"      Content: {word_count} words ({text_length} chars)")
                        break

            # Generate config suggestion
            if working_title_selector and working_content_selector:
                suggested_config = {
                    'article_selectors': {
                        'title': working_title_selector,
                        'content': working_content_selector,
                    }
                }
                print("   💡 Suggested configuration update:")
                print(yaml.dump(suggested_config, indent=2))
                return suggested_config
            else:
                print("   ❌ Could not find working selectors")
                return None

        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            return None

    def fix_ahwoo_com(self):
        """Fix ahwoo.com source configuration."""
        print("🔧 Fixing ahwoo.com source...")

        test_url = "https://ahwoo.com/news/4807024/kitten-space-agency/planetary-rings"

        try:
            response = self.session.get(test_url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            print("   📡 Fetched page for analysis")

            # The page returns very little content (17 words)
            # This suggests either:
            # 1. The article doesn't exist
            # 2. Content is dynamically loaded
            # 3. The URL structure has changed

            total_text = soup.get_text(strip=True)
            print(f"   📊 Total text: {len(total_text.split())} words")

            if len(total_text.split()) < 50:
                print("   ⚠️  Very little content - possible causes:")
                print("      • Article may not exist")
                print("      • Content loaded dynamically via JavaScript")
                print("      • URL structure changed")
                print("      • Site requires authentication")

                # Check if it's a 404-style page
                if '404' in total_text.lower() or 'not found' in total_text.lower():
                    print("   ❌ Article appears to not exist (404)")
                else:
                    print("   💡 Suggestion: Test with a different ahwoo.com URL")

            return None

        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            return None

    def suggest_forbes_workaround(self):
        """Suggest workarounds for Forbes bot protection."""
        print("🛡️ Forbes.com bot protection workarounds...")

        print("   Forbes has aggressive anti-bot protection (Cloudflare)")
        print("   Possible workarounds:")
        print("   • Implement request delays (5-10 seconds between requests)")
        print("   • Use headless browser (Selenium/Playwright)")
        print("   • Try different user agents")
        print("   • Use proxy rotation")
        print("   • Consider RSS feed instead of direct scraping")

        # Check if Forbes has RSS feeds
        rss_candidates = [
            "https://www.forbes.com/real-time/feed2/",
            "https://www.forbes.com/tech/feed2/",
            "https://www.forbes.com/innovation/feed2/",
        ]

        print("\n   📡 Checking Forbes RSS feeds:")
        for rss_url in rss_candidates:
            try:
                response = self.session.get(rss_url, timeout=10)
                if response.status_code == 200 and 'xml' in response.headers.get('content-type', ''):
                    print(f"   ✅ {rss_url}")
                else:
                    print(f"   ❌ {rss_url}")
            except:
                print(f"   ❌ {rss_url}")

    def apply_fixes(self):
        """Apply all fixes for the problematic sources."""
        print("🚀 CAPCAT SOURCE FIXES")
        print("=" * 60)

        # Fix percepta.ai
        print("\n1️⃣ PERCEPTA.AI")
        percepta_config = self.fix_percepta_ai()

        # Fix ahwoo.com
        print("\n2️⃣ AHWOO.COM")
        self.fix_ahwoo_com()

        # Suggest Forbes workaround
        print("\n3️⃣ FORBES.COM")
        self.suggest_forbes_workaround()

        # Summary
        print("\n" + "=" * 60)
        print("📋 SUMMARY")
        print("=" * 60)

        if percepta_config:
            print("✅ percepta.ai: Configuration fix available")
            print("   Apply the suggested article_selectors to the source config")
        else:
            print("❌ percepta.ai: Manual investigation needed")

        print("❌ ahwoo.com: Article may not exist or needs dynamic loading support")
        print("⚠️  forbes.com: Requires anti-bot workarounds")

        print("\n💡 NEXT STEPS:")
        print("1. Update source configurations with suggested selectors")
        print("2. Test sources individually: capcat fetch <source> --count 1")
        print("3. Consider implementing delays and headless browser for protected sites")
        print("4. Monitor logs for similar patterns")

def main():
    fixer = SourceFixer()
    fixer.apply_fixes()

if __name__ == "__main__":
    main()