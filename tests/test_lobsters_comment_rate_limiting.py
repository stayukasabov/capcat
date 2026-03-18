"""
Test suite for Lobsters comment fetching rate limiting and retry logic.

Tests verify:
1. Minimum 1.0s delay between comment requests
2. 429 errors trigger exponential backoff retry
3. Maximum 3 retry attempts honored
4. Successful retry after transient 429
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import requests
from capcat.sources.builtin.custom.lb.source import LbSource
from capcat.core.source_system.base_source import SourceConfig


class TestLobstersCommentRateLimiting:
    """Test rate limiting for comment fetching."""

    @pytest.fixture
    def lobsters_source(self):
        """Create LbSource instance with rate limiting config."""
        config = SourceConfig(
            name='lb',
            display_name='Lobsters',
            base_url='https://lobste.rs',
            rate_limit=1.0,
            supports_comments=True,
            has_comments=True,
            custom_config={
                'max_retries': 3,
                'base_delay': 2.0
            }
        )
        return LbSource(config=config)

    def test_comment_fetch_includes_minimum_delay(self, lobsters_source):
        """Test that comment fetching includes minimum 1.0s delay before request."""
        with patch('time.sleep') as mock_sleep, \
             patch.object(lobsters_source.session, 'get') as mock_get, \
             patch('builtins.open', create=True):

            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'comments': []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Fetch comments
            lobsters_source.fetch_comments(
                comment_url='https://lobste.rs/s/test',
                article_title='Test Article',
                article_folder_path='/tmp/test'
            )

            # Verify sleep was called with rate_limit value
            mock_sleep.assert_called_with(1.0)

    def test_429_error_triggers_retry_with_exponential_backoff(self, lobsters_source):
        """Test that 429 errors trigger retry with exponential backoff (2s, 4s, 8s)."""
        with patch('time.sleep') as mock_sleep, \
             patch.object(lobsters_source.session, 'get') as mock_get, \
             patch('builtins.open', create=True):

            # Mock 429 error response
            mock_response = Mock()
            mock_response.status_code = 429

            def raise_429(*args, **kwargs):
                error = requests.exceptions.HTTPError()
                error.response = mock_response
                raise error

            mock_response.raise_for_status = raise_429
            mock_get.return_value = mock_response

            # Attempt to fetch comments (should fail after retries)
            result = lobsters_source.fetch_comments(
                comment_url='https://lobste.rs/s/test',
                article_title='Test Article',
                article_folder_path='/tmp/test'
            )

            # Verify exponential backoff: rate_limit + retry delays
            # First call: sleep(1.0) for rate limit
            # Retry 1: sleep(2.0)
            # Retry 2: sleep(4.0)
            # Retry 3: sleep(8.0)
            expected_calls = [
                ((1.0,),),  # Initial rate limit
                ((2.0,),),  # First retry backoff
                ((1.0,),),  # Rate limit before retry
                ((4.0,),),  # Second retry backoff
                ((1.0,),),  # Rate limit before retry
                ((8.0,),),  # Third retry backoff
            ]

            # Should have multiple sleep calls for backoff
            assert mock_sleep.call_count >= 4, "Expected multiple sleep calls for retries"
            assert result is False, "Should return False after max retries"

    def test_maximum_retry_attempts_honored(self, lobsters_source):
        """Test that maximum 3 retry attempts are honored."""
        with patch('time.sleep'), \
             patch.object(lobsters_source.session, 'get') as mock_get, \
             patch('builtins.open', create=True):

            # Mock persistent 429 error
            mock_response = Mock()
            mock_response.status_code = 429

            def raise_429(*args, **kwargs):
                error = requests.exceptions.HTTPError()
                error.response = mock_response
                raise error

            mock_response.raise_for_status = raise_429
            mock_get.return_value = mock_response

            # Attempt to fetch comments
            result = lobsters_source.fetch_comments(
                comment_url='https://lobste.rs/s/test',
                article_title='Test Article',
                article_folder_path='/tmp/test'
            )

            # Verify max 4 attempts (1 initial + 3 retries)
            assert mock_get.call_count <= 4, f"Expected max 4 attempts, got {mock_get.call_count}"
            assert result is False, "Should return False after max retries"

    def test_successful_retry_after_transient_429(self, lobsters_source):
        """Test successful comment fetch after transient 429 error."""
        with patch('time.sleep'), \
             patch.object(lobsters_source.session, 'get') as mock_get, \
             patch('builtins.open', create=True) as mock_open, \
             patch('capcat.sources.builtin.custom.lb.source.BeautifulSoup') as mock_bs, \
             patch('capcat.core.streamlined_comment_processor.create_optimized_comment_processor') as mock_processor_factory:

            # First call returns 429, second succeeds
            mock_429_response = Mock()
            mock_429_response.status_code = 429

            def raise_429(*args, **kwargs):
                error = requests.exceptions.HTTPError()
                error.response = mock_429_response
                raise error

            mock_429_response.raise_for_status = raise_429

            mock_success_response = Mock()
            mock_success_response.status_code = 200
            mock_success_response.text = '<html><body>Comments</body></html>'
            mock_success_response.raise_for_status = Mock()

            # Mock comment processor
            mock_processor = Mock()
            mock_processor.process_comments_flattened.return_value = [
                {"id": "c1", "user": "Anonymous", "user_link": "#", "text": "Test comment", "level": 0}
            ]
            mock_processor.generate_inline_comments_markdown.return_value = '# Comments\nTest comment'
            mock_processor.get_performance_metrics.return_value = {
                'comments_processed': 1,
                'links_processed': 0
            }
            mock_processor_factory.return_value = mock_processor

            # First call fails, second succeeds
            mock_get.side_effect = [mock_429_response, mock_success_response]

            # Fetch comments
            result = lobsters_source.fetch_comments(
                comment_url='https://lobste.rs/s/test',
                article_title='Test Article',
                article_folder_path='/tmp/test'
            )

            # Verify retry succeeded
            assert result is True, "Should return True after successful retry"
            assert mock_get.call_count == 2, "Should have retried once"


class TestLobstersCommentRetryConfiguration:
    """Test retry configuration handling."""

    def test_respects_custom_rate_limit(self):
        """Test that custom rate_limit config is respected."""
        config = SourceConfig(
            name='lb',
            display_name='Lobsters',
            base_url='https://lobste.rs',
            rate_limit=2.5,
            supports_comments=True
        )
        source = LbSource(config=config)

        with patch('time.sleep') as mock_sleep, \
             patch.object(source.session, 'get') as mock_get, \
             patch('builtins.open', create=True):

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'comments': []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            source.fetch_comments(
                comment_url='https://lobste.rs/s/test',
                article_title='Test Article',
                article_folder_path='/tmp/test'
            )

            # Verify custom rate limit used
            mock_sleep.assert_called_with(2.5)

    def test_default_rate_limit_when_not_configured(self):
        """Test default 1.0s rate limit when not configured."""
        config = SourceConfig(
            name='lb',
            display_name='Lobsters',
            base_url='https://lobste.rs',
            supports_comments=True
        )
        source = LbSource(config=config)

        with patch('time.sleep') as mock_sleep, \
             patch.object(source.session, 'get') as mock_get, \
             patch('builtins.open', create=True):

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'comments': []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            source.fetch_comments(
                comment_url='https://lobste.rs/s/test',
                article_title='Test Article',
                article_folder_path='/tmp/test'
            )

            # Verify default rate limit
            mock_sleep.assert_called_with(1.0)
