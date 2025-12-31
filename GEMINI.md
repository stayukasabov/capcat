# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Instruction: Absolute Mode

- Eliminate: emojis, filler, hype, soft asks, conversational transitions, call-to-action appendixes
- Assume: user retains high-perception despite blunt tone
- Prioritize: blunt, directive phrasing; aim at cognitive rebuilding, not tone-matching
- Disable: engagement/sentiment-boosting behaviors
- Suppress: metrics like satisfaction scores, emotional softening, continuation bias
- Never mirror: user's diction, mood, or affect
- Speak only: to underlying cognitive tier
- No: questions, offers, suggestions, transitions, motivational content
- Terminate reply: immediately after delivering info - no closures
- Goal: restore independent, high-fidelity thinking
- Outcome: model obsolescence via user self-sufficiency

## Project Overview

Capcat is a news article archiving system that fetches articles from 17+ sources, converts to Markdown, and organizes with media files. Features modular source architecture with dynamic plugin discovery.

**Key Facts:**
- Python 3.8+ required
- Hybrid architecture: config-driven + custom sources
- Privacy-compliant: usernames anonymized as "Anonymous"
- Output: `../News/` (batch) and `../Capcats/` (single articles)

## Essential Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Usage (via wrapper)
./capcat single https://example.com/article              # Single article
./capcat fetch hn,bbc --count 15 --media                # Specific sources
./capcat bundle tech --count 10                         # Predefined bundles
./capcat list sources                                    # Show all sources

# File logging (all commands)
./capcat -L capcat.log bundle tech --count 10           # Timestamped logs to file

# Direct Python (if wrapper fails)
python capcat.py bundle tech --count 10
```

## Architecture Overview

**Core Structure:**
```
Application/
├── capcat.py              # Main application
├── capcat                 # Bash wrapper
├── run_capcat.py          # Python wrapper
├── cli.py                 # CLI interface
├── core/                  # Core modules
│   ├── source_system/     # Source registry, factory, monitoring
│   ├── config.py          # Configuration management
│   ├── article_fetcher.py # Content processing
│   └── unified_media_processor.py  # Media handling
├── sources/
│   ├── active/
│   │   ├── config_driven/ # YAML-configured sources (1 source: InfoQ)
│   │   └── custom/        # Python implementations (10 sources)
│   └── base/              # Base classes and schemas
├── htmlgen/               # HTML generation system
├── themes/                # CSS themes
└── docs/                  # Detailed documentation
```

**Two Source Types:**
1. **Config-Driven** (YAML): Simple sources like InfoQ, IEEE (15-30 min setup)
2. **Custom** (Python): Complex sources like HN, BBC with comments (2-4 hr setup)

**Key Systems:**
- **SourceRegistry**: Auto-discovers sources from `sources/active/`
- **SessionPool**: Shared HTTP connections for performance
- **UnifiedMediaProcessor**: Centralized image/media handling
- **Template System**: HTML generation with source-specific configs

## Development Standards

**PEP 8 Compliance (Mandatory):**
- 4 spaces indentation, max 79 chars line length
- Imports: stdlib → third-party → local (blank line separated)
- Descriptive variable names (no single letters except counters)
- Google-style docstrings for all public functions
- Type hints in function signatures

**Core Principles:**
- DRY: No code duplication
- Single Responsibility: One function, one purpose
- Built-in functions over custom implementations
- Comprehensive exception handling for network/file operations

**Testing Requirements:**
- Every new function needs unit tests
- Run tests before commits: `pytest --cov=core`
- Test sources individually before system tests

## Important Development Rules

**Media Download Requirements:**
- Images: ALWAYS downloaded (regardless of --media flag)
- Video/Audio/Documents: Only with --media flag

**Ethical Scraping:**
- Check robots.txt before adding sources
- Prefer RSS/API over HTML scraping
- Sources with anti-bot protection (Cloudflare, etc.) use RSS feeds to bypass
- No paywalls or subscriptions
- Rate limit: 1 request per 10 seconds

**File Versioning:**
- Keep original names for new versions: `capcat` (new) not `capcat_fixed`
- Backup old versions: `capcat_backup`, `capcat_old`
- Preserves integrations and references

**No Emoji Policy:**
- Never use emojis in code, docs, or communication

## Testing Procedures

**Standard Test Flow:**
1. Present plan and ASK FOR APPROVAL before running
2. Test bundles FIRST (reveal real-world issues)
3. Create `test-diagnose-[item].md` for each test
4. Read all diagnose files and categorize: HIGH/MEDIUM/LOW
5. Fix systematically in priority order

**Test Commands:**
```bash
source venv/bin/activate
./capcat bundle tech --count 5        # Test bundle
./capcat fetch hn --count 10          # Test source
python test_comprehensive_sources.py   # Full test suite
```

**Success Criteria:**
- No import/syntax errors
- 80%+ success rate for sources
- Correct media filtering
- Proper output structure

**HTML/CSS Change Testing:**
When changes are made to CSS or the HTML generation logic, the following procedure must be followed to verify them:
1.  Generate a test article with the `--html` flag. For example: `./capcat fetch hn --count 1 --html`.
2.  Inspect the generated HTML file located in the output directory (`../News/` or `../Capcats/`).
3.  Read the content of the relevant CSS files (e.g., `themes/base.css`, `themes/design-system.css`).
4.  Verify that the CSS changes (e.g., new variables, updated styles) are present and correctly applied.
5.  Verify that the HTML file correctly links to all necessary stylesheets.

## Adding New Sources

**Config-Driven (Simple):**
```yaml
# sources/active/config_driven/configs/newsource.yaml
display_name: "New Source"
base_url: "https://newsource.com/"
category: tech
article_selectors: [".headline a"]
content_selectors: [".article-content"]
```

**Custom (Complex):**
```python
# sources/active/custom/newsource/source.py
from core.source_system.base_source import BaseSource

