#!/usr/bin/env python3
"""
Capcat Log Analyzer
Analyzes Capcat logs to identify patterns in failures and warnings.
"""

import re
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime
import argparse

class CapcatLogAnalyzer:
    def __init__(self):
        self.log_patterns = {
            'empty_markdown': r'WARNING: Empty markdown for (.+?)(?:\s|$)',
            'content_fetch_failed': r'WARNING: Content fetch failed for: (.+?)(?:\s|$)',
            'access_forbidden': r'WARNING: Access forbidden for article (.+?) - (.+?)(?:\s|$)',
            'pdf_download_failed': r'WARNING: PDF download failed for (.+?): (.+?)(?:\s|$)',
            'pdf_download_none': r'WARNING: PDF download returned None for: (.+?)(?:\s|$)',
            'network_error': r'WARNING: NetworkError: (.+?)(?:\s|$)',
            'timeout_error': r'WARNING: TimeoutError: (.+?)(?:\s|$)',
            'parse_error': r'WARNING: ParseError: (.+?)(?:\s|$)',
        }

    def analyze_log_file(self, log_file):
        """Analyze a log file for patterns."""
        print(f"📊 Analyzing log file: {log_file}")

        if not Path(log_file).exists():
            print(f"❌ Log file not found: {log_file}")
            return

        with open(log_file, 'r') as f:
            content = f.read()

        return self.analyze_log_content(content)

    def analyze_log_content(self, content):
        """Analyze log content for patterns."""
        results = {
            'total_lines': len(content.splitlines()),
            'patterns': {},
            'failed_domains': Counter(),
            'error_types': Counter(),
            'timeline': defaultdict(list)
        }

        lines = content.splitlines()

        for line in lines:
            # Extract timestamp if present
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            timestamp = timestamp_match.group(1) if timestamp_match else None

            # Check each pattern
            for pattern_name, pattern in self.log_patterns.items():
                matches = re.finditer(pattern, line)

                for match in matches:
                    if pattern_name not in results['patterns']:
                        results['patterns'][pattern_name] = []

                    match_data = {
                        'line': line,
                        'groups': match.groups(),
                        'timestamp': timestamp
                    }

                    results['patterns'][pattern_name].append(match_data)

                    # Extract domain from URL if present
                    url_groups = [g for g in match.groups() if g and ('http' in g or '.com' in g or '.org' in g)]
                    if url_groups:
                        from urllib.parse import urlparse
                        try:
                            domain = urlparse(url_groups[0]).netloc
                            results['failed_domains'][domain] += 1
                        except:
                            pass

                    # Categorize error type
                    results['error_types'][pattern_name] += 1

                    # Timeline
                    if timestamp:
                        results['timeline'][timestamp].append({
                            'type': pattern_name,
                            'data': match.groups()
                        })

        return results

    def print_analysis_report(self, results):
        """Print a comprehensive analysis report."""
        print("\n" + "="*80)
        print("CAPCAT LOG ANALYSIS REPORT")
        print("="*80)

        print(f"\n📊 SUMMARY:")
        print(f"Total log lines: {results['total_lines']:,}")
        print(f"Total issues found: {sum(len(patterns) for patterns in results['patterns'].values())}")

        # Error type breakdown
        print(f"\n🚨 ERROR TYPE BREAKDOWN:")
        for error_type, count in results['error_types'].most_common():
            percentage = (count / results['total_lines']) * 100
            print(f"  {error_type:20} {count:5} issues ({percentage:.1f}%)")

        # Failed domains
        print(f"\n🌐 TOP FAILING DOMAINS:")
        for domain, count in results['failed_domains'].most_common(10):
            print(f"  {domain:30} {count:3} failures")

        # Detailed pattern analysis
        print(f"\n🔍 DETAILED ANALYSIS:")

        for pattern_name, matches in results['patterns'].items():
            if not matches:
                continue

            print(f"\n  📋 {pattern_name.upper()}:")
            print(f"     Total: {len(matches)} occurrences")

            # Show sample matches
            print(f"     Samples:")
            for i, match in enumerate(matches[:3]):
                print(f"       {i+1}. {match['groups'][0] if match['groups'] else 'N/A'}")

            # Pattern-specific analysis
            if pattern_name == 'empty_markdown':
                self.analyze_empty_markdown_pattern(matches)
            elif pattern_name == 'access_forbidden':
                self.analyze_access_forbidden_pattern(matches)

    def analyze_empty_markdown_pattern(self, matches):
        """Analyze empty markdown patterns."""
        print(f"     Analysis:")

        domains = Counter()
        for match in matches:
            if match['groups']:
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(match['groups'][0]).netloc
                    domains[domain] += 1
                except:
                    pass

        print(f"       Affected domains: {len(domains)}")
        for domain, count in domains.most_common(3):
            print(f"         {domain}: {count} articles")

    def analyze_access_forbidden_pattern(self, matches):
        """Analyze access forbidden patterns."""
        print(f"     Analysis:")

        protection_types = Counter()
        for match in matches:
            if len(match['groups']) > 1:
                protection_type = match['groups'][1]
                protection_types[protection_type] += 1

        print(f"       Protection types:")
        for protection, count in protection_types.most_common():
            print(f"         {protection}: {count} occurrences")

    def analyze_recent_logs(self):
        """Analyze recent Capcat execution logs."""
        print("🔍 Looking for recent Capcat logs...")

        # Common log locations
        log_locations = [
            Path.home() / ".capcat" / "logs",
            Path.cwd() / "logs",
            Path("/tmp/capcat.log"),
            Path("/var/log/capcat.log"),
        ]

        found_logs = []
        for location in log_locations:
            if location.is_file():
                found_logs.append(location)
            elif location.is_dir():
                found_logs.extend(location.glob("*.log"))

        if not found_logs:
            print("❌ No log files found in common locations")
            print("💡 Try running with: python log-analyzer.py <path-to-log-file>")
            return

        print(f"✅ Found {len(found_logs)} log files")

        # Analyze most recent
        most_recent = max(found_logs, key=lambda p: p.stat().st_mtime)
        print(f"📄 Analyzing most recent: {most_recent}")

        results = self.analyze_log_file(most_recent)
        self.print_analysis_report(results)

    def analyze_from_input(self, log_input):
        """Analyze log content from various inputs."""
        if Path(log_input).exists():
            # It's a file
            results = self.analyze_log_file(log_input)
        else:
            # Treat as direct log content
            results = self.analyze_log_content(log_input)

        self.print_analysis_report(results)

    def generate_recommendations(self, results):
        """Generate recommendations based on analysis."""
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)

        # Empty markdown issues
        empty_markdown_count = len(results['patterns'].get('empty_markdown', []))
        if empty_markdown_count > 0:
            print(f"\n🔧 EMPTY MARKDOWN ISSUES ({empty_markdown_count} found):")
            print("   Possible causes:")
            print("   • Content extraction selectors are outdated")
            print("   • Website changed structure")
            print("   • Content is dynamically loaded via JavaScript")
            print("   • Anti-bot protection blocks content")
            print()
            print("   Solutions:")
            print("   • Run source-tester.py to test extraction patterns")
            print("   • Update article_selectors in source configs")
            print("   • Check for dynamic content loading")
            print("   • Update user agent strings")

        # Access forbidden issues
        access_forbidden_count = len(results['patterns'].get('access_forbidden', []))
        if access_forbidden_count > 0:
            print(f"\n🛡️  ACCESS FORBIDDEN ISSUES ({access_forbidden_count} found):")
            print("   Possible causes:")
            print("   • Cloudflare/bot protection")
            print("   • Rate limiting")
            print("   • User agent blocking")
            print("   • Geographic restrictions")
            print()
            print("   Solutions:")
            print("   • Implement request delays")
            print("   • Use rotating user agents")
            print("   • Add proxy support")
            print("   • Consider headless browser for JS-heavy sites")

        # Network issues
        network_count = len(results['patterns'].get('network_error', []))
        if network_count > 0:
            print(f"\n🌐 NETWORK ISSUES ({network_count} found):")
            print("   Solutions:")
            print("   • Increase timeout values")
            print("   • Add retry logic")
            print("   • Check internet connectivity")
            print("   • Monitor DNS resolution")

