"""Batch fetch command - processes multiple sources via the unified processor."""
from __future__ import annotations

import argparse
import os
import time
from typing import Dict, List, Tuple

from capcat.core.shutdown import GracefulShutdown
from capcat.core.unified_source_processor import process_source_articles
from capcat.core.source_system.base_source import SourceError
from capcat.core import json_events


def process_sources(
    sources: List[str],
    args: argparse.Namespace,
    config: object,
    logger: object,
    generate_html: bool = False,
    output_dir: str = ".",
    command: str = "fetch",
) -> Dict[str, object]:
    """Process multiple sources using the unified processor.

    Args:
        sources: List of source identifiers to process (e.g., 'hn', 'bbc').
        args: Parsed arguments with count, quiet, verbose, media attributes.
        config: Configuration object with system settings.
        logger: Logger instance for output.
        generate_html: Whether to generate HTML output after processing.
        output_dir: Output directory path for saved articles.
        command: The CLI command name ("fetch" or "bundle"), included in
            the hidden --json run_start event.

    Returns:
        Dict with keys 'successful' (list), 'failed' (list of tuples), 'total'.
    """
    successful_sources: List[str] = []
    failed_sources: List[Tuple[str, str]] = []
    is_batch = len(sources) > 1
    completed = 0
    total_fetched = 0
    total_errors = 0

    start_time = time.time()
    json_events.emit(
        "run_start", command=command, sources=sources,
        count=getattr(args, "count", None),
    )

    with GracefulShutdown() as shutdown:
        for source in sources:
            if shutdown.should_shutdown():
                break
            json_events.emit("source_start", source=source)
            try:
                logger.info(f"Processing {source} articles...")
                process_source_articles(
                    source_name=source,
                    count=args.count,
                    output_dir=output_dir,
                    quiet=getattr(args, "quiet", False),
                    verbose=getattr(args, "verbose", False),
                    download_files=getattr(args, "media", False),
                    download_pdfs=getattr(args, "pdfs", False),
                    batch_mode=is_batch,
                    generate_html=generate_html,
                    force_no_pdfs=getattr(args, "no_pdfs", False),
                )
                successful_sources.append(source)
                completed += 1
                logger.info(f"Successfully processed {source}")

            except SourceError:
                failed_sources.append((source, "Source unavailable"))
                if is_batch:
                    logger.info("Continuing with remaining sources...")
            except Exception as exc:
                logger.error(f"Error processing {source}: {exc}")
                failed_sources.append((source, str(exc)))
                if is_batch:
                    logger.warning(
                        f"Skipping {source} and continuing with remaining sources"
                    )

            fetched, errors = json_events.pop_article_counts()
            total_fetched += fetched
            total_errors += errors
            json_events.emit(
                "source_complete", source=source, fetched=fetched, errors=errors
            )

        if shutdown.should_shutdown():
            print(f"\nCancelled - fetched {completed} of {len(sources)} sources.")
            os._exit(130)

    json_events.emit(
        "run_complete",
        total_fetched=total_fetched,
        total_errors=total_errors,
        output_dir=output_dir,
        html_path=json_events.pop_html_path(),
        duration_seconds=round(time.time() - start_time, 1),
    )

    return {
        "successful": successful_sources,
        "failed": failed_sources,
        "total": len(sources),
    }
