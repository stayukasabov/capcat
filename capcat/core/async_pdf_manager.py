#!/usr/bin/env python3
"""
Asynchronous PDF download manager to prevent thread pool exhaustion.
Handles PDF downloads separately from article processing.
"""

import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests

from .logging_config import get_logger
from .config import PdfConfig


def pdf_exceeds_size_limit(url: str, session, max_bytes: int) -> bool:
    """Return True if HEAD response reports Content-Length > max_bytes."""
    try:
        head = session.head(url, timeout=10, allow_redirects=True)
        content_length = head.headers.get("Content-Length")
        if content_length and int(content_length) > max_bytes:
            return True
    except Exception:
        pass
    return False


class AsyncPDFManager:
    """
    Manages asynchronous PDF downloads to prevent blocking article processing threads.

    Instead of downloading PDFs synchronously during article processing, this manager:
    1. Collects PDF links during article processing
    2. Downloads PDFs asynchronously in background
    3. Updates markdown files once downloads complete
    """

    def __init__(self, max_workers: int = 4, pdf_config: PdfConfig = None):
        self.max_workers = max_workers
        self.pdf_config = pdf_config if pdf_config is not None else PdfConfig()
        self._check_session = requests.Session()
        self.logger = get_logger(self.__class__.__name__)

        # Background download management
        self.download_queue: Queue = Queue()
        self.active_downloads: Dict[str, threading.Event] = {}
        self.completed_downloads: Dict[str, str] = {}  # url -> local_path
        self.failed_downloads: Set[str] = set()

        # Background thread management
        self.executor: Optional[ThreadPoolExecutor] = None
        self.shutdown_event = threading.Event()
        self.worker_thread: Optional[threading.Thread] = None

        self._lock = threading.Lock()
        self._queued_by_folder: Dict[str, List[str]] = {}

    def start(self):
        """Start the background PDF download service."""
        if self.worker_thread is not None:
            return  # Already started

        self.shutdown_event.clear()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

        self.logger.info(f"Started async PDF manager with {self.max_workers} workers")

    def stop(self):
        """Stop the background PDF download service."""
        if self.worker_thread is None:
            return

        self.shutdown_event.set()

        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None

        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
            self.worker_thread = None

        self.logger.info("Stopped async PDF manager")

    def extract_and_queue_pdf_links(
        self, markdown_content: str, article_folder_path: str
    ) -> Tuple[str, int]:
        """
        Extract PDF links from markdown and queue them for async download.
        Returns updated markdown with placeholder links and count of PDFs queued.
        """
        # Match [text](url) where url looks like a PDF
        link_pattern = re.compile(r'\[([^\]]*)\]\((https?://[^)]+)\)')
        seen_urls = set()
        queued_count = 0

        def is_pdf_url(url: str) -> bool:
            path = urlparse(url).path.lower()
            return path.endswith(".pdf") or "pdf" in path

        def replace_link(match):
            nonlocal queued_count
            text, link_url = match.group(1), match.group(2)

            if link_url in seen_urls or not is_pdf_url(link_url):
                return match.group(0)  # Keep original

            seen_urls.add(link_url)

            if queued_count >= self.pdf_config.max_pdf_per_article:
                return match.group(0)  # Cap reached, keep original link unchanged

            # Queue for background download
            download_info = {
                'url': link_url,
                'folder_path': article_folder_path,
                'link_text': text,
                'article_markdown_path': None,  # Will be set later
            }

            with self._lock:
                # Create event for tracking completion
                self.active_downloads[link_url] = threading.Event()

            self.download_queue.put(download_info)
            queued_count += 1

            # Return placeholder for now - will be updated when download completes
            placeholder_path = f"files/downloading_{os.path.basename(urlparse(link_url).path)}"
            self.logger.debug(f"Queued PDF download: {link_url} -> {placeholder_path}")

            return f"[{text}]({placeholder_path})"

        updated_content = link_pattern.sub(replace_link, markdown_content)

        if queued_count > 0:
            self.logger.info(f"Queued {queued_count} PDF downloads for background processing")
            with self._lock:
                self._queued_by_folder[article_folder_path] = list(seen_urls)

        return updated_content, queued_count

    def get_queued_urls_for_folder(self, folder_path: str) -> List[str]:
        """Return and remove the queued PDF URLs for a given article folder."""
        with self._lock:
            return self._queued_by_folder.pop(folder_path, [])

    def update_article_with_completed_downloads(self, markdown_file_path: str):
        """
        Update an article's markdown file with completed PDF downloads.
        This is called after the article is saved to update PDF links.
        """
        if not os.path.exists(markdown_file_path):
            return

        try:
            with open(markdown_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find placeholder links and update with actual downloads
            updated = False
            link_pattern = re.compile(r'\[([^\]]*)\]\(files/downloading_([^)]+)\)')

            def replace_placeholder(match):
                nonlocal updated
                text, filename = match.group(1), match.group(2)

                # Find corresponding completed download
                for url, local_path in self.completed_downloads.items():
                    if os.path.basename(urlparse(url).path) == filename:
                        updated = True
                        relative = os.path.relpath(
                            local_path, os.path.dirname(markdown_file_path)
                        )
                        return f"[{text}]({relative})"

                # If not completed yet, check if it failed
                for failed_url in self.failed_downloads:
                    if os.path.basename(urlparse(failed_url).path) == filename:
                        # Restore original URL since download failed
                        updated = True
                        return f"[{text}]({failed_url})"

                return match.group(0)  # Keep placeholder

            updated_content = link_pattern.sub(replace_placeholder, content)

            if updated:
                with open(markdown_file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                self.logger.debug(f"Updated PDF links in {markdown_file_path}")

        except Exception as e:
            self.logger.warning(f"Failed to update PDF links in {markdown_file_path}: {e}")

    def _worker_loop(self):
        """Background worker loop for processing PDF download queue."""
        self.logger.debug("PDF download worker loop started")

        try:
            while not self.shutdown_event.is_set():
                try:
                    # Get download task with timeout
                    download_info = self.download_queue.get(timeout=1.0)
                except Exception:
                    continue  # Timeout or shutdown

                if self.shutdown_event.is_set():
                    break

                # Submit download to thread pool
                if self.executor:
                    self.executor.submit(self._download_pdf, download_info)

        except Exception as e:
            self.logger.error(f"PDF download worker loop error: {e}")
        finally:
            self.logger.debug("PDF download worker loop stopped")

    def _download_pdf(self, download_info: dict):
        """Download a single PDF file."""
        url = download_info['url']
        folder_path = download_info['folder_path']

        try:
            self.logger.debug(f"Starting PDF download: {url}")

            if pdf_exceeds_size_limit(url, self._check_session, self.pdf_config.max_pdf_size_bytes):
                self.logger.warning("Skipping PDF (too large): %s", url)
                with self._lock:
                    self.failed_downloads.add(url)
                return

            # Import here to avoid circular imports
            from .downloader import download_file

            local_path = download_file(url, folder_path, "document", True)

            if local_path:
                with self._lock:
                    self.completed_downloads[url] = local_path
                self.logger.debug(f"Completed PDF download: {url} -> {local_path}")
            else:
                with self._lock:
                    self.failed_downloads.add(url)
                self.logger.debug(f"Failed PDF download: {url}")

        except Exception as e:
            with self._lock:
                self.failed_downloads.add(url)
            self.logger.debug(f"PDF download failed {url}: {e}")

        finally:
            # Signal completion
            with self._lock:
                if url in self.active_downloads:
                    self.active_downloads[url].set()
                    del self.active_downloads[url]

    def wait_for_downloads(self, urls: List[str], timeout: float = 30.0) -> bool:
        """
        Wait for specific PDF downloads to complete.
        Returns True if all completed, False if timeout.
        """
        events = []
        with self._lock:
            events = [self.active_downloads.get(url) for url in urls if url in self.active_downloads]

        if not events:
            return True  # No active downloads

        # Wait for all events
        start_time = time.time()
        for event in events:
            if event:
                remaining_time = max(0.1, timeout - (time.time() - start_time))
                if not event.wait(timeout=remaining_time):
                    return False  # Timeout

        return True

    def get_status(self) -> Dict:
        """Get current status of the PDF download manager."""
        with self._lock:
            return {
                'queued': self.download_queue.qsize(),
                'active': len(self.active_downloads),
                'completed': len(self.completed_downloads),
                'failed': len(self.failed_downloads),
                'worker_alive': self.worker_thread.is_alive() if self.worker_thread else False,
            }


# Global instance for article fetchers to use
_global_pdf_manager: Optional[AsyncPDFManager] = None

def initialize_pdf_manager(pdf_config: "PdfConfig") -> AsyncPDFManager:
    """Return the running global AsyncPDFManager, creating and starting it if needed.

    Idempotent: subsequent calls with any config return the already-running instance.
    The manager is started on first creation; callers must not call .start() themselves.
    """
    global _global_pdf_manager
    if _global_pdf_manager is not None and _global_pdf_manager.worker_thread is not None:
        return _global_pdf_manager
    _global_pdf_manager = AsyncPDFManager(pdf_config=pdf_config)
    _global_pdf_manager.start()
    return _global_pdf_manager


def get_pdf_manager() -> AsyncPDFManager:
    """Get the global async PDF manager instance."""
    global _global_pdf_manager
    if _global_pdf_manager is None:
        _global_pdf_manager = AsyncPDFManager()
    return _global_pdf_manager

def shutdown_pdf_manager():
    """Shutdown the global PDF manager."""
    global _global_pdf_manager
    if _global_pdf_manager:
        _global_pdf_manager.stop()
        _global_pdf_manager = None