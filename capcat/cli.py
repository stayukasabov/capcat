"""CLI entry point for Capcat.

Routes subcommands to legacy capcat_legacy.py / cli.py logic via delegating
stubs.  Every heavy import lives inside the function body (lazy import) so
startup stays fast and circular-import-safe.
"""
from __future__ import annotations
import sys


# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

def _print_help() -> None:
    print(
        "Usage: capcat <command> [options]\n\n"
        "Commands:\n"
        "  init             Initialize a capcat project in the current directory\n"
        "  catch            Launch the interactive TUI\n"
        "  single <url>     Fetch a single article\n"
        "  fetch <sources>  Batch fetch from sources\n"
        "  bundle <name>    Fetch a bundle\n"
        "  list sources     List available sources\n"
        "  add-source       Add a new source\n"
        "  remove-source    Remove a source\n"
        "  generate-config  Generate a YAML config\n"
        "\nOptions:\n"
        "  -L <file>        Log output to file\n"
        "  -V, --verbose    Verbose output\n"
        "  -q, --quiet      Quiet output\n"
        "  --media          Download media files\n"
        "  --html           Generate HTML output\n"
        "  --update         Update existing articles\n"
        "  --help           Show this help\n"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point.  Routes to TUI or CLI dispatch."""
    args = sys.argv[1:]
    if args and args[0] == "catch":
        from capcat.tui import run
        run()
    else:
        _dispatch(args)


# ---------------------------------------------------------------------------
# Top-level dispatch
# ---------------------------------------------------------------------------

def _dispatch(args: list[str]) -> None:
    if not args or args[0] in ("-h", "--help"):
        _print_help()
        return

    # Handle -L <file> global option before command routing
    log_file = None
    if "-L" in args:
        idx = args.index("-L")
        if idx + 1 < len(args):
            log_file = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        else:
            print("capcat: -L requires a filename argument")
            raise SystemExit(1)

    command = args[0]
    rest = args[1:]

    if command == "init":
        _cmd_init(rest)
    elif command == "single":
        _cmd_single(rest, log_file=log_file)
    elif command == "fetch":
        _cmd_fetch(rest, log_file=log_file)
    elif command == "bundle":
        _cmd_bundle(rest, log_file=log_file)
    elif command == "list":
        _cmd_list(rest)
    elif command == "add-source":
        _cmd_add_source(rest)
    elif command == "remove-source":
        _cmd_remove_source(rest)
    elif command == "generate-config":
        _cmd_generate_config(rest)
    else:
        print(f"capcat: unknown command '{command}'. Run 'capcat --help'.")
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# Helpers: parse common flags out of a raw arg list
# ---------------------------------------------------------------------------

def _pop_flag(args: list[str], *flags: str) -> tuple[bool, list[str]]:
    """Remove boolean flags from *args*, return (found, remaining)."""
    found = False
    remaining = []
    for a in args:
        if a in flags:
            found = True
        else:
            remaining.append(a)
    return found, remaining


def _pop_value(args: list[str], *flags: str,
               default: str | None = None) -> tuple[str | None, list[str]]:
    """Remove a flag that takes one value, return (value, remaining)."""
    remaining: list[str] = []
    value = default
    skip_next = False
    for i, a in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if a in flags and i + 1 < len(args):
            value = args[i + 1]
            skip_next = True
        else:
            remaining.append(a)
    return value, remaining


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

def _cmd_init(args: list[str]) -> None:
    from pathlib import Path
    from capcat.commands.init import init_project, AlreadyInitializedError
    reinit = "--reinit" in args
    try:
        init_project(Path.cwd(), reinit=reinit)
        print("Capcat project initialized.")
        print("  Config/   -- your sources, themes, and config")
        print("  .capcat/  -- internal state (don't edit)")
        print(
            "\nRun 'capcat catch' for the interactive menu "
            "or 'capcat --help' for commands."
        )
    except AlreadyInitializedError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# single <url>
# ---------------------------------------------------------------------------

def _cmd_single(args: list[str], log_file: str | None = None) -> None:
    """capcat single <url> [--output DIR] [--media] [--html] [--update]
       [--verbose] [--quiet] [--log-file FILE]
    """
    if not args or args[0] in ("-h", "--help"):
        print("Usage: capcat single <url> [--output DIR] [--media] "
              "[--html] [--update] [-V] [-q]")
        return

    verbose, args = _pop_flag(args, "-V", "--verbose")
    quiet, args = _pop_flag(args, "-q", "--quiet")
    media, args = _pop_flag(args, "-M", "--media")
    html, args = _pop_flag(args, "-H", "--html")
    update, args = _pop_flag(args, "-U", "--update")
    output, args = _pop_value(args, "-o", "--output", default=".")
    lf, args = _pop_value(args, "-L", "--log-file")
    log_file = lf or log_file

    if not args:
        print("capcat single: URL required")
        raise SystemExit(1)

    url = args[0]

    # Delegate to legacy run_app via config dict
    _run_legacy({
        "action": "single",
        "url": url,
        "output": output,
        "media": media,
        "html": html,
        "update": update,
        "verbose": verbose,
        "quiet": quiet,
        "log_file": log_file,
    })


# ---------------------------------------------------------------------------
# fetch <sources>
# ---------------------------------------------------------------------------

def _cmd_fetch(args: list[str], log_file: str | None = None) -> None:
    """capcat fetch <sources> [--count N] [--output DIR] [--media] [--html]
       [--update] [--verbose] [--quiet] [--log-file FILE]
    """
    if not args or args[0] in ("-h", "--help"):
        print("Usage: capcat fetch <sources> [--count N] [--output DIR] "
              "[--media] [--html] [--update] [-V] [-q]")
        return

    verbose, args = _pop_flag(args, "-V", "--verbose")
    quiet, args = _pop_flag(args, "-q", "--quiet")
    media, args = _pop_flag(args, "-M", "--media")
    html, args = _pop_flag(args, "-H", "--html")
    update, args = _pop_flag(args, "-U", "--update")
    output, args = _pop_value(args, "-o", "--output", default=".")
    count_str, args = _pop_value(args, "-c", "--count", default="30")
    lf, args = _pop_value(args, "-L", "--log-file")
    log_file = lf or log_file

    if not args:
        print("capcat fetch: source list required (comma-separated)")
        raise SystemExit(1)

    sources = [s.strip() for s in args[0].split(",")]

    _run_legacy({
        "action": "fetch",
        "sources": sources,
        "count": int(count_str),
        "output": output,
        "media": media,
        "html": html,
        "update": update,
        "verbose": verbose,
        "quiet": quiet,
        "log_file": log_file,
    })


# ---------------------------------------------------------------------------
# bundle <name>
# ---------------------------------------------------------------------------

def _cmd_bundle(args: list[str], log_file: str | None = None) -> None:
    """capcat bundle <name> [--count N] [--output DIR] [--media] [--html]
       [--all] [--update] [--verbose] [--quiet] [--log-file FILE]
    """
    if not args or args[0] in ("-h", "--help"):
        print("Usage: capcat bundle <name> [--count N] [--output DIR] "
              "[--media] [--html] [--all] [--update] [-V] [-q]")
        return

    verbose, args = _pop_flag(args, "-V", "--verbose")
    quiet, args = _pop_flag(args, "-q", "--quiet")
    media, args = _pop_flag(args, "-M", "--media")
    html, args = _pop_flag(args, "-H", "--html")
    update, args = _pop_flag(args, "-U", "--update")
    all_bundles, args = _pop_flag(args, "-A", "--all")
    output, args = _pop_value(args, "-o", "--output", default=".")
    count_str, args = _pop_value(args, "-c", "--count", default="30")
    lf, args = _pop_value(args, "-L", "--log-file")
    log_file = lf or log_file

    # Resolve bundle sources via legacy cli module
    from cli import get_available_bundles
    bundles = get_available_bundles()

    if all_bundles:
        ordered = ["techpro", "tech", "news", "science", "ai"]
        active = [b for b in ordered if b in bundles and bundles[b]]
        bundle_name = f"all-bundles-ordered({', '.join(active)})"
        sources = active
    else:
        if not args:
            print("capcat bundle: bundle name required (or --all)")
            raise SystemExit(1)
        bundle_name = args[0]
        if bundle_name not in bundles:
            print(f"capcat bundle: unknown bundle '{bundle_name}'. "
                  f"Available: {', '.join(sorted(bundles.keys()))}")
            raise SystemExit(1)
        sources = bundles[bundle_name]["sources"]

    _run_legacy({
        "action": "bundle",
        "sources": sources,
        "count": int(count_str),
        "output": output,
        "media": media,
        "html": html,
        "update": update,
        "bundle_name": bundle_name,
        "all_bundles": all_bundles,
        "verbose": verbose,
        "quiet": quiet,
        "log_file": log_file,
    })


# ---------------------------------------------------------------------------
# list [sources|bundles|all]
# ---------------------------------------------------------------------------

def _cmd_list(args: list[str]) -> None:
    """capcat list [sources|bundles|all]"""
    what = "all"
    if args and args[0] not in ("-h", "--help"):
        what = args[0]

    if what in ("-h", "--help"):
        print("Usage: capcat list [sources|bundles|all]")
        return

    from cli import list_sources_and_bundles
    list_sources_and_bundles(what)


# ---------------------------------------------------------------------------
# add-source --url <url>
# ---------------------------------------------------------------------------

def _cmd_add_source(args: list[str]) -> None:
    """capcat add-source --url <feed-url>"""
    if not args or args[0] in ("-h", "--help"):
        print("Usage: capcat add-source --url <feed-url>")
        return

    url, args = _pop_value(args, "--url")
    if not url:
        print("capcat add-source: --url is required")
        raise SystemExit(1)

    from cli import add_source
    add_source(url)


# ---------------------------------------------------------------------------
# remove-source
# ---------------------------------------------------------------------------

def _cmd_remove_source(args: list[str]) -> None:
    """capcat remove-source [--dry-run] [--batch FILE] [--undo [ID]]
       [--no-backup] [--no-analytics] [--force]
    """
    if args and args[0] in ("-h", "--help"):
        print("Usage: capcat remove-source [--dry-run] [--batch FILE] "
              "[--undo [BACKUP_ID]] [--no-backup] [--no-analytics] [--force]")
        return

    import argparse
    # Build a minimal Namespace matching what legacy remove_source() expects
    dry_run, args = _pop_flag(args, "-n", "--dry-run")
    no_backup, args = _pop_flag(args, "--no-backup")
    no_analytics, args = _pop_flag(args, "--no-analytics")
    force, args = _pop_flag(args, "-f", "--force")
    batch, args = _pop_value(args, "-b", "--batch")

    # --undo can be bare (meaning 'latest') or take a value
    undo_val = None
    if "--undo" in args or "-u" in args:
        _, args = _pop_flag(args, "--undo", "-u")
        # If there's a remaining positional, treat it as backup id
        if args:
            undo_val = args.pop(0)
        else:
            undo_val = "latest"

    ns = argparse.Namespace(
        dry_run=dry_run,
        no_backup=no_backup,
        no_analytics=no_analytics,
        force=force,
        batch=batch,
        undo=undo_val,
    )

    from cli import remove_source
    remove_source(ns)


# ---------------------------------------------------------------------------
# generate-config
# ---------------------------------------------------------------------------

def _cmd_generate_config(args: list[str]) -> None:
    """capcat generate-config [--output FILE]"""
    if args and args[0] in ("-h", "--help"):
        print("Usage: capcat generate-config [--output FILE]")
        return

    import argparse
    output, _ = _pop_value(args, "-o", "--output")
    ns = argparse.Namespace(output=output)

    from cli import generate_config_command
    generate_config_command(ns)


# ---------------------------------------------------------------------------
# Legacy bridge: feed a config dict into capcat_legacy.run_app logic
# ---------------------------------------------------------------------------

def _run_legacy(config_dict: dict) -> None:
    """Run the legacy application logic with the given config dict.

    Imports capcat_legacy and invokes its run_app path by constructing the
    same config dict that cli.parse_arguments() would return, then feeding
    it to capcat_legacy.run_app's internal flow.
    """
    import os
    from capcat.core.logging_config import get_logger, setup_logging
    from capcat.core.config import get_config

    setup_logging(
        level=config_dict.get("log_level", "INFO"),
        log_file=config_dict.get("log_file"),
        verbose=config_dict.get("verbose", False),
        quiet=config_dict.get("quiet", False),
    )
    logger = get_logger(__name__)

    action = config_dict["action"]

    if action == "single":
        from capcat_legacy import scrape_single_article
        from capcat.core.html_post_processor import launch_web_view

        url = config_dict["url"]
        output_dir = config_dict["output"]
        download_media = config_dict["media"]
        generate_html = config_dict.get("html", False)
        update_mode = config_dict.get("update", False)

        if update_mode:
            from capcat.core.update_manager import get_update_manager
            from capcat.core.article_fetcher import set_global_update_mode
            set_global_update_mode(True)
            um = get_update_manager()
            if not um.check_and_handle_update("single", url=url):
                logger.info("Update cancelled by user")
                set_global_update_mode(False)
                return

        if not url.lower().endswith(".pdf"):
            logger.info(f"Scraping single article: {url}")

        base_dir = None
        try:
            success, base_dir = scrape_single_article(
                url,
                output_dir,
                verbose=config_dict.get("verbose", False),
                files=download_media,
                generate_html=generate_html,
                update_mode=update_mode,
            )
            if success:
                if base_dir is None:
                    logger.info("Operation completed (user skip)")
                    sys.exit(0)

                application_dir = os.path.dirname(os.path.abspath(
                    __import__("capcat_legacy").__file__
                ))
                project_root = os.path.dirname(application_dir)
                rel_path = os.path.relpath(base_dir, project_root)
                output_location = f"../{rel_path}/"

                if generate_html:
                    try:
                        logger.info("Generating HTML web view...")
                        launch_web_view(base_dir, is_single_article=True)
                        import glob
                        pattern = os.path.join(
                            base_dir, "**/html/article.html"
                        )
                        html_files = glob.glob(pattern, recursive=True)
                        if html_files:
                            article_rel = os.path.relpath(
                                html_files[0], project_root
                            )
                            output_location = f"../{article_rel}"
                    except Exception as html_err:
                        logger.warning(f"HTML generation failed: {html_err}")

                logger.info(f"You can find your files in {output_location}")
            else:
                sys.exit(1)

            if update_mode:
                from capcat.core.article_fetcher import set_global_update_mode
                set_global_update_mode(False)
            sys.exit(0)
        except Exception as e:
            logger.error(f"Single article processing failed: {e}")
            if config_dict.get("update", False):
                from capcat.core.article_fetcher import set_global_update_mode
                set_global_update_mode(False)
            sys.exit(1)

    elif action in ("fetch", "bundle"):
        from capcat_legacy import process_sources
        from capcat.core.shutdown import GracefulShutdown

        config = get_config()
        sources = config_dict["sources"]
        generate_html = config_dict.get("html", False)
        output_dir = config_dict["output"]
        bundle_name = config_dict.get("bundle_name")
        update_mode = config_dict.get("update", False)

        if update_mode:
            from capcat.core.update_manager import get_update_manager
            from capcat.core.article_fetcher import set_global_update_mode
            set_global_update_mode(True)
            um = get_update_manager()
            if action == "bundle":
                if not um.check_and_handle_update(
                    "bundle", bundle_name=bundle_name
                ):
                    logger.info("Update cancelled by user")
                    set_global_update_mode(False)
                    return
            else:
                if not um.check_and_handle_update(
                    "fetch", sources=sources
                ):
                    logger.info("Update cancelled by user")
                    set_global_update_mode(False)
                    return

        try:
            # Create args-like object for backward compat
            class Args:
                def __init__(self, cd):
                    self.count = cd.get("count", 30)
                    self.quiet = cd.get("quiet", False)
                    self.verbose = cd.get("verbose", False)
                    self.media = cd.get("media", False)

            args_obj = Args(config_dict)

            if bundle_name and bundle_name.startswith("all-bundles-ordered"):
                from cli import get_available_bundles
                bundles = get_available_bundles()
                for bn in sources:
                    if bn in bundles and bundles[bn]:
                        bsources = bundles[bn]["sources"]
                        logger.info(
                            f"Processing bundle '{bn}': "
                            f"{', '.join(bsources)}"
                        )
                        process_sources(
                            bsources, args_obj, config, logger,
                            generate_html, output_dir,
                        )
                logger.info("All bundles processing completed")
            else:
                if bundle_name:
                    logger.info(
                        f"Fetching articles from bundle '{bundle_name}': "
                        f"{', '.join(sources)}"
                    )
                else:
                    logger.info(
                        f"Fetching articles from sources: "
                        f"{', '.join(sources)}"
                    )
                result = process_sources(
                    sources, args_obj, config, logger,
                    generate_html, output_dir,
                )
                if result["failed"] and not result["successful"]:
                    print(
                        "\nCapcat Info: No articles fetched "
                        "- all sources unavailable\n"
                    )
                    sys.exit(1)

            # Output location
            from datetime import datetime
            formatted_date = datetime.now().strftime("%d-%m-%Y")
            if output_dir == ".":
                output_location = f"../News/news_{formatted_date}/"
            else:
                output_location = os.path.abspath(output_dir)
                if not output_location.endswith("/"):
                    output_location += "/"

            if generate_html:
                try:
                    from capcat.core.html_post_processor import launch_web_view
                    if output_location.startswith("../"):
                        project_root = os.path.dirname(
                            os.path.dirname(os.path.abspath(
                                __import__("capcat_legacy").__file__
                            ))
                        )
                        html_dir = os.path.join(
                            project_root, output_location[3:]
                        )
                    else:
                        html_dir = output_location
                    logger.info("Generating HTML web view...")
                    launch_web_view(html_dir)
                except Exception as html_err:
                    logger.warning(f"HTML generation failed: {html_err}")

            logger.info(f"You can find your files in {output_location}")

            if update_mode:
                from capcat.core.article_fetcher import set_global_update_mode
                set_global_update_mode(False)
            sys.exit(0)

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            if config_dict.get("update", False):
                from capcat.core.article_fetcher import set_global_update_mode
                set_global_update_mode(False)
            sys.exit(1)
