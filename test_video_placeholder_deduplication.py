#!/usr/bin/env python3
"""
TDD Test Suite: Video Placeholder Deduplication

Test Cases:
1. Multiple video placeholders reduced to single note
2. Multiple audio placeholders reduced to single note
3. Mixed media placeholders handled correctly
4. No emoji in placeholder text
5. Duplicate placeholders removed from DOM
"""

import unittest
from core.formatter import html_to_markdown


class TestVideoPlaceholderDeduplication(unittest.TestCase):
    """Test video/audio placeholder deduplication in formatter."""

    def test_multiple_video_placeholders_deduplicated(self):
        """Should show only one video note for multiple video elements."""
        html = '''
        <div class="video-player">Video 1</div>
        <div class="video-container">Video 2</div>
        <div class="video-wrapper">Video 3</div>
        <div class="video-embed">Video 4</div>
        <div class="video-box">Video 5</div>
        '''

        markdown = html_to_markdown(html, 'https://example.com')

        # Should have exactly one video note
        video_note_count = markdown.count('Video content available')
        self.assertEqual(
            video_note_count, 1,
            f"Should have 1 video note, found {video_note_count}"
        )

    def test_multiple_audio_placeholders_deduplicated(self):
        """Should show only one audio note for multiple audio elements."""
        html = '''
        <div class="audio-player">Audio 1</div>
        <div class="audio-container">Audio 2</div>
        <div class="audio-wrapper">Audio 3</div>
        '''

        markdown = html_to_markdown(html, 'https://example.com')

        # Should have exactly one audio note
        audio_note_count = markdown.count('Audio content available')
        self.assertEqual(
            audio_note_count, 1,
            f"Should have 1 audio note, found {audio_note_count}"
        )

    def test_mixed_media_placeholders_handled(self):
        """Should show one note each for video and audio."""
        html = '''
        <div class="video-player">Video 1</div>
        <div class="audio-player">Audio 1</div>
        <div class="video-container">Video 2</div>
        <div class="audio-wrapper">Audio 2</div>
        '''

        markdown = html_to_markdown(html, 'https://example.com')

        video_note_count = markdown.count('Video content available')
        audio_note_count = markdown.count('Audio content available')

        self.assertEqual(video_note_count, 1, "Should have 1 video note")
        self.assertEqual(audio_note_count, 1, "Should have 1 audio note")

    def test_no_emoji_in_placeholders(self):
        """Should not include emoji in placeholder text."""
        html = '''
        <div class="video-player">Video content</div>
        <div class="audio-player">Audio content</div>
        '''

        markdown = html_to_markdown(html, 'https://example.com')

        # Check for specific emoji that were previously used
        self.assertNotIn('📹', markdown, "Should not contain video emoji")
        self.assertNotIn('🎧', markdown, "Should not contain audio emoji")

    def test_single_video_placeholder_unchanged(self):
        """Should handle single video placeholder correctly."""
        html = '<div class="video-player">Video content</div>'

        markdown = html_to_markdown(html, 'https://example.com')

        video_note_count = markdown.count('Video content available')
        self.assertEqual(video_note_count, 1, "Should have 1 video note")

    def test_no_media_no_placeholders(self):
        """Should not add placeholders when no media elements present."""
        html = '<p>Regular text content</p><div>More content</div>'

        markdown = html_to_markdown(html, 'https://example.com')

        self.assertNotIn('Video content available', markdown)
        self.assertNotIn('Audio content available', markdown)

    def test_content_preserved_with_media(self):
        """Should preserve regular content along with media placeholder."""
        html = '''
        <p>Introduction text</p>
        <div class="video-player">Video</div>
        <p>Conclusion text</p>
        '''

        markdown = html_to_markdown(html, 'https://example.com')

        self.assertIn('Introduction text', markdown)
        self.assertIn('Conclusion text', markdown)
        self.assertEqual(
            markdown.count('Video content available'), 1,
            "Should have exactly 1 video note"
        )

    def test_video_placeholder_class_variations(self):
        """Should detect video placeholders with various class naming."""
        test_cases = [
            '<div class="video">Content</div>',
            '<div class="VIDEO_PLAYER">Content</div>',
            '<span class="embedded-video">Content</span>',
            '<div class="video-content">Content</div>',
        ]

        for html in test_cases:
            with self.subTest(html=html):
                markdown = html_to_markdown(html, 'https://example.com')
                self.assertIn(
                    'Video content available', markdown,
                    f"Should detect video in: {html}"
                )

    def test_audio_placeholder_class_variations(self):
        """Should detect audio placeholders with various class naming."""
        test_cases = [
            '<div class="audio">Content</div>',
            '<div class="AUDIO_PLAYER">Content</div>',
            '<span class="embedded-audio">Content</span>',
            '<div class="audio-content">Content</div>',
        ]

        for html in test_cases:
            with self.subTest(html=html):
                markdown = html_to_markdown(html, 'https://example.com')
                self.assertIn(
                    'Audio content available', markdown,
                    f"Should detect audio in: {html}"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
