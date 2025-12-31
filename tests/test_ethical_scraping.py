import unittest
from unittest.mock import patch, MagicMock
import requests
from core.article_fetcher import ArticleFetcher
from core.ethical_scraping import get_ethical_manager

class TestEthicalScraping(unittest.TestCase):

    def setUp(self):
        # Reset the global manager before each test to clear cache
        get_ethical_manager.__globals__['_global_manager'] = None
        self.session = requests.Session()
        class TestArticleFetcher(ArticleFetcher):
            def should_skip_url(self, url: str, title: str) -> bool:
                return False
        self.fetcher = TestArticleFetcher(self.session, source_code='test')

    @patch('requests.Session.get')
    @patch('requests.get')
    def test_disallowed_url_raises_exception(self, mock_get_req, mock_get_sess):
        """Test that a disallowed URL raises a RequestException."""
        robots_txt_content = "User-agent: *\nDisallow: /private/"
        mock_response = MagicMock()
        mock_response.text = robots_txt_content
        mock_response.status_code = 200
        mock_get_req.return_value = mock_response

        disallowed_url = "http://example.com/private/article.html"

        with self.assertRaises(requests.RequestException) as cm:
            self.fetcher._fetch_url_with_retry(disallowed_url)
        
        self.assertIn("URL blocked by robots.txt", str(cm.exception))

    @patch('requests.Session.get')
    @patch('requests.get')
    def test_allowed_url_fetches_successfully(self, mock_get_req, mock_get_sess):
        """Test that an allowed URL is fetched without raising an exception."""
        robots_txt_content = "User-agent: *\nDisallow: /private/"
        mock_robots_response = MagicMock()
        mock_robots_response.text = robots_txt_content
        mock_robots_response.status_code = 200

        mock_article_response = MagicMock()
        mock_article_response.status_code = 200
        mock_article_response.text = "<html><head><title>Test</title></head><body>Article content</body></html>"

        # First call for robots.txt, second for the article
        mock_get_req.side_effect = [mock_robots_response, mock_article_response]
        mock_get_sess.side_effect = [mock_robots_response, mock_article_response]

        allowed_url = "http://example.com/public/article.html"

        try:
            response = self.fetcher._fetch_url_with_retry(allowed_url)
            self.assertEqual(response.status_code, 200)
        except requests.RequestException as e:
            self.fail(f"_fetch_url_with_retry() raised RequestException unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()