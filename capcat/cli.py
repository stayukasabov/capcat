"""CLI entry point for Capcat.

Routes subcommands to legacy capcat_legacy.py / cli.py logic via delegating
stubs.  Every heavy import lives inside the function body (lazy import) so
startup stays fast and circular-import-safe.
"""
from __future__ import annotations
import sys
from pathlib import Path


GLOBAL_SETTINGS_TEMPLATE = """\
# Global Settings - Capcat
# Edit this file to tune behavior for this vault.
# All fields are optional. Defaults are shown in comments.
# Restart capcat after editing.
#
# ── Article count ────────────────────────────────────────────────────────────
# The article_count field below is a global fallback only.
# Each source has its own count defined in its config.yaml inside your vault:
#   Config/sources/active/hn/config.yaml  →  article_count: 10
#   Config/sources/active/lb/config.yaml  →  article_count: 5
# Edit those files to control how many articles each source fetches.
# The global fallback here only applies to custom sources that have no
# article_count in their own config.yaml.
#
# ── Upgrading ────────────────────────────────────────────────────────────────
# After a capcat upgrade, new settings may have been added to this template.
# To regenerate this file with all the latest settings:
#   capcat settings --force
# Warning: --force overwrites this file completely. Back up your edits first.

# ─── PDF Downloads ──────────────────────────────────────
pdf:
  # Skip PDF files larger than this size in bytes.
  # Default: 20971520 (20MB). Examples: 10485760 = 10MB, 52428800 = 50MB
  max_pdf_size_bytes: 20971520

  # Maximum number of PDFs queued per article.
  # Default: 10
  max_pdf_per_article: 10

# ─── Media Downloads ─────────────────────────────────────
media:
  # Download PDF files when capcat encounters a direct PDF link.
  # When false, capcat generates a stub note instead of downloading the PDF.
  # Override per-source in Config/sources/active/<source>/config.yaml
  # or per-run in Config/capcat.yml under the source entry.
  # Default: false
  download_pdfs: false

  # Download and embed images locally.
  # Default: true
  download_images: true

  # Download video files.
  # Default: false
  download_videos: false

  # Download audio files.
  # Default: false
  download_audio: false

  # Download generic document files (non-PDF).
  # Default: false
  download_documents: false

# ─── Network ────────────────────────────────────────────
network:
  # TCP connection timeout in seconds. Increase for slow servers.
  # Default: 10
  connect_timeout: 10

  # HTTP response body read timeout in seconds.
  # Default: 30
  read_timeout: 30

  # Image and PDF download timeout in seconds.
  # Default: 60
  media_download_timeout: 60

  # HEAD request timeout for link checking in seconds.
  # Default: 10
  head_request_timeout: 10

  # Retry attempts on network failure.
  # Default: 3
  max_retries: 3

  # Base delay between retries in seconds.
  # Default: 1.0
  retry_delay: 1.0

  # Minimum seconds between requests to the same domain.
  # Default: 1.0
  crawl_delay: 1.0

  # How long to cache robots.txt responses in minutes.
  # Default: 15
  robots_cache_ttl_minutes: 15

  # HTTP User-Agent header sent with all requests.
  # Default: "Capcat/2.0 (Personal news archiver)"
  user_agent: "Capcat/2.0 (Personal news archiver)"

  # HTTP connection pool size.
  # Default: 20
  pool_connections: 20

  # Maximum concurrent connections.
  # Default: 20
  pool_maxsize: 20

# ─── Processing ─────────────────────────────────────────
processing:
  # Global fallback - articles fetched per source when no per-source count
  # is set. This value is rarely reached for sources that already have
  # article_count defined in their own config.
  #
  # To set a per-source count, edit the source's config.yaml in your vault:
  #   Config/sources/active/hn/config.yaml  →  article_count: 10
  #   Config/sources/active/lb/config.yaml  →  article_count: 5
  #
  # Default: 30
  article_count: 30

  # Concurrent article fetcher workers.
  # Default: 8
  max_workers: 8

  # HTML to Markdown conversion timeout in seconds.
  # Default: 30
  conversion_timeout: 30

  # Maximum images downloaded per article (normal mode).
  # Default: 20
  max_images: 20

  # Maximum images downloaded per article when --media flag is active.
  # Default: 1000
  max_images_media_mode: 1000

  # Skip images whose width OR height is smaller than this value in pixels.
  # Raises the floor above the built-in 64px icon/tracker filter.
  # Example: 400 keeps only editorial-sized images; 150 is a light filter.
  # Default: 150
  min_image_dimensions: 150

  # Skip images larger than this in bytes (checked via content-length before download).
  # Protects vault disk space from raw high-resolution files.
  # Default: 5242880 (5MB). Examples: 1048576 = 1MB, 2097152 = 2MB
  max_image_size_bytes: 5242880

  # Maximum characters in vault filenames.
  # Default: 100
  max_filename_length: 100

  # Download and embed images locally.
  # Default: true
  download_images: true

  # Download video files.
  # Default: false
  download_videos: false

  # Download audio files.
  # Default: false
  download_audio: false

  # Download generic document files.
  # Default: false
  download_documents: false

  # Fetch and save comments alongside articles.
  # Default: true
  create_comments_file: true

  # Strip <style> tags from HTML before conversion.
  # Set to false to keep inline CSS text in the markdown output.
  # Default: true
  remove_style_tags: true

  # Strip <nav> tags from HTML before conversion.
  # Set to false to include navigation menus and breadcrumbs in the output.
  # Default: true
  remove_nav_tags: true

  # Produce hard line breaks in markdown for every <br> tag.
  # When true: <br> becomes \\ (Obsidian, GitHub, CommonMark hard break).
  # When false: <br> becomes a plain newline - renderer controls reflowing.
  # Advanced users: set false for cleaner paragraph flow in strict renderers.
  # Default: true
  markdown_line_breaks: true

# ─── UI ─────────────────────────────────────────────────
ui:
  # Spinner style for article progress.
  # Options: dots, wave, loading, pulse, bounce, modern
  # Default: dots
  progress_spinner_style: dots

# ─── Logging ────────────────────────────────────────────
logging:
  # Console log verbosity. Options: DEBUG, INFO, WARNING, ERROR
  # INFO shows normal fetch progress.
  # WARNING suppresses info messages - useful for scripted/quiet runs
  #   that need cleaner output than -q but still want error visibility.
  # DEBUG shows full request-level detail.
  # Note: -V / --verbose and -q / --quiet flags override this at runtime.
  # Default: INFO
  console_level: INFO

  # Log level written to log file (when --log-file is used).
  # Default: DEBUG
  file_level: DEBUG

  # Maximum log file size before rotation in bytes.
  # Default: 10485760 (10MB)
  max_log_file_size: 10485760

  # Number of rotated log files to keep.
  # Default: 5
  log_file_backup_count: 5

  # Auto-create log directory if it does not exist.
  # Default: true
  auto_create_log_dir: true

"""


# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

def _print_help() -> None:
    """Print the top-level usage text to stdout and return."""
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
        "  settings         Write Global-settings.yaml template to Config/\n"
        "  settings --force Overwrite existing Global-settings.yaml with the\n"
        "                   latest template (preserves nothing - back up first)\n"
        "\nOptions:\n"
        "  -L <file>        Log output to file\n"
        "  -V, --verbose    Verbose output\n"
        "  -q, --quiet      Quiet output\n"
        "  --media          Download media files\n"
        "  --html           Generate HTML output\n"
        "  --update         Update existing articles\n"
        "  --version        Show version and exit\n"
        "  --help           Show this help\n"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_app(args: list) -> None:
    """Programmatic entry point - run capcat with a pre-built argument list."""
    _dispatch(args)


def _raise_fd_limit() -> None:
    """Raise the OS file descriptor soft limit to prevent 'Too many open files'.

    Multiple thread pools (article workers, PDF manager, media executor,
    conversion executor) open many files and sockets concurrently.
    The macOS default soft limit of 256 is easily exhausted.
    """
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        target = min(4096, hard)
        if soft < target:
            resource.setrlimit(resource.RLIMIT_NOFILE, (target, hard))
    except Exception:
        pass


def main() -> None:
    """Main entry point.  Routes to TUI or CLI dispatch."""
    _raise_fd_limit()
    args = sys.argv[1:]
    if args and args[0] == "catch":
        _auto_init("catch")
        from capcat.tui import run
        run()
    else:
        _dispatch(args)


# ---------------------------------------------------------------------------
# Top-level dispatch
# ---------------------------------------------------------------------------

def _dispatch(args: list[str]) -> None:
    """Route a raw argument list to the appropriate command handler.

    Handles global flags (-L, --version, --help) before delegating to
    per-command functions. Exits with code 1 on unknown commands.

    Args:
        args: sys.argv[1:] with the program name already removed.
    """
    if not args or args[0] in ("-h", "--help"):
        _print_help()
        return

    if args[0] == "--version":
        from capcat import __version__
        print(f"capcat {__version__}")
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

    _auto_init(command)

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
    elif command == "settings":
        _cmd_settings(rest)
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
    """Handle the ``capcat init`` command.

    Creates ``.capcat/`` state directory and ``Config/`` scaffold in cwd.
    Exits with code 1 if the project is already initialized (unless
    ``--reinit`` is passed).

    Args:
        args: Remaining arguments after ``init`` (e.g. ``["--reinit"]``).
    """
    from pathlib import Path
    from capcat.commands.init import init_project, AlreadyInitializedError
    reinit = "--reinit" in args
    try:
        init_project(Path.cwd(), reinit=reinit)
        if not reinit:
            user_settings = Path.home() / ".config" / "capcat" / "Global-settings.yaml"
            if not user_settings.exists():
                user_settings.parent.mkdir(parents=True, exist_ok=True)
                user_settings.write_text(GLOBAL_SETTINGS_TEMPLATE, encoding="utf-8")
            vault_settings = Path("Config") / "Global-settings.yaml"
            if not vault_settings.exists():
                vault_settings.write_text(GLOBAL_SETTINGS_TEMPLATE, encoding="utf-8")
        print("Capcat project initialized.")
        print("  Config/   -- your themes")
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
    pdfs, args = _pop_flag(args, "-P", "--pdfs")
    html, args = _pop_flag(args, "-H", "--html")
    update, args = _pop_flag(args, "-U", "--update")
    output, args = _pop_value(args, "-o", "--output", default=".")
    lf, args = _pop_value(args, "-L", "--log-file")
    log_file = lf or log_file

    if not args:
        print("capcat single: URL required")
        raise SystemExit(1)

    url = args[0]

    _setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)

    from capcat.commands.single import scrape_single_article
    success, out_dir = scrape_single_article(
        url=url,
        output_dir=output,
        verbose=verbose,
        files=media,
        pdfs=pdfs or media,
        generate_html=html,
        update_mode=update,
    )
    if success and out_dir:
        print(f"Saved to: {out_dir}")


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
    pdfs, args = _pop_flag(args, "-P", "--pdfs")
    no_pdfs, args = _pop_flag(args, "--no-pdfs")
    html, args = _pop_flag(args, "-H", "--html")
    update, args = _pop_flag(args, "-U", "--update")
    output, args = _pop_value(args, "-o", "--output", default=".")
    count_str, args = _pop_value(args, "-c", "--count", default=None)
    lf, args = _pop_value(args, "-L", "--log-file")
    log_file = lf or log_file

    if not args:
        print("capcat fetch: source list required (space- or comma-separated)")
        raise SystemExit(1)

    sources = [s.strip() for a in args for s in a.split(",") if s.strip()]
    count = int(count_str) if count_str is not None else None

    _setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)

    import argparse as _argparse
    from capcat.core.logging_config import get_logger
    from capcat.commands.fetch import process_sources

    _args = _argparse.Namespace(
        count=count, quiet=quiet, verbose=verbose, media=media,
        pdfs=pdfs or media, no_pdfs=no_pdfs,
    )
    logger = get_logger(__name__)
    process_sources(
        sources=sources,
        args=_args,
        config=None,
        logger=logger,
        generate_html=html,
        output_dir=output,
    )


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
    pdfs, args = _pop_flag(args, "-P", "--pdfs")
    no_pdfs, args = _pop_flag(args, "--no-pdfs")
    html, args = _pop_flag(args, "-H", "--html")
    update, args = _pop_flag(args, "-U", "--update")
    all_bundles, args = _pop_flag(args, "-A", "--all")
    output, args = _pop_value(args, "-o", "--output", default=".")
    count_str, args = _pop_value(args, "-c", "--count", default=None)
    lf, args = _pop_value(args, "-L", "--log-file")
    log_file = lf or log_file

    from capcat.core.source_system.bundle_service import get_available_bundles
    from capcat.core.config import find_project_root, NoProjectError
    try:
        _project_root = find_project_root()
    except NoProjectError:
        _project_root = None
    bundles = get_available_bundles(project_root=_project_root)

    def _expand_bundles(bundle_names):
        seen, result = set(), []
        for b in bundle_names:
            for sid in bundles.get(b, {}).get("sources", []):
                if sid not in seen:
                    seen.add(sid)
                    result.append(sid)
        return result

    if all_bundles:
        ordered = ["techpro", "tech", "news", "science", "ai"]
        active = [b for b in ordered if b in bundles and bundles[b]]
        bundle_name = f"all-bundles-ordered({', '.join(active)})"
        sources = _expand_bundles(active)
    else:
        if not args:
            print("capcat bundle: bundle name required (or --all)")
            raise SystemExit(1)
        bundle_name = args[0]
        if bundle_name == "all":
            ordered = ["techpro", "tech", "news", "science", "ai"]
            active = [b for b in ordered if b in bundles and bundles[b]]
            bundle_name = f"all-bundles-ordered({', '.join(active)})"
            sources = _expand_bundles(active)
        else:
            if bundle_name not in bundles:
                print(f"capcat bundle: unknown bundle '{bundle_name}'. "
                      f"Available: {', '.join(sorted(bundles.keys()))}")
                raise SystemExit(1)
            sources = bundles[bundle_name]["sources"]

    count = int(count_str) if count_str is not None else None

    _setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)

    import argparse as _argparse
    from capcat.core.logging_config import get_logger
    from capcat.commands.fetch import process_sources

    _args = _argparse.Namespace(
        count=count, quiet=quiet, verbose=verbose, media=media,
        pdfs=pdfs or media, no_pdfs=no_pdfs,
    )
    logger = get_logger(__name__)
    process_sources(
        sources=sources,
        args=_args,
        config=None,
        logger=logger,
        generate_html=html,
        output_dir=output,
    )


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

    from capcat.core.source_system.source_registry import SourceRegistry
    from capcat.core.source_system.bundle_service import get_available_bundles
    from capcat.core.config import find_project_root, NoProjectError
    try:
        _project_root = find_project_root()
    except NoProjectError:
        _project_root = None

    registry = SourceRegistry(project_root=_project_root)
    registry.discover_sources()

    if what in ("sources", "all"):
        print("\nAvailable sources:")
        for sid in sorted(registry.get_available_sources()):
            cfg = registry.get_source_config(sid)
            name = cfg.display_name if cfg else sid
            print(f"  {sid:<20} {name}")

    if what in ("bundles", "all"):
        bundles = get_available_bundles(project_root=_project_root)
        print("\nAvailable bundles:")
        for bundle_id, bundle_data in sorted(bundles.items()):
            sources_list = bundle_data["sources"]
            sources_str = ", ".join(sources_list[:3])
            if len(sources_list) > 3:
                sources_str += f", ... ({len(sources_list)} total)"
            desc = bundle_data.get("description", "")
            print(f"  {bundle_id:<20} {desc}")
            print(f"  {'':20} Sources: {sources_str}")


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

    from capcat.commands.add_source import add_source
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

    from capcat.commands.remove_source import remove_source
    remove_source(ns)


# ---------------------------------------------------------------------------
# settings
# ---------------------------------------------------------------------------

def _cmd_settings(args: list[str]) -> None:
    """Write Global-settings.yaml template to Config/ directory."""
    if args and args[0] in ("-h", "--help"):
        print(
            "Usage: capcat settings [--force]\n\n"
            "Write the Global-settings.yaml template to Config/ in the current vault.\n\n"
            "The file controls vault-wide defaults: network timeouts, image limits,\n"
            "PDF rules, logging, and UI preferences.\n\n"
            "Per-source article counts are NOT set here. Edit the source's own\n"
            "config.yaml inside your vault instead:\n"
            "  Config/sources/active/hn/config.yaml  →  article_count: 10\n\n"
            "Options:\n"
            "  --force   Overwrite an existing Global-settings.yaml with the latest\n"
            "            template. All local edits will be lost - back up the file\n"
            "            first if you want to keep custom values.\n"
            "            Useful after a capcat upgrade to pick up newly added settings.\n"
        )
        return
    force = "--force" in args
    out = Path("Config") / "Global-settings.yaml"
    if out.exists() and not force:
        print("Config/Global-settings.yaml already exists. Use --force to overwrite.")
        return
    out.write_text(GLOBAL_SETTINGS_TEMPLATE, encoding="utf-8")
    print(f"Written: {out.resolve()}")


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

    from capcat.commands.generate_config import generate_config
    generate_config(ns)


# ---------------------------------------------------------------------------
# Auto-init
# ---------------------------------------------------------------------------

def _auto_init(command: str) -> None:
    """Initialize a capcat project in cwd if not already initialized.

    Runs silently before any command except init/help/version.
    """
    _skip = {"init", "--help", "-h", "--version"}
    if command in _skip:
        return
    from pathlib import Path
    from capcat.commands.init import init_project, AlreadyInitializedError
    try:
        init_project(Path.cwd())
        print("Initialized capcat in ./")
    except AlreadyInitializedError:
        pass

    # Ensure vault-level Global-settings.yaml exists before any command runs.
    # Config files must be present before downloads start so users can tune
    # settings without having to manually run `capcat settings`.
    vault_settings = Path("Config") / "Global-settings.yaml"
    if not vault_settings.exists() and Path("Config").is_dir():
        vault_settings.write_text(GLOBAL_SETTINGS_TEMPLATE, encoding="utf-8")

    # Check if package themes have been updated since last init
    try:
        from capcat.core.config import find_project_root, check_theme_upgrade, NoProjectError
        check_theme_upgrade(find_project_root())
    except NoProjectError:
        pass  # Not in a capcat project - skip silently
    except Exception:
        import logging
        logging.getLogger("capcat.cli").debug("Theme upgrade check failed", exc_info=True)


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def _setup_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_file: str | None = None,
) -> None:
    """Configure logging for the current command."""
    from capcat.core.logging_config import setup_logging
    from capcat.core.config import get_config
    console_level = get_config().logging.console_level
    setup_logging(verbose=verbose, quiet=quiet, log_file=log_file, level=console_level)
