#!/usr/bin/env python3
"""
Simple test script to validate the refactored components of Capcat.
"""

# First activate the virtual environment if available
import os
import sys

# Check for virtual environment and activate it if needed
venv_dir = os.path.join(os.path.dirname(__file__), "venv")
if os.path.exists(venv_dir):
    # Add virtual environment packages to path
    venv_site_packages = os.path.join(venv_dir, "lib", "python3.11", "site-packages")
    if os.path.exists(venv_site_packages):
        sys.path.insert(0, venv_site_packages)
    
    # For newer Python versions, check other possible paths
    import glob
    venv_lib_dirs = glob.glob(os.path.join(venv_dir, "lib", "python*", "site-packages"))
    for lib_dir in venv_lib_dirs:
        if os.path.exists(lib_dir):
            sys.path.insert(0, lib_dir)
            break

import os
import tempfile
from unittest.mock import Mock, patch

import requests
from bs4 import BeautifulSoup

# Import the refactored components
from core.media_processor import MediaProcessor
from core.storage_manager import StorageManager


def test_media_processor():
    """Test the MediaProcessor component."""
    print("Testing MediaProcessor...")
    
    session = Mock(spec=requests.Session)
    processor = MediaProcessor(session, download_files=True)
    
    # Test 1: Extract media links
    html_content = '''
    <html>
        <body>
            <img src="https://example.com/image.jpg" alt="Test Image">
            <img src="/relative.jpg" alt="Relative Image">
            <a href="https://example.com/doc.pdf">PDF</a>
            <video><source src="https://example.com/video.mp4"></video>
            <audio><source src="https://example.com/audio.mp3"></audio>
        </body>
    </html>
    '''
    soup = BeautifulSoup(html_content, 'html.parser')
    base_url = "https://example.com"
    
    links = processor._extract_media_links(soup, base_url)
    
    # Should find at least 2 images, 1 document, 1 video, 1 audio
    assert len(links) >= 5, f"Expected at least 5 links, got {len(links)}"
    
    link_types = [link[0] for link in links]
    assert link_types.count('image') >= 2, f"Expected at least 2 images, got {link_types.count('image')}"
    assert 'document' in link_types, f"Expected document in link types, got {link_types}"
    assert 'video' in link_types, f"Expected video in link types, got {link_types}"
    assert 'audio' in link_types, f"Expected audio in link types, got {link_types}"
    
    print("  ✓ Media link extraction test passed")
    
    # Test 2: Filter media links
    all_links = [
        ('image', 'https://example.com/image.jpg', 'Image'),
        ('document', 'https://example.com/doc.pdf', 'PDF'),
        ('image', 'https://example.com/icon.png', 'Icon'),  # This might be filtered
    ]
    
    # With download_files=True, should include documents
    filtered = processor._filter_media_links(all_links)
    assert len(filtered) >= 2, f"With download_files=True, expected at least 2 links, got {len(filtered)}"
    
    # With download_files=False, should still include images
    processor_no_files = MediaProcessor(session, download_files=False)
    filtered_no_files = processor_no_files._filter_media_links(all_links)
    
    # Should include images
    filtered_types = [link[0] for link in filtered_no_files]
    # Even with download_files=False, images should be included
    image_count = sum(1 for t in filtered_types if t == 'image')
    assert image_count >= 2, f"Expected at least 2 images even with download_files=False, got {image_count}"
    
    print("  ✓ Media link filtering test passed")


def test_storage_manager():
    """Test the StorageManager component."""
    print("Testing StorageManager...")
    
    manager = StorageManager()
    
    # Test 1: Create article folder
    with tempfile.TemporaryDirectory() as base_dir:
        title = "Test Article Title"
        folder_path = manager.create_article_folder(base_dir, title)
        
        # Verify folder was created
        assert os.path.exists(folder_path), f"Expected folder to be created at {folder_path}"
        assert title in folder_path, f"Expected title '{title}' in folder path '{folder_path}'"
        
        # Verify images folder was created
        images_path = os.path.join(folder_path, "images")
        assert os.path.exists(images_path), f"Expected images folder at {images_path}"
    
    print("  ✓ Article folder creation test passed")
    
    # Test 2: Save article content
    with tempfile.TemporaryDirectory() as temp_dir:
        # First create an article folder
        folder_path = manager.create_article_folder(temp_dir, "Test Article")
        
        content = "# Test Article\n\nThis is test content."
        file_path = manager.save_article_content(folder_path, content)
        
        # Verify file was created and contains content
        assert os.path.exists(file_path), f"Expected file to be created at {file_path}"
        assert file_path == os.path.join(folder_path, "article.md"), f"Expected article.md file path"
        
        with open(file_path, 'r') as f:
            saved_content = f.read()
        
        assert saved_content == content, f"Content mismatch: expected '{content}', got '{saved_content}'"
    
    print("  ✓ Save article content test passed")
    
    # Test 3: Cleanup empty images folder
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an article folder with empty images directory
        folder_path = manager.create_article_folder(temp_dir, "Test Article")
        images_path = os.path.join(folder_path, "images")
        
        # Verify images folder exists
        assert os.path.exists(images_path), f"Expected images folder to exist at {images_path}"
        
        # Clean up the empty images folder
        manager.cleanup_empty_images_folder(folder_path)
        
        # Verify images folder is gone
        assert not os.path.exists(images_path), f"Expected images folder to be removed, but still exists at {images_path}"
    
    print("  ✓ Cleanup empty images folder test passed")
    
    # Test 4: Don't cleanup non-empty images folder
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an article folder with images directory
        folder_path = manager.create_article_folder(temp_dir, "Test Article")
        images_path = os.path.join(folder_path, "images")
        
        # Create a file in the images folder
        test_file = os.path.join(images_path, "test.jpg")
        with open(test_file, 'w') as f:
            f.write("dummy image data")
        
        # Verify images folder exists
        assert os.path.exists(images_path), f"Expected images folder to exist at {images_path}"
        
        # Clean up (should not remove the images folder)
        manager.cleanup_empty_images_folder(folder_path)
        
        # Verify images folder still exists
        assert os.path.exists(images_path), f"Expected non-empty images folder to still exist at {images_path}"
    
    print("  ✓ Don't cleanup non-empty images folder test passed")


def main():
    """Run all tests."""
    print("Running refactored components tests...\n")
    
    try:
        test_media_processor()
        test_storage_manager()
        
        print("\n✓ All tests passed!")
        return True
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)