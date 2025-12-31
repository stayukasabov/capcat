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

## PRIORITY RULE: Task Execution Protocol

**WHEN EXECUTING TASKS ALWAYS PROVIDE TASK ORDER LIST FIRST**

Before starting any multi-step task:
1. List all steps in order
2. Show clear task breakdown
3. Get implicit/explicit confirmation
4. Execute sequentially
5. Report completion status

Example:
```
Task Order:
1. Add rule to CLAUDE.md
2. Update dependency script
3. Find test PDF file

Proceeding with execution...
```

## Project Overview

News archiving: 17+ sources → Markdown + media. Plugin-based architecture.

- Python 3.8+
- Config YAML or custom Python sources
- Usernames → "Anonymous"
- Output: `../News/` (batch), `../Capcats/` (single)

## Essential Commands

```bash
# Setup
./scripts/fix_dependencies.sh          # Auto-fix
./scripts/fix_dependencies.sh --force  # Rebuild venv
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Usage
./capcat single https://example.com/article
./capcat fetch hn,bbc --count 15 --media
./capcat bundle tech --count 10
./capcat list sources
./capcat catch                          # Interactive menu
./capcat generate-config                # YAML generator
./capcat add-source --url URL
./capcat remove-source
./capcat -L capcat.log bundle tech --count 10  # Log to file
python capcat.py bundle tech --count 10        # Direct Python
```

## Architecture Overview

```
Application/
├── capcat.py, capcat, run_capcat.py, cli.py
├── core/
│   ├── interactive.py, source_system/, config.py
│   ├── article_fetcher.py, unified_media_processor.py
├── sources/active/
│   ├── config_driven/  # YAML sources
│   └── custom/         # Python sources
├── htmlgen/, themes/, docs/
```

**Source Types:**
1. Config YAML: InfoQ, IEEE (15-30 min)
2. Custom Python: HN, BBC with comments (2-4 hr)

**Core Systems:**
- SourceRegistry: Auto-discovers `sources/active/`
- SessionPool: Shared HTTP connections
- UnifiedMediaProcessor: Media handling
- Template System: HTML generation
- **UnifiedArticleProcessor: Universal article processing entry point (Dec 2025)**

## Unified Article Processing (Dec 2025)

**Problem Solved:**
- Single/fetch/bundle commands had separate processing paths
- Batch mode (fetch/bundle) bypassed specialized sources (Twitter, YouTube)
- HN article → YouTube link = HTTP 403 error

**Solution:**
`core/unified_article_processor.py` - All commands route through single entry point

**Processing Flow:**
```
All Commands → UnifiedArticleProcessor.process_article()
                          ↓
          Check URL against specialized sources
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                     ↓
  Specialized Match?                    No Match
  (Twitter, YouTube,                         ↓
   Medium, Substack)              Source-specific or Generic
        ↓                           ArticleFetcher
  Config-driven placeholder
```

**Specialized Sources:**
- `sources/specialized/twitter/` - Twitter/X.com placeholder ("X.com post")
- `sources/specialized/youtube/` - YouTube placeholder ("YouTube Video")
- `sources/specialized/medium/` - Medium paywall handling
- `sources/specialized/substack/` - Substack handling

**Config-Driven Templates:**
```yaml
# sources/specialized/twitter/config.yaml
template:
  title: "X.com post"
  body: "Visit the original publication."
```

**Integration Points:**
1. `core/unified_source_processor.py:343` - Batch processing (_process_single_article)
2. `core/article_fetcher.py:328` - Single article (fetch_article_content)

**Adding New Specialized Source:**
1. Create `sources/specialized/newsource/config.yaml`
2. Create `sources/specialized/newsource/source.py` (extends BaseSource)
3. Add to `sources/specialized/__init__.py` SPECIALIZED_SOURCES dict
4. Zero code changes needed - config-driven

## Development Standards

**PEP 8:**
- 4 spaces, 79 char max
- Imports: stdlib → third-party → local
- Descriptive names (no single letters except counters)
- Google docstrings, type hints

**Principles:**
- DRY, single responsibility
- Built-ins over custom
- Exception handling for network/file ops

**Testing:**
- Unit tests for new functions
- `pytest --cov=core` before commits
- Test sources individually first

## Critical Rules

**Media:**
- Images: Always download
- Video/Audio/Docs: --media flag only

**Scraping:**
- Check robots.txt
- RSS/API over HTML
- Anti-bot sources: use RSS
- No paywalls
- 1 req/10 sec rate limit

**Versioning:**
- New: `capcat` not `capcat_fixed`
- Backup: `capcat_backup`, `capcat_old`

**No emojis**

## Testing

**Flow:**
1. Present plan, get approval
2. Test bundles first
3. Create `test-diagnose-[item].md`
4. Categorize: HIGH/MEDIUM/LOW
5. Fix by priority

```bash
source venv/bin/activate
./capcat bundle tech --count 5
./capcat fetch hn --count 10
python test_comprehensive_sources.py
```

**Success:**
- No import/syntax errors
- 80%+ source success
- Correct media filtering
- Valid output structure

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

## Bug Investigation

**Check docs/ FIRST before searching code**
1. Search `docs/` for patterns
2. User specs may be documented
3. Example: truncation limits → search docs for "truncat|max.*len|title"

## Common Issues

**Dependencies:**
```bash
./scripts/fix_dependencies.sh --force
python3 scripts/setup_dependencies.py --verbose --force-rebuild
rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

**Module Not Found:**
```bash
./capcat list sources  # Wrapper handles venv
source venv/bin/activate
```

**Source Failures:**
- RSS bypasses anti-bot (Cloudflare)
- DNS/network → feed URL changed
- Check `test-diagnose-*.md`

**Wrapper Issues:**
```bash
python3 run_capcat.py list sources
```

## Key Files

**Docs:**
- `docs/quick-start.md`, `docs/architecture.md`
- `docs/source-development.md`, `docs/interactive-mode.md`
- `docs/source-management-menu.md`, `docs/dependency-management.md`

**Config:**
- `requirements.txt`, `capcat.yml`, `sources/active/bundles.yml`

**Scripts:**
- `scripts/setup_dependencies.py`, `scripts/fix_dependencies.sh`
- `scripts/generate_source_config.py`

**Testing:**
- `test_comprehensive_sources.py`, `test-diagnose-*.md`

## Documentation Philosophy

CLAUDE.md minimal - details in `docs/`:
- Factual only
- No obvious instructions
- Architecture, commands, non-obvious patterns

## Config Priority

1. CLI args → 2. ENV vars → 3. `capcat.yml` → 4. Defaults

## Privacy

- Usernames → "Anonymous"
- Profile links preserved
- No personal data stored

## Quick Reference

**Sources:**
- Tech: hn, lb, iq, gizmodo, ieee, futurism, lesswrong
- News: bbc, guardian
- Science: nature, scientificamerican
- AI: lesswrong, googleai, openai, mitnews
- Sports: bbcsport

**Bundles:**
- tech, techpro, news, science, ai, sports

**Output:**
- Batch: `../News/news_DD-MM-YYYY/Source_DD-MM-YYYY/NN_Title/`
- Single: `../Capcats/cc_DD-MM-YYYY-Title/`
- HTML: `*/html/` with --html flag
