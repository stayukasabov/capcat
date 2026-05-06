#!/usr/bin/env python3
"""
Hacker News source implementation using the official Firebase API.
Uses hacker-news.firebaseio.com/v0/ for article discovery and comment fetching.
"""

import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Tuple

from capcat.core.article_fetcher import NewsSourceArticleFetcher
from capcat.core.ethical_scraping import get_ethical_manager
from capcat.core.storage_manager import comments_md_filename
from capcat.core.source_system.base_source import (
    Article,
    ArticleDiscoveryError,
    BaseSource,
    ContentFetchError,
)


class HnSource(BaseSource):
    """
    Hacker News source implementation using the official Firebase API.

    All article discovery and comment fetching uses the HN Firebase API
    at hacker-news.firebaseio.com/v0/. No HTML is scraped from
    news.ycombinator.com for discovery or comments.
    """

    _HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
    _MAX_LINKS_PER_COMMENT = 5
    _MAX_COMMENTS_PER_ARTICLE = 200
    _MAX_COMMENT_DEPTH = 4
    _CONCURRENT_WORKERS = 5
    _hn_compliance_message_shown = False

    @property
    def source_type(self) -> str:
        return "custom"

    def discover_articles(self, count: int) -> List[Article]:
        """
        Discover articles from Hacker News via the official Firebase API.

        Fetches /v0/topstories.json for story IDs, then fetches metadata
        for each story sequentially with rate limiting.
        """
        try:
            self.logger.info("Fetching top stories from official Hacker News API")

            manager = get_ethical_manager()

            story_ids = manager.request_hn_api(
                self.session,
                f"{self._HN_API_BASE}/topstories.json",
                timeout=self.config.timeout,
            )

            if not story_ids:
                raise ArticleDiscoveryError(
                    "Failed to fetch top stories from HN API", self.config.name
                )

            articles = []
            first_failed = False

            for story_id in story_ids:
                if len(articles) >= count:
                    break

                item = manager.request_hn_api(
                    self.session,
                    f"{self._HN_API_BASE}/item/{story_id}.json",
                    timeout=self.config.timeout,
                )

                if item is None:
                    if not articles and not first_failed:
                        first_failed = True
                        continue
                    elif not articles and first_failed:
                        raise ArticleDiscoveryError(
                            "Network appears down, aborting HN discovery",
                            self.config.name,
                        )
                    self.logger.warning(
                        f"Skipping story {story_id}: API request failed"
                    )
                    continue

                if item.get("type") != "story":
                    continue

                title = item.get("title", "Untitled Article")
                url = item.get("url") or (
                    f"https://news.ycombinator.com/item?id={story_id}"
                )
                comment_url = f"https://news.ycombinator.com/item?id={story_id}"
                comment_ids = item.get("kids")

                article = Article(
                    title=title,
                    url=url,
                    comment_url=comment_url,
                    comment_ids=comment_ids,
                    hn_item_id=story_id,
                )
                articles.append(article)

            self.logger.info(
                f"Successfully discovered {len(articles)} articles "
                f"for {self.config.name}"
            )

            if not HnSource._hn_compliance_message_shown:
                print(
                    "\nUsing official Hacker News API with rate-limited "
                    "requests to comply with site guidelines. "
                    "This may take a few minutes.\n",
                    flush=True,
                )
                HnSource._hn_compliance_message_shown = True

            return articles

        except ArticleDiscoveryError:
            raise
        except Exception as e:
            raise ArticleDiscoveryError(
                f"Failed to discover articles: {e}", self.config.name
            )

    def fetch_article_content(
        self, article: Article, output_dir: str, progress_callback=None,
        download_files: bool = False, download_pdfs: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        Fetch article content from Hacker News.
        Optimized to prevent conversion hangs.
        """
        try:
            self.logger.debug(f"Fetching content for article: {article.title}")

            # Skip HN discussion pages - only process external articles
            if article.url.startswith("https://news.ycombinator.com/item?id="):
                self.logger.debug(
                    f"Skipping HN discussion page: {article.title}"
                )
                return False, None

            fetcher_config = {
                "name": self.config.display_name,
                "content_selectors": [
                    "article",
                    ".post-content",
                    ".article-content",
                    ".content",
                    "main",
                    ".main-content",
                    ".entry-content",
                    ".blog-post",
                    ".article-body",
                    "body",
                ],
                "skip_patterns": [
                    "/news",
                    "/newest",
                    "/threads",
                    "/front",
                    "/user?id=",
                    "hide?id=",
                    "news.ycombinator.com/news",
                    "news.ycombinator.com/newest",
                    "news.ycombinator.com/item",
                ],
            }

            fetcher = NewsSourceArticleFetcher(
                fetcher_config, self.session,
                download_files=download_files,
                download_pdfs=download_pdfs,
            )

            original_timeout = (
                self.session.timeout
                if hasattr(self.session, "timeout")
                else None
            )
            self.session.timeout = 15

            try:
                success, title, folder_path = fetcher.fetch_article_content(
                    title=article.title,
                    url=article.url,
                    index=0,
                    base_folder=output_dir,
                    progress_callback=progress_callback,
                )
            finally:
                if original_timeout is not None:
                    self.session.timeout = original_timeout
                elif hasattr(self.session, "timeout"):
                    delattr(self.session, "timeout")

            if success:
                return True, folder_path
            else:
                return False, None

        except Exception as e:
            raise ContentFetchError(
                f"Failed to fetch content for {article.url}: {e}",
                self.config.name,
            )

    def _validate_custom_config(self) -> List[str]:
        """Validate Hacker News-specific configuration."""
        return []

    def _should_skip_custom(self, url: str, title: str = "") -> bool:
        """Custom skip logic for Hacker News."""
        return False

    def fetch_comments(
        self,
        comment_url: str,
        article_title: str,
        article_folder_path: str,
        html_mode: bool = False,
        comment_ids: Optional[List[int]] = None,
    ) -> bool:
        """
        Fetch and save HN comments via the official Firebase API.

        Recursively fetches each comment item from /v0/item/{id}.json,
        building a flat list with depth tracking. Passes the result to
        StreamlinedCommentProcessor for rendering.

        Args:
            comment_url: URL of the comments page (used in output header)
            article_title: Title of the article for logging
            article_folder_path: Folder path for saving the output file
            html_mode: If True, generate HTML; if False, generate markdown
            comment_ids: List of top-level comment IDs from the story item

        Returns:
            True if comments were successfully saved, False otherwise
        """
        if not comment_url:
            self.logger.debug(f"No comment URL available for: {article_title}")
            return False

        if not article_folder_path or not os.path.exists(article_folder_path):
            self.logger.error(
                f"Invalid article folder path: {article_folder_path}"
            )
            return False

        if not comment_ids:
            self.logger.debug(f"No comment IDs available for: {article_title}")
            comment_ids = []

        try:
            manager = get_ethical_manager()

            comments = self._fetch_comment_tree(manager, comment_ids, depth=0)

            self.logger.debug(
                f"Fetched {len(comments)} comments for: {article_title}"
            )

            from capcat.core.streamlined_comment_processor import (
                create_optimized_comment_processor,
            )

            processor = create_optimized_comment_processor(max_comments=None)

            if html_mode:
                content = processor.generate_inline_comments_html(
                    comments, article_title, comment_url,
                    link_text="view on HN",
                )
                filename = os.path.join(
                    article_folder_path, "html", "comments.html"
                )
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            else:
                content = processor.generate_inline_comments_markdown(
                    comments, article_title, comment_url,
                    article_folder_path, link_text="view on HN",
                )
                filename = os.path.join(
                    article_folder_path, comments_md_filename(article_title)
                )

            metrics = processor.get_performance_metrics()
            self.logger.info(
                f"Processed {metrics['comments_processed']} comments "
                f"with {metrics['links_processed']} links "
                f"for: {article_title}"
            )

            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)

                format_type = "HTML" if html_mode else "markdown"
                self.logger.info(
                    f"Successfully saved {len(comments)} comments "
                    f"as {format_type} for: {article_title}"
                )
                return True

            except (PermissionError, OSError, UnicodeEncodeError) as file_error:
                self.logger.error(
                    f"File I/O error writing comments "
                    f"for {article_title}: {file_error}"
                )
                return False

        except Exception as processing_error:
            self.logger.error(
                f"Comment processing error "
                f"for {comment_url}: {processing_error}"
            )
            return False

    def _fetch_comment_tree(
        self,
        manager,
        comment_ids: List[int],
        depth: int,
    ) -> List[dict]:
        """
        Fetch comments from the HN Firebase API using concurrent workers.

        Top-level comments are fetched in parallel using a thread pool.
        Children are fetched recursively within each worker thread.
        Display order is preserved by processing results in submission order.

        Args:
            manager: EthicalScrapingManager instance
            comment_ids: List of comment IDs to fetch
            depth: Current nesting depth (0 = top-level)

        Returns:
            Flat list of comment dicts in display order
        """
        counter = {"n": 0}
        lock = threading.Lock()

        def _fetch_single(cid, d):
            """Fetch one comment and its children. Thread-safe."""
            with lock:
                if counter["n"] >= self._MAX_COMMENTS_PER_ARTICLE:
                    return []

            if d > self._MAX_COMMENT_DEPTH:
                return []

            item = manager.request_hn_api(
                self.session,
                f"{self._HN_API_BASE}/item/{cid}.json",
                timeout=self.config.timeout,
                skip_rate_limit=True,
            )
            if item is None:
                return []

            with lock:
                if counter["n"] >= self._MAX_COMMENTS_PER_ARTICLE:
                    return []
                counter["n"] += 1

            result = []
            is_deleted = item.get("deleted", False)
            is_dead = item.get("dead", False)

            if not is_deleted and not is_dead:
                text = self._clean_api_comment_html(item.get("text", ""))
                if text:
                    result.append({
                        "id": str(cid),
                        "user": "Anonymous",
                        "user_link": (
                            f"https://news.ycombinator.com/item?id={cid}"
                        ),
                        "text": text,
                        "level": d,
                    })

            # Recurse into children sequentially within this thread
            kids = item.get("kids", [])
            for kid_id in kids:
                with lock:
                    if counter["n"] >= self._MAX_COMMENTS_PER_ARTICLE:
                        break
                result.extend(_fetch_single(kid_id, d + 1))

            return result

        # Dispatch top-level comment IDs to the thread pool
        comments = []
        with ThreadPoolExecutor(
            max_workers=self._CONCURRENT_WORKERS,
        ) as pool:
            futures = []
            for cid in comment_ids:
                with lock:
                    if counter["n"] >= self._MAX_COMMENTS_PER_ARTICLE:
                        break
                futures.append(pool.submit(_fetch_single, cid, depth))

            # Collect in submission order to preserve display order
            for future in futures:
                result = future.result()
                if result:
                    comments.extend(result)

        return comments

    def _clean_api_comment_html(self, html: str) -> str:
        """
        Convert HN API comment HTML to clean text with markdown links.

        The Firebase API returns comment text as HTML-encoded content
        (e.g. <p>tags, <a> links, <code> blocks). This method converts
        it to plain text with markdown-style links, matching the output
        format of the former HTML scraper.

        Args:
            html: HTML string from the API's text field

        Returns:
            Cleaned text with markdown links
        """
        if not html:
            return ""

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # Remove reply/control links
        for unwanted in soup.find_all(
            "a", string=re.compile(r"reply|permalink|parent|flag", re.I)
        ):
            unwanted.decompose()

        # Convert remaining links to markdown (up to limit)
        links_processed = 0
        for link in soup.find_all("a", href=True):
            if links_processed >= self._MAX_LINKS_PER_COMMENT:
                link.decompose()
                continue

            href = link.get("href", "")
            link_text = link.get_text().strip()

            if not href or not link_text:
                link.decompose()
                continue

            if href.startswith("/"):
                href = f"https://news.ycombinator.com{href}"
            elif not href.startswith(("http://", "https://")):
                href = f"https://{href}"

            link.replace_with(f"[{link_text}]({href})")
            links_processed += 1

        # Extract text, split by paragraphs
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text().strip()
            if text:
                paragraphs.append(text)

        if paragraphs:
            return "\n\n".join(paragraphs)

        # Fallback: no <p> tags, just get all text
        text = soup.get_text().strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n\n".join(lines)
