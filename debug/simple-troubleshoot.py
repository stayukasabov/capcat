#!/usr/bin/env python3
"""
Simple troubleshoot script without emojis per CLAUDE.md
"""

import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def test_url_simple(url, name):
    """Test URL with minimal output."""
    print(f"\nTesting: {name}")
    print(f"URL: {url}")
    print("-" * 60)

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        response = session.get(url, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Size: {len(response.content):,} bytes")

        soup = BeautifulSoup(response.content, 'html.parser')
        total_text = soup.get_text(strip=True)
        word_count = len(total_text.split())

        print(f"Words: {word_count}")

        # Check for bot protection indicators
        content_lower = response.text.lower()
        if any(indicator in content_lower for indicator in ['captcha', 'cloudflare', 'checking your browser']):
            print("Bot protection: DETECTED")
        else:
            print("Bot protection: None detected")

        # Simple assessment
        if response.status_code == 200 and word_count > 50:
            print("Assessment: ACCESSIBLE")
        elif response.status_code == 403:
            print("Assessment: BLOCKED")
        else:
            print("Assessment: PROBLEM")

    except Exception as e:
        print(f"Error: {e}")

def main():
    urls = [
        ("https://percepta.ai/blog/constructing-llm-computer", "percepta.ai"),
        ("https://www.forbes.com/sites/joetoscano1/2026/03/06/google-just-patented-the-end-of-your-website/", "forbes.com"),
        ("https://ahwoo.com/news/4807024/kitten-space-agency/planetary-rings", "ahwoo.com")
    ]

    print("CAPCAT TROUBLESHOOTING")
    print("=" * 60)

    for url, name in urls:
        test_url_simple(url, name)

    print("\nRECOMMENDations:")
    print("- percepta.ai: Update content extraction selectors")
    print("- forbes.com: Implement anti-bot workarounds")
    print("- ahwoo.com: Verify article exists or handle dynamic content")

if __name__ == "__main__":
    main()