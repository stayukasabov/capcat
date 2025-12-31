#!/usr/bin/env python3
"""
TDD tests for MediaProcessor Step 1 - Low-Risk Methods.

Tests methods being migrated from ArticleFetcher:
1. _is_pdf_url() - PDF detection
2. _cleanup_empty_images_folder() - Empty folder cleanup
3. _should_skip_image() - UI element detection
4. _cleanup_failed_media_reference() - Failed media cleanup

Following TDD: Write tests FIRST, then implement.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock
import requests

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media_processor import MediaProcessor


class TestPDFDetection(unittest.TestCase):
    """Test PDF URL detection - TDD for _is_pdf_url()"""

    def setUp(self):
        """Set up test fixtures."""
        self.session = requests.Session()
        self.processor = MediaProcessor(self.session, download_files=False)

    def tearDown(self):
        """Clean up."""
        self.session.close()

    def test_pdf_url_with_extension(self):
        """Test PDF URL with .pdf extension."""
        url = "https://example.com/document.pdf"
        result = self.processor.is_pdf_url(url)
        self.assertTrue(result)

    def test_pdf_url_case_insensitive(self):
        """Test PDF detection is case insensitive."""
        urls = [
            "https://example.com/doc.PDF",
            "https://example.com/doc.Pdf",
            "https://example.com/doc.pDf"
        ]
        for url in urls:
            with self.subTest(url=url):
                result = self.processor.is_pdf_url(url)
                self.assertTrue(result)

    def test_pdf_url_with_query_params(self):
        """Test PDF URL with query parameters."""
        url = "https://example.com/document.pdf?download=true&id=123"
        result = self.processor.is_pdf_url(url)
        self.assertTrue(result)

    def test_non_pdf_url(self):
        """Test non-PDF URLs return False."""
        urls = [
            "https://example.com/page.html",
            "https://example.com/image.jpg",
            "https://example.com/doc.docx",
            "https://example.com/",
        ]
        for url in urls:
            with self.subTest(url=url):
                result = self.processor.is_pdf_url(url)
                self.assertFalse(result)

    def test_pdf_in_path_but_not_extension(self):
        """Test URL containing 'pdf' but not .pdf extension."""
        url = "https://example.com/pdf-viewer/document.html"
        result = self.processor.is_pdf_url(url)
        self.assertFalse(result)


class TestCleanupEmptyImagesFolder(unittest.TestCase):
    """Test empty images folder cleanup - TDD for _cleanup_empty_images_folder()"""

    def setUp(self):
        """Set up test fixtures."""
        self.session = requests.Session()
        self.processor = MediaProcessor(self.session, download_files=False)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        self.session.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_removes_empty_images_folder(self):
        """Test that empty images folder is removed."""
        images_folder = os.path.join(self.temp_dir, "images")
        os.makedirs(images_folder)

        # Verify folder exists
        self.assertTrue(os.path.exists(images_folder))

        # Clean up empty folder
        self.processor.cleanup_empty_images_folder(self.temp_dir)

        # Verify folder was removed
        self.assertFalse(os.path.exists(images_folder))

    def test_preserves_images_folder_with_files(self):
        """Test that images folder with files is NOT removed."""
        images_folder = os.path.join(self.temp_dir, "images")
        os.makedirs(images_folder)

        # Add a file to the folder
        test_file = os.path.join(images_folder, "test.jpg")
        with open(test_file, "w") as f:
            f.write("test")

        # Attempt cleanup
        self.processor.cleanup_empty_images_folder(self.temp_dir)

        # Verify folder still exists
        self.assertTrue(os.path.exists(images_folder))
        self.assertTrue(os.path.exists(test_file))

    def test_handles_nonexistent_images_folder(self):
        """Test handling when images folder doesn't exist."""
        # Should not crash
        self.processor.cleanup_empty_images_folder(self.temp_dir)
        # No assertion needed - just verify no exception


