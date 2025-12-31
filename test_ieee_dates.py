#!/usr/bin/env python3
"""Quick test to verify IEEE Spectrum RSS dates are parsed correctly."""

import requests
from core.source_system.feed_parser import FeedParserFactory

# Fetch IEEE Spectrum RSS
url = "https://spectrum.ieee.org/feeds/feed.rss"
response = requests.get(url, timeout=30)

print("Fetching IEEE Spectrum RSS feed...")
print(f"Status: {response.status_code}\n")

# Parse with our feed parser
items = FeedParserFactory.detect_and_parse(response.content)

print(f"Parsed {len(items)} items\n")
print("First 5 items (should be sorted by date, most recent first):\n")

for i, item in enumerate(items[:5], 1):
    date_str = item.published_date.strftime("%Y-%m-%d %H:%M") if item.published_date else "NO DATE"
    print(f"{i}. {item.title}")
    print(f"   Date: {date_str}")
    print(f"   URL: {item.url}\n")

# Check if dates are actually sorted
print("\n" + "="*70)
print("DATE SORTING VERIFICATION:")
print("="*70)

dates_with_items = [(item.published_date, item.title) for item in items if item.published_date]

if len(dates_with_items) > 1:
    is_sorted = all(
        dates_with_items[i][0] >= dates_with_items[i+1][0]
        for i in range(len(dates_with_items)-1)
    )

    if is_sorted:
        print("✓ SUCCESS: Items are correctly sorted by date (most recent first)")
    else:
        print("✗ FAILURE: Items are NOT sorted correctly")
        print("\nFirst 3 dates:")
        for i, (date, title) in enumerate(dates_with_items[:3], 1):
            print(f"  {i}. {date} - {title}")
else:
    print("⚠ WARNING: Not enough dated items to verify sorting")

print(f"\nItems with dates: {len(dates_with_items)}/{len(items)}")
