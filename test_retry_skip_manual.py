#!/usr/bin/env python3
"""
Manual test script for retry-skip logic.
Tests the GREEN phase implementation.
"""

import requests
from unittest.mock import Mock, MagicMock
from sources.active.custom.lb.source import LbSource
from core.source_system.base_source import SourceConfig
from core.network_resilience import get_skip_tracker, reset_retry_state


def test_lobsters_skip_on_timeout():
    """Test that lobsters source skips after 2 timeout attempts."""
    print("Testing: Lobsters skip on timeout...")

    # Reset retry state
    reset_retry_state()

    # Create lobsters source
    config = SourceConfig(
        name='lb',
        display_name='Lobsters',
        base_url='https://lobste.rs',
        timeout=5.0,
    )

    # Mock session to simulate timeouts
    mock_session = Mock()
    mock_session.get.side_effect = requests.exceptions.Timeout("Connection timeout")

    source = LbSource(config, session=mock_session)

    # Discover articles (should skip after 2 failures)
    articles = source.discover_articles(count=10)

    # Verify skip behavior
    assert articles == [], f"Expected empty list after skip, got {len(articles)} articles"

    # Verify skip was tracked
    skip_tracker = get_skip_tracker()
    skip_summary = skip_tracker.get_summary()

    print(f"  Skipped sources: {skip_summary['total_skipped']}")
    print(f"  Skip details: {skip_summary['skipped']}")

    assert skip_summary['total_skipped'] > 0, "Should have skipped at least one source"

    print("  PASS: Source correctly skipped after timeout")


def test_successful_retry():
    """Test that source succeeds on retry if connection recovers."""
    print("\nTesting: Successful retry on second attempt...")

    # Reset retry state
    reset_retry_state()

    config = SourceConfig(
        name='test',
        display_name='Test Source',
        base_url='https://test.com',
        timeout=5.0,
    )

    # Mock session that fails once then succeeds
    mock_session = Mock()
    call_count = [0]

    def side_effect_func(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            raise requests.exceptions.Timeout("First attempt timeout")
        # Second attempt succeeds
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'''<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Test Article</title>
                    <link>https://test.com/article</link>
                    <comments>https://test.com/comments</comments>
                </item>
            </channel>
        </rss>
        '''
        mock_response.raise_for_status = Mock()
        return mock_response

    mock_session.get.side_effect = side_effect_func

    source = LbSource(config, session=mock_session)

    # Discover articles (should succeed on retry)
    articles = source.discover_articles(count=10)

    assert len(articles) > 0, "Should have discovered articles on retry"
    print(f"  Discovered {len(articles)} articles on retry")
    print("  PASS: Retry succeeded as expected")


def test_skip_summary_format():
    """Test that skip summary has correct format."""
    print("\nTesting: Skip summary format...")

    reset_retry_state()

    config = SourceConfig(
        name='format_test',
        display_name='Format Test',
        base_url='https://test.com',
        timeout=5.0,
    )

    mock_session = Mock()
    mock_session.get.side_effect = requests.exceptions.ConnectionError("Connection refused")

    source = LbSource(config, session=mock_session)
    articles = source.discover_articles(count=10)

    skip_tracker = get_skip_tracker()
    skip_summary = skip_tracker.get_summary()

    assert 'skipped' in skip_summary, "Summary should have 'skipped' key"
    assert 'total_skipped' in skip_summary, "Summary should have 'total_skipped' key"

    if skip_summary['total_skipped'] > 0:
        source_name = list(skip_summary['skipped'].keys())[0]
        skip_info = skip_summary['skipped'][source_name]

        assert 'reason' in skip_info, "Skip info should have 'reason'"
        assert 'attempts' in skip_info, "Skip info should have 'attempts'"
        assert 'error_type' in skip_info, "Skip info should have 'error_type'"

        print(f"  Skip info format: {skip_info}")
        print("  PASS: Skip summary has correct format")


if __name__ == '__main__':
    try:
        test_lobsters_skip_on_timeout()
        test_successful_retry()
        test_skip_summary_format()

        print("\n" + "="*60)
        print("GREEN PHASE VALIDATION: All manual tests PASSED")
        print("="*60)

    except AssertionError as e:
        print(f"\nFAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