class TestShouldSkipImage(unittest.TestCase):
    """Test image skipping logic - TDD for _should_skip_image()"""

    def setUp(self):
        """Set up test fixtures."""
        self.session = requests.Session()
        self.processor = MediaProcessor(self.session, download_files=False)

        # Standard UI patterns
        self.ui_patterns = {
            "class_patterns": ["icon", "logo", "avatar", "badge", "button"],
            "id_patterns": ["header", "footer", "nav", "menu"],
            "alt_patterns": ["icon", "logo", "button"],
            "src_patterns": ["icon", "logo", "sprite", "button"]
        }

    def tearDown(self):
        """Clean up."""
        self.session.close()

    def test_skip_image_with_icon_class(self):
        """Test skipping image with 'icon' class."""
        img_tag = Mock()
        img_tag.get = Mock(side_effect=lambda x, default=None:
            ["icon"] if x == "class" else default)

        result = self.processor.should_skip_image(
            img_tag, "https://example.com/img.jpg", self.ui_patterns
        )
        self.assertTrue(result)

    def test_skip_image_with_logo_in_src(self):
        """Test skipping image with 'logo' in src URL."""
        img_tag = Mock()
        img_tag.get = Mock(return_value=None)

        result = self.processor.should_skip_image(
            img_tag, "https://example.com/logo.png", self.ui_patterns
        )
        self.assertTrue(result)

    def test_skip_tracking_pixel(self):
        """Test skipping tracking pixels."""
        img_tag = Mock()
        img_tag.get = Mock(return_value=None)

        urls = [
            "https://example.com/pixel.gif",
            "https://example.com/beacon.jpg",
            "https://analytics.example.com/track.png",
            "https://example.com/1x1.gif"
        ]

        for url in urls:
            with self.subTest(url=url):
                result = self.processor.should_skip_image(
                    img_tag, url, self.ui_patterns
                )
                self.assertTrue(result)

    def test_keep_content_image(self):
        """Test keeping actual content images."""
        img_tag = Mock()
        img_tag.get = Mock(return_value=None)

        result = self.processor.should_skip_image(
            img_tag, "https://example.com/article-photo.jpg", self.ui_patterns
        )
        self.assertFalse(result)

    def test_skip_with_multiple_classes(self):
        """Test skipping with multiple CSS classes."""
        img_tag = Mock()
        img_tag.get = Mock(side_effect=lambda x, default=None:
            ["img-responsive", "icon", "rounded"] if x == "class" else default)

        result = self.processor.should_skip_image(
            img_tag, "https://example.com/img.jpg", self.ui_patterns
        )
        self.assertTrue(result)


class TestCleanupFailedMediaReference(unittest.TestCase):
    """Test failed media cleanup - TDD for _cleanup_failed_media_reference()"""

    def setUp(self):
        """Set up test fixtures."""
        self.session = requests.Session()
        self.processor = MediaProcessor(self.session, download_files=False)

    def tearDown(self):
        """Clean up."""
        self.session.close()

    def test_cleanup_failed_image_reference(self):
        """Test cleaning up failed image reference."""
        content = "Check this ![Photo](http://example.com/img.jpg) here"
        result = self.processor.cleanup_failed_media_reference(
            content,
            "http://example.com/img.jpg",
            "image",
            "Photo"
        )

        # Should convert to regular link with unavailable notice
        self.assertIn("[Photo](http://example.com/img.jpg)", result)
        self.assertIn("*(image unavailable)*", result)
        self.assertNotIn("![Photo]", result)  # No image syntax

    def test_cleanup_failed_document_reference(self):
        """Test cleaning up failed document reference."""
        content = "Download [Report](http://example.com/doc.pdf) now"
        result = self.processor.cleanup_failed_media_reference(
            content,
            "http://example.com/doc.pdf",
            "document",
            "Report"
        )

        self.assertIn("[Report](http://example.com/doc.pdf)", result)
        self.assertIn("*(document unavailable)*", result)

    def test_cleanup_preserves_other_content(self):
        """Test that other content is preserved."""
        content = (
            "# Title\n\n"
            "Some text.\n\n"
            "![Image](http://example.com/img.jpg)\n\n"
            "More text."
        )
        result = self.processor.cleanup_failed_media_reference(
            content,
            "http://example.com/img.jpg",
            "image",
            "Image"
        )

        self.assertIn("# Title", result)
        self.assertIn("Some text.", result)
        self.assertIn("More text.", result)


def run_tests():
    """Run all Step 1 tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPDFDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestCleanupEmptyImagesFolder))
    suite.addTests(loader.loadTestsFromTestCase(TestShouldSkipImage))
    suite.addTests(loader.loadTestsFromTestCase(TestCleanupFailedMediaReference))

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())