def main():
    parser = argparse.ArgumentParser(description='Analyze Capcat logs for issues')
    parser.add_argument('input', nargs='?', help='Log file path or log content')
    parser.add_argument('--recommendations', action='store_true', help='Generate recommendations')

    args = parser.parse_args()

    analyzer = CapcatLogAnalyzer()

    if args.input:
        analyzer.analyze_from_input(args.input)
    else:
        # Analyze the provided error messages
        sample_log = """
Capcat Info: WARNING: Empty markdown for https://percepta.ai/blog/constructing-llm-computer
Capcat Info: WARNING: Content fetch failed for: Constructing an LLM-Computer
Capcat Info: WARNING: Access forbidden for article https://www.forbes.com/sites/joetoscano1/2026/03/06/google-just-patented-the-end-of-your-website/ - anti-bot protection detected
Capcat Info: WARNING: Content fetch failed for: Google Just Patented The End Of Your Website
Capcat Info: WARNING: Empty markdown for https://ahwoo.com/news/4807024/kitten-space-agency/planetary-rings
Capcat Info: WARNING: Content fetch failed for: Planetary rings
        """

        print("📋 Analyzing provided error messages...")
        results = analyzer.analyze_log_content(sample_log)
        analyzer.print_analysis_report(results)

        if args.recommendations:
            analyzer.generate_recommendations(results)

if __name__ == "__main__":
    main()