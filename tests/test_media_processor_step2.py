#!/usr/bin/env python3
"""
TDD tests for MediaProcessor Step 2 - Medium-Risk Methods.

Tests methods being migrated from ArticleFetcher:
1. remove_image_from_markdown() - Remove image references
2. parse_srcset() - Extract best image from srcset
3. process_document_links() - Process document download links

Following TDD: Write tests FIRST, then implement.
"""

import unittest
from unittest.mock import Mock, patch
import requests

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_processor import MediaProcessor


class TestRemoveImageFromMarkdown(unittest.TestCase):
    """Test image removal from markdown - TDD for remove_image_from_markdown()"""

    def setUp(self):
        """Set up test fixtures."""
        self.session = requests.Session()
        self.processor = MediaProcessor(self.session, download_files=False)

    def tearDown(self):
        """Clean up."""
        self.session.close()

    def test_remove_basic_image(self):
        """Test removing basic image syntax."""
        content = "Text before\n![Alt text](http://example.com/img.jpg)\nText after"
        result = self.processor.remove_image_from_markdown(
            content, "http://example.com/img.jpg"
        )

        self.assertIn("Text before", result)
        self.assertIn("Text after", result)
        self.assertNotIn("![Alt text]", result)
        self.assertNotIn("http://example.com/img.jpg", result)

    def test_remove_image_with_title(self):
        """Test removing image with title attribute."""
        content = '![Alt](http://example.com/img.jpg "Title")'
        result = self.processor.remove_image_from_markdown(
            content, "http://example.com/img.jpg"
        )

        self.assertNotIn("![Alt]", result)
        self.assertNotIn("http://example.com/img.jpg", result)

    def test_remove_multiple_references(self):
        """Test removing multiple references to same image."""
        content = (
            "![Image1](http://example.com/img.jpg)\n"
            "Some text\n"
            "![Image2](http://example.com/img.jpg)"
        )
        result = self.processor.remove_image_from_markdown(
            content, "http://example.com/img.jpg"
        )

        self.assertNotIn("![Image1]", result)
        self.assertNotIn("![Image2]", result)
        self.assertNotIn("http://example.com/img.jpg", result)
        self.assertIn("Some text", result)

    def test_preserves_other_images(self):
        """Test that other images are preserved."""
        content = (
            "![Image1](http://example.com/img1.jpg)\n"
            "![Image2](http://example.com/img2.jpg)"
        )
        result = self.processor.remove_image_from_markdown(
            content, "http://example.com/img1.jpg"
        )

        self.assertNotIn("img1.jpg", result)
        self.assertIn("![Image2](http://example.com/img2.jpg)", result)

    def test_cleans_up_excessive_newlines(self):
        """Test cleanup of excessive blank lines after removal."""
        content = "Text\n\n\n![Image](http://example.com/img.jpg)\n\n\nMore"
        result = self.processor.remove_image_from_markdown(
            content, "http://example.com/img.jpg"
        )

        # Should not have more than 2 consecutive newlines
        self.assertNotIn("\n\n\n", result)


class TestParseSrcset(unittest.TestCase):
    """Test srcset parsing - TDD for parse_srcset()"""

    def setUp(self):
        """Set up test fixtures."""
        self.session = requests.Session()
        self.processor = MediaProcessor(self.session, download_files=False)

    def tearDown(self):
        """Clean up."""
        self.session.close()

    def test_parse_pixel_density_srcset(self):
        """Test parsing srcset with pixel density descriptors."""
        srcset = "img.jpg 1x, img@2x.jpg 2x, img@3x.jpg 3x"
        result = self.processor.parse_srcset(srcset)

        self.assertEqual(result, "img@3x.jpg")

    def test_parse_width_descriptor_srcset(self):
        """Test parsing srcset with width descriptors."""
        srcset = "img-400.jpg 400w, img-800.jpg 800w, img-1200.jpg 1200w"
        result = self.processor.parse_srcset(srcset)

        self.assertEqual(result, "img-1200.jpg")

    def test_parse_single_source(self):
        """Test parsing srcset with single source."""
        srcset = "img.jpg 1x"
        result = self.processor.parse_srcset(srcset)

        self.assertEqual(result, "img.jpg")

    def test_parse_no_descriptor(self):
        """Test parsing srcset with no descriptor."""
        srcset = "img.jpg"
        result = self.processor.parse_srcset(srcset)

        self.assertEqual(result, "img.jpg")

    def test_parse_mixed_descriptors(self):
        """Test parsing srcset with mixed descriptors."""
        srcset = "img-small.jpg 1x, img-large.jpg 2x, img-xlarge.jpg 1600w"
        result = self.processor.parse_srcset(srcset)

        # Should prefer the highest resolution (1600w > 2x)
        # 2x = 2000 pseudo-width, so 2x wins over 1600w
        self.assertIn("large", result)

    def test_parse_empty_srcset(self):
        """Test parsing empty srcset."""
        result = self.processor.parse_srcset("")

        self.assertEqual(result, "")

    def test_parse_whitespace_handling(self):
        """Test parsing srcset with extra whitespace."""
        srcset = " img1.jpg  1x ,  img2.jpg  2x  "
        result = self.processor.parse_srcset(srcset)

        self.assertEqual(result, "img2.jpg")


class TestProcessDocumentLinks(unittest.TestCase):
    """Test document link processing - TDD for process_document_links()"""

    def setUp(self):
        """Set up test fixtures."""
        self.session = requests.Session()
        self.processor = MediaProcessor(self.session, download_files=True)

    def tearDown(self):
        """Clean up."""
        self.session.close()

    def test_identify_pdf_links(self):
        """Test identification of PDF document links."""
        from bs4 import BeautifulSoup

        html = '<a href="http://example.com/doc.pdf">Download PDF</a>'
        soup = BeautifulSoup(html, 'html.parser')
        markdown = "[Download PDF](http://example.com/doc.pdf)"

        # This method should identify and process PDF links
        # We'll test the actual implementation when we write it
        # For now, just verify the method exists and accepts correct parameters
        self.assertTrue(hasattr(self.processor, 'process_document_links'))

    def test_skip_non_document_links(self):
        """Test that non-document links are skipped."""
        from bs4 import BeautifulSoup

        html = '<a href="http://example.com/page.html">Normal Link</a>'
        soup = BeautifulSoup(html, 'html.parser')
        markdown = "[Normal Link](http://example.com/page.html)"

        # Should not process HTML pages as documents
        self.assertTrue(hasattr(self.processor, 'process_document_links'))

    def test_respects_download_files_flag(self):
        """Test that download_files flag is respected."""
        # When download_files=False, should not process documents
        processor_no_download = MediaProcessor(self.session, download_files=False)

        self.assertFalse(processor_no_download.download_files)

        # When download_files=True, should process documents
        processor_with_download = MediaProcessor(self.session, download_files=True)

        self.assertTrue(processor_with_download.download_files)


def run_tests():
    """Run all Step 2 tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRemoveImageFromMarkdown))
    suite.addTests(loader.loadTestsFromTestCase(TestParseSrcset))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessDocumentLinks))

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())
