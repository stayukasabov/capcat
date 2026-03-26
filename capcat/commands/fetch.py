"""Batch fetch command — processes multiple sources via the unified processor."""
from __future__ import annotations

import argparse
import os
from typing import Dict, List, Tuple

from capcat.core.shutdown import GracefulShutdown
from capcat.core.unified_source_processor import (
    UnifiedSourceProcessor,
    process_source_articles,
)
from capcat.core.source_system.base_source import SourceError


def process_sources(
    sources: List[str],
    args: argparse.Namespace,
    config: object,
    logger: object,
    generate_html: bool = False,
    output_dir: str = ".",
) -> Dict[str, object]:
    """Process multiple sources using the unified processor.

    Args:
        sources: List of source identifiers to process (e.g., 'hn', 'bbc').
        args: Parsed arguments with count, quiet, verbose, media attributes.
        config: Configuration object with system settings.
        logger: Logger instance for output.
        generate_html: Whether to generate HTML output after processing.
        output_dir: Output directory path for saved articles.

    Returns:
        Dict with keys 'successful' (list), 'failed' (list of tuples), 'total'.
    """
    UnifiedSourceProcessor.clear_url_cache()
    logger.debug("Cleared URL deduplication cache for new session")

    successful_sources: List[str] = []
    failed_sources: List[Tuple[str, str]] = []
    is_batch = len(sources) > 1
    completed = 0

    with GracefulShutdown() as shutdown:
        for source in sources:
            if shutdown.should_shutdown():
                break
            try:
                logger.info(f"Processing {source} articles...")
                process_source_articles(
                    source_name=source,
                    count=args.count,
                    output_dir=output_dir,
                    quiet=getattr(args, "quiet", False),
                    verbose=getattr(args, "verbose", False),
                    download_files=getattr(args, "media", False),
                    batch_mode=is_batch,
                    generate_html=generate_html,
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

        if shutdown.should_shutdown():
            print(f"\nCancelled — fetched {completed} of {len(sources)} sources.")
            os._exit(130)

    return {
        "successful": successful_sources,
        "failed": failed_sources,
        "total": len(sources),
    }