class NewSource(BaseSource):
    def get_articles(self, count=30):
        # Custom implementation
        pass
```

## Common Issues

**Module Not Found:**
```bash
# Use wrapper (handles venv automatically)
./capcat list sources

# Or activate manually
source venv/bin/activate
```

**Source Failures:**
- Sources using RSS feeds bypass anti-bot protection (Cloudflare, etc.)
- DNS or network errors indicate feed URL may have changed
- Check `test-diagnose-*.md` files for details

**Wrapper Issues:**
```bash
# Use Python wrapper directly
python3 run_capcat.py list sources
```

## Key Files Reference

**Must Read First:**
- `docs/architecture.md` - Complete system design
- `docs/quick-start.md` - Setup guide
- `docs/source-development.md` - Adding sources

**Configuration:**
- `requirements.txt` - Dependencies
- `capcat.yml` - Optional user config (CLI args override)
- `sources/active/bundles.yml` - Bundle definitions

**Testing:**
- `test_comprehensive_sources.py` - Full system test
- `test-diagnose-*.md` - Individual test results

## Documentation Philosophy

**Keep CLAUDE.md minimal** - Details belong in `docs/`:
- No promotional language or self-serving claims
- Factual tone only
- No obvious instructions (e.g., "write tests", "handle errors")
- Focus on architecture, commands, and non-obvious patterns

## Configuration Priority

1. Command-line arguments (highest)
2. Environment variables
3. Config files (`capcat.yml`)
4. Default values (lowest)

## Privacy & Compliance

**Comment Processing:**
- Usernames anonymized to "Anonymous"
- Profile links preserved for reference
- Pattern-based detection in HTML generation
- Legal compliance: no personal data stored

## Quick Reference

**Active Sources:**
- Tech: hn, lb, iq, gizmodo, ieee, futurism, lesswrong
- News: bbc, guardian
- Science: nature, scientificamerican
- AI: lesswrong, googleai, openai, mitnews
- Sports: bbcsport

**Bundles:**
- `tech`: gizmodo + futurism + ieee
- `techpro`: hn + lb + iq
- `news`: bbc + guardian
- `science`: nature + scientificamerican
- `ai`: lesswrong + googleai + openai + mitnews
- `sports`: bbcsport

**Output Structure:**
- Batch: `../News/news_DD-MM-YYYY/Source_DD-MM-YYYY/NN_Title/`
- Single: `../Capcats/cc_DD-MM-YYYY-Title/`
- HTML: `*/html/` subfolder when using --html flag