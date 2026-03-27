#!/usr/bin/env python3
"""
Quick Troubleshoot Script
Immediately diagnose the three failing URLs from the error messages.
"""

import requests
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time

class QuickTroubleshooter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def test_url(self, url, name):
        """Quick test of a problematic URL."""
        print(f"\n🔍 Testing: {name}")
        print(f"🔗 URL: {url}")
        print("-" * 80)

        try:
            # Test basic connectivity
            print("1️⃣  Testing connectivity...")
            response = self.session.get(url, timeout=15)

            print(f"   ✅ Status: {response.status_code}")
            print(f"   📏 Size: {len(response.content):,} bytes")
            print(f"   🏷️  Content-Type: {response.headers.get('content-type', 'unknown')}")

            # Check for bot protection
            print("2️⃣  Checking for bot protection...")
            content = response.text.lower()

            bot_indicators = [
                ('Cloudflare', ['checking your browser', 'cloudflare challenge']),
                ('Access Denied', ['access denied', 'forbidden', '403']),
                ('Rate Limited', ['rate limit', 'too many requests']),
                ('Bot Detection', ['bot detected', 'captcha', 'recaptcha'])
            ]

            protection_found = False
            for protection_type, indicators in bot_indicators:
                for indicator in indicators:
                    if indicator in content:
                        print(f"   ⚠️  {protection_type}: {indicator}")
                        protection_found = True

            if not protection_found:
                print("   ✅ No obvious bot protection detected")

            # Parse HTML and check content structure
            print("3️⃣  Analyzing content structure...")
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check for title
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)[:100]
                print(f"   📰 Title: {title}...")
            else:
                print("   ❌ No title found")

            # Check for main content areas
            content_selectors = ['article', 'main', '.content', '.post', '.article-content']
            content_found = False

            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    text_length = len(elements[0].get_text(strip=True))
                    word_count = len(elements[0].get_text(strip=True).split())
                    print(f"   📋 {selector}: {word_count} words ({text_length} chars)")
                    content_found = True
                    break

            if not content_found:
                print("   ❌ No obvious content containers found")

            # Check total text content
            total_text = soup.get_text(strip=True)
            total_words = len(total_text.split())
            print(f"   📊 Total text: {total_words} words ({len(total_text)} chars)")

            if total_words < 50:
                print("   ⚠️  Very little text content - likely a problem")

            # Look for dynamic content indicators
            if 'javascript' in content or 'loading' in content:
                print("   ⚠️  May have dynamic/JavaScript content")

            return {
                'status': response.status_code,
                'size': len(response.content),
                'words': total_words,
                'protection': protection_found,
                'accessible': response.status_code == 200 and total_words > 50
            }

        except requests.exceptions.Timeout:
            print("   ❌ Request timed out")
            return {'error': 'timeout'}
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection failed")
            return {'error': 'connection'}
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            return {'error': str(e)}
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            return {'error': str(e)}

    def run_quick_test(self):
        """Run quick tests on the problematic URLs."""
        print("🚨 CAPCAT TROUBLESHOOTING - QUICK DIAGNOSIS")
        print("=" * 80)

        problematic_urls = [
            ("https://percepta.ai/blog/constructing-llm-computer", "Constructing an LLM-Computer"),
            ("https://www.forbes.com/sites/joetoscano1/2026/03/06/google-just-patented-the-end-of-your-website/", "Forbes - Google Patent"),
            ("https://ahwoo.com/news/4807024/kitten-space-agency/planetary-rings", "Planetary Rings")
        ]

        results = []
        for url, name in problematic_urls:
            result = self.test_url(url, name)
            result['url'] = url
            result['name'] = name
            results.append(result)
            time.sleep(1)  # Be respectful

        # Summary
        print("\n" + "=" * 80)
        print("🏁 QUICK DIAGNOSIS SUMMARY")
        print("=" * 80)

        for result in results:
            name = result['name']
            if 'error' in result:
                print(f"❌ {name}: {result['error']}")
            else:
                status = "✅ OK" if result.get('accessible') else "❌ PROBLEM"
                words = result.get('words', 0)
                protection = "🛡️" if result.get('protection') else ""
                print(f"{status} {name}: {words} words {protection}")

        # Recommendations
        print("\n💡 IMMEDIATE RECOMMENDATIONS:")

        for result in results:
            if 'error' not in result:
                if result.get('protection'):
                    print(f"   🛡️  {result['name']}: Bot protection detected - implement delays/different user agent")
                elif result.get('words', 0) < 50:
                    print(f"   📝 {result['name']}: Low content - check extraction selectors")
                elif result.get('accessible'):
                    print(f"   ✅ {result['name']}: Seems accessible - may be selector issue")

def main():
    troubleshooter = QuickTroubleshooter()
    troubleshooter.run_quick_test()

if __name__ == "__main__":
    main()