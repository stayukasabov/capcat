"""Regression: images inside <button> elements must be preserved during button removal.

Many sites wrap content images in <button> elements for lightbox/modal functionality.
The current html_to_markdown removes ALL buttons, destroying content images.

Fix: before removing buttons, extract any images they contain and preserve them
at the same document position.
"""
from __future__ import annotations

from bs4 import BeautifulSoup

import pytest


def test_button_images_preserved_during_removal():
    """Images inside buttons should be extracted before buttons are removed."""
    from capcat.core.formatter import _preserve_button_images

    html = '''
    <div>
        <p>Before image</p>
        <button aria-label="View image" class="lightbox">
            <img src="/uploads/diagram.png" alt="Important diagram"/>
        </button>
        <p>After image</p>
    </div>
    '''

    soup = BeautifulSoup(html, 'html.parser')
    _preserve_button_images(soup)

    # Button should be gone
    assert len(soup.find_all('button')) == 0

    # Image should remain in same position
    images = soup.find_all('img')
    assert len(images) == 1
    assert images[0]['src'] == '/uploads/diagram.png'

    # Image should be between the paragraphs
    content = str(soup)
    assert 'Before image' in content
    assert 'After image' in content
    before_pos = content.find('Before image')
    img_pos = content.find('<img')
    after_pos = content.find('After image')
    assert before_pos < img_pos < after_pos


def test_multiple_images_in_button():
    """Multiple images in one button should all be preserved."""
    from capcat.core.formatter import _preserve_button_images

    html = '''
    <div>
        <button class="gallery">
            <img src="/uploads/photo1.jpg" alt="Photo 1"/>
            <img src="/uploads/photo2.jpg" alt="Photo 2"/>
        </button>
    </div>
    '''

    soup = BeautifulSoup(html, 'html.parser')
    _preserve_button_images(soup)

    assert len(soup.find_all('button')) == 0
    images = soup.find_all('img')
    assert len(images) == 2
    assert images[0]['src'] == '/uploads/photo1.jpg'
    assert images[1]['src'] == '/uploads/photo2.jpg'


def test_buttons_without_images_removed():
    """Buttons with no images should be removed completely."""
    from capcat.core.formatter import _preserve_button_images

    html = '''
    <div>
        <button onclick="doSomething()">Click me</button>
        <button><span>Text only</span></button>
    </div>
    '''

    soup = BeautifulSoup(html, 'html.parser')
    _preserve_button_images(soup)

    assert len(soup.find_all('button')) == 0
    assert len(soup.find_all('img')) == 0


def test_nested_button_content_preserved():
    """Complex button content with images should preserve only the images."""
    from capcat.core.formatter import _preserve_button_images

    html = '''
    <div>
        <button class="complex">
            <div class="wrapper">
                <img src="/uploads/icon.png" alt="Icon"/>
                <span class="label">View full size</span>
            </div>
        </button>
    </div>
    '''

    soup = BeautifulSoup(html, 'html.parser')
    _preserve_button_images(soup)

    assert len(soup.find_all('button')) == 0
    images = soup.find_all('img')
    assert len(images) == 1
    assert images[0]['src'] == '/uploads/icon.png'

    # Wrapper text should be gone
    assert 'View full size' not in str(soup)
    assert 'wrapper' not in str(soup)