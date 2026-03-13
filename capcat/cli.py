"""CLI entry point for Capcat."""
from __future__ import annotations
import sys


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
        "  --help           Show this help\n"
    )


def main() -> None:
    """Main entry point. Routes to TUI or CLI dispatch."""
    args = sys.argv[1:]
    if args and args[0] == "catch":
        from capcat.tui import run
        run()
    else:
        _dispatch(args)


def _dispatch(args: list[str]) -> None:
    if not args or args[0] in ("-h", "--help"):
        _print_help()
        return
    command = args[0]
    if command == "init":
        _cmd_init(args[1:])
    else:
        print(f"capcat: unknown command '{command}'. Run 'capcat --help'.")
        raise SystemExit(1)


def _cmd_init(args: list[str]) -> None:
    from pathlib import Path
    from capcat.commands.init import init_project, AlreadyInitializedError
    reinit = "--reinit" in args
    try:
        init_project(Path.cwd(), reinit=reinit)
        print("Capcat project initialized.")
        print("  Config/   — your sources, themes, and config")
        print("  .capcat/  — internal state (don't edit)")
        print(
            "\nRun 'capcat catch' for the interactive menu "
            "or 'capcat --help' for commands."
        )
    except AlreadyInitializedError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)
