# Developer Guide

## Prerequisites

- Python 3.11+
- [pipx](https://pipx.pypa.io/) for isolated CLI install
- git

## Setup: Development Environment

```bash
git clone https://github.com/stayukasabov/capcat.git
cd capcat
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

Verify:
```bash
python3 -c "import capcat; print(capcat.__version__)"
```

## Setup: End-User Install (pipx)

```bash
pipx install capcat
capcat --version
```

Upgrade:
```bash
pipx upgrade capcat
```

## Project Structure

```
capcat/                          # Python package root
├── capcat/                      # Source package
│   ├── __init__.py              # Version
│   ├── cli.py                   # CLI entry point (_dispatch, _cmd_*)
│   ├── commands/                # Command implementations (fetch, single, bundle)
│   ├── core/                    # Core systems
│   │   ├── interactive.py       # TUI (questionary-based)
│   │   ├── session_pool.py      # HTTP session management
│   │   ├── unified_source_processor.py  # Article processing pipeline
│   │   ├── unified_article_processor.py # Per-article routing
│   │   ├── config/              # Configuration (get_news_dir, get_capcats_dir)
│   │   └── source_system/       # Source registry, feed parser, bundle service
│   ├── sources/
│   │   ├── builtin/             # Packaged sources
│   │   │   ├── bundles.yml      # Bundle definitions
│   │   │   ├── config_driven/configs/  # YAML source configs
│   │   │   └── custom/          # HN, Lobsters Python sources
│   │   └── specialized/         # Twitter, YouTube, Medium, Substack placeholders
│   ├── htmlgen/                 # HTML generation templates
│   └── themes/                  # CSS themes
├── tests/
│   └── unit/                    # Unit tests (pytest)
├── docs/                        # Documentation
└── context-engineering/         # Claude Code context files (trigger system)
```

## CLI Standards

Follow [clig.dev](https://clig.dev/) for all CLI design.

Key rules:
- `--version` prints `capcat <version>` and exits 0
- `--help` / `-h` prints usage and exits 0
- Errors to stderr; output to stdout
- Exit 0 on success, non-zero on failure
- Short flags for frequent options; long flags always available

## Running Tests

```bash
cd ~/capcat && source venv/bin/activate
pytest tests/unit/ -v
```

Coverage:
```bash
pytest tests/unit/ --cov=capcat --cov-report=term-missing
```
