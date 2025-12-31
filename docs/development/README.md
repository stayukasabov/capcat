# Development Documentation

## Overview

This directory contains comprehensive technical documentation for Capcat developers, including architecture details, design patterns, implementation logic, and team onboarding materials.

---

## Document Index

### 1. Architecture & Logic
**File**: `01-architecture-logic.md`

**Purpose**: Complete technical architecture explanation for junior developers

**Contents**:
- System architecture layers (UI, orchestration, source, processing, output)
- Hybrid source system (config-driven vs custom)
- Core design patterns (Factory, Registry, Strategy, Session Pooling, Observer)
- Complete data flow diagrams
- Error handling strategy
- Performance optimizations
- Security considerations
- Configuration management

**Target Audience**: Junior developers, new team members, code reviewers

**Key Concepts**:
- Hybrid architecture supporting 2 source types
- Registry pattern for source discovery
- Factory pattern for source instantiation
- Graceful degradation on errors
- Connection pooling for performance

**Code Examples**: 30+ real code snippets with explanations

---

### 2. Team Onboarding
**File**: `02-team-onboarding.md`

**Purpose**: Complete onboarding guide for new developers and designers

**Contents**:
- Day 1: Environment setup and verification
- Day 1-2: Codebase exploration exercises
- Day 3-4: First contribution tasks
- Week 1: Deep dive sessions (architecture, user interface, testing)
- Week 2: Collaboration practices (code review, git workflow)
- Development workflows (adding sources, fixing bugs)
- Common tasks and debugging tips
- Success checklist and next steps

**Target Audience**: New team members (developers)

**Time Estimate**:
- Setup: 30 minutes
- Codebase exploration: 2 days
- First contribution: 3-4 days
- Full onboarding: 2 weeks

**Learning Path**:
1. Environment setup → Working Capcat installation
2. Code exploration → Understanding architecture
3. Small contributions → Confidence building
4. Independent work → Full productivity

---

## How to Use This Documentation

### For New Developers

**Week 1 Roadmap**:

**Day 1: Setup** (2-4 hours)
```bash
# Follow setup in 02-team-onboarding.md
git clone <repo>
./scripts/fix_dependencies.sh
./capcat list sources  # Verify installation
```

**Day 2: Architecture** (4-6 hours)
1. Read `01-architecture-logic.md` sections 1-3
2. Draw architecture diagram from memory
3. Complete Exercise 2: Trace code flow
4. Review design patterns section

**Day 3: First Contribution** (4-6 hours)
1. Pick Task 1 or 2 from onboarding guide
2. Add config-driven source or fix documentation
3. Create pull request
4. Iterate based on feedback

**Day 4-5: Deep Understanding** (8-10 hours)
1. Complete all hands-on exercises
2. Add custom source (if comfortable with Python)
3. Write tests for your contribution
4. Attend deep dive sessions

### For Experienced Developers

**Quick Reference**:

**Adding New Source**:
- Config-driven: See "Adding a New Config-Driven Source" in onboarding doc
- Custom: See "Adding a New Custom Source" + Architecture patterns in logic doc

**Understanding Data Flow**:
- Section "Complete Article Fetching Flow" in `01-architecture-logic.md`
- Follow execution: CLI → Registry → Factory → Source → Processing → Output

**Debugging Issues**:
- "Debugging Tips" section in onboarding doc
- "Error Handling Strategy" in architecture doc
- Use `--debug` flag for verbose logging

**Code Review Guidelines**:
- "Code Review Guidelines" in onboarding doc
- Check against design patterns in architecture doc

### For Product Designers

**Understanding Technical Constraints**:

1. **Why Hybrid Architecture?**
   - Read: `01-architecture-logic.md` "Hybrid Source Layer" section
   - Understand: Config-driven (simple, 30min) vs Custom (complex, 4hr)
   - Implication: Feature complexity affects development time

2. **Why CLI First?**
   - Read: Architecture decisions
   - Understand: Automation, scriptability, power users
   - Implication: GUI is secondary, not primary interface

3. **Performance Constraints**:
   - Read: "Performance Optimizations" in architecture doc
   - Understand: Network I/O is bottleneck
   - Implication: Bulk operations faster than individual

4. **Privacy Architecture**:
   - Read: "Security Considerations" in architecture doc
   - Understand: Local-first, no telemetry by design
   - Implication: Analytics limited, user research critical

**Collaboration Points**:
- Feature feasibility discussion
- Technical constraints awareness
- Implementation time estimates
- Interface vs technical tradeoffs

### For Code Reviewers

**Review Checklist** (from onboarding doc):

**Architecture Compliance**:
- [ ] Follows established patterns (Factory, Registry, Strategy)
- [ ] Fits into layer architecture (doesn't violate boundaries)
- [ ] Reuses existing components (no reinventing wheel)
- [ ] Maintains separation of concerns

**Code Quality**:
- [ ] PEP 8 compliant
- [ ] Docstrings present and clear
- [ ] No code duplication
- [ ] Single responsibility principle

**Testing**:
- [ ] Unit tests for new functions
- [ ] Integration tests for workflows
- [ ] Edge cases covered
- [ ] Tests actually test what they claim

**Documentation**:
- [ ] README updated if user-facing change
- [ ] Architecture doc updated if structural change
- [ ] API reference updated if interface change
- [ ] Comments explain "why" not "what"

---

## Architecture Overview

### System Layers

```
┌─────────────────────────────────────┐
│     USER INTERFACES                 │  cli.py, interactive.py
├─────────────────────────────────────┤
│     CORE ORCHESTRATION              │  capcat.py, config.py
├─────────────────────────────────────┤
│     SOURCE SYSTEM                   │  Registry, Factory, Sources
├─────────────────────────────────────┤
│     CONTENT PROCESSING              │  Fetcher, MediaProcessor
├─────────────────────────────────────┤
│     OUTPUT GENERATION               │  FileWriter, HTMLGenerator
└─────────────────────────────────────┘
```

### Key Components

**Source System**:
- `SourceRegistry`: Auto-discovers sources from filesystem
- `SourceFactory`: Creates appropriate source instance
- `BaseSource`: Abstract base for all sources
- `ConfigDrivenSource`: YAML-based simple sources
- Custom sources: Python implementations

**Processing Pipeline**:
1. Article discovery (Source.get_articles)
2. Content fetching (ArticleFetcher)
3. Media processing (UnifiedMediaProcessor)
4. Format conversion (HTMLConverter)
5. File generation (FileWriter)

**Design Patterns**:
- Factory: Source creation
- Registry: Source discovery
- Strategy: Content extraction
- Observer: Progress tracking
- Singleton: Session pooling

---

## Development Workflows

### Quick Reference

**Add Config Source** (30 min):
```bash
# Create YAML config
cat > sources/active/config_driven/configs/source.yaml <<EOF
display_name: "Source Name"
base_url: "https://example.com/"
category: tech
article_selectors: [".headline a"]
content_selectors: [".article-body"]
EOF

# Test
./capcat fetch source --count 5
```

**Add Custom Source** (4 hrs):
```bash
# Create structure
mkdir -p sources/active/custom/source
cd sources/active/custom/source

# Create source.py (implement BaseSource)
# Create config.yaml
# Create __init__.py

# Test and commit
```

**Fix Bug**:
1. Write failing test
2. Fix code
3. Verify test passes
4. Run full test suite
5. Commit with "fix:" prefix

**Add Feature**:
1. Discuss with team
2. Update architecture doc if needed
3. Implement with tests
4. Update user docs
5. Create PR with detailed description

---

## Code Organization

### Directory Structure

```
Application/
├── capcat.py              # Main application
├── cli.py                 # CLI interface
├── core/                  # Core modules
│   ├── source_system/     # Source management
│   │   ├── source_registry.py
│   │   ├── source_factory.py
│   │   ├── base_source.py
│   │   └── config_driven_source.py
│   ├── article_fetcher.py
│   ├── unified_media_processor.py
│   └── config.py
├── sources/
│   └── active/
│       ├── config_driven/
│       │   └── configs/*.yaml
│       └── custom/
│           └── */source.py
├── tests/                 # Test suite
├── docs/                  # Documentation
│   ├── tutorials/        # User and exhaustive tutorials
│   └── development/      # This directory
└── scripts/              # Utility scripts
```

### Import Conventions

```python
# Standard library
import os
import sys
from typing import List, Dict

# Third-party
import requests
import yaml
from bs4 import BeautifulSoup

# Local modules
from core.config import get_config
from core.source_system.base_source import BaseSource
from core.exceptions import SourceError
```

### Naming Conventions

**Files**: `lowercase_with_underscores.py`
**Classes**: `PascalCase`
**Functions**: `lowercase_with_underscores`
**Constants**: `UPPERCASE_WITH_UNDERSCORES`
**Private**: `_leading_underscore`

---

## Testing Strategy

### Test Types

**Unit Tests** (Fast, isolated):
```python
# Test individual functions
def test_slugify():
    assert slugify("Hello World") == "hello_world"
    assert slugify("Test@#$123") == "test_123"
```

**Integration Tests** (Medium speed, component interaction):
```python
# Test component interactions
def test_source_registry_and_factory():
    registry = SourceRegistry()
    source = registry.get_source('hn')
    articles = source.get_articles(count=5)
    assert len(articles) == 5
```

**End-to-End Tests** (Slow, full workflow):
```python
# Test complete user workflows
def test_fetch_command_workflow():
    result = run_capcat("fetch hn --count 5")
    assert result.success
    assert output_exists()
```

### Coverage Goals

- Core modules: 90%+
- Sources: 80%+
- CLI: 70%+
- Overall: 85%+

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=core --cov=sources

# Specific module
pytest tests/test_source_registry.py

# Watch mode (re-run on change)
ptw
```

---

## Common Patterns

### Error Handling

```python
try:
    result = operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return default_value
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

### Logging

```python
logger = get_logger(__name__)

logger.debug("Detailed debug info")
logger.info("User-relevant information")
logger.warning("Something unexpected")
logger.error("Operation failed")
logger.exception("Error with traceback")
```

### Configuration

```python
# Get configuration
config = get_config()
count = config.get('default_count', 30)

# Respect CLI override
if args.count:
    count = args.count
```

---

## Performance Guidelines

### Do's

- Use session pooling for HTTP requests
- Parallelize independent operations
- Cache expensive computations
- Use generators for large datasets
- Lazy load when possible

### Don'ts

- Don't create new sessions per request
- Don't process serially when can parallelize
- Don't load entire files into memory
- Don't make unnecessary network calls
- Don't ignore timeouts

### Example Optimization

```python
# Bad: Sequential processing
for article in articles:
    content = fetch_content(article.url)  # Slow
    process(content)

# Good: Parallel processing
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as executor:
    contents = executor.map(fetch_content, article_urls)
    for content in contents:
        process(content)
```

---

## Security Guidelines

### Input Validation

```python
def validate_count(count):
    if not 1 <= count <= 1000:
        raise ValidationError("Count must be 1-1000")
    return count
```

### Path Sanitization

```python
def sanitize_path(path):
    # Remove path traversal
    path = path.replace('..', '')
    # Remove absolute paths
    path = path.lstrip('/')
    return path
```

### No Secrets in Code

```python
# Bad
API_KEY = "secret_key_12345"

# Good
API_KEY = os.getenv('CAPCAT_API_KEY')
if not API_KEY:
    raise ConfigError("API_KEY not set")
```

---

## Related Documentation

### User Documentation

- **Quick Start**: `../quick-start.md`
- **Getting Started Tutorial**: `../tutorials/user/01-getting-started.md`
- **Architecture**: `../architecture.md`
- **Source Development**: `../source-development.md`
- **Testing Guide**: `../testing.md`

### API Documentation

- **API Reference**: `../api-reference.md`
- **Module Docs**: `../api/`

---

## Contributing

### Before Starting Work

1. Check existing issues and PRs
2. Discuss significant changes with team
3. Read relevant documentation
4. Understand user impact

### Development Process

1. Create feature branch
2. Write failing tests
3. Implement feature
4. Make tests pass
5. Update documentation
6. Create pull request
7. Address review feedback
8. Merge when approved

### Code Review Process

1. Self-review checklist
2. Automated checks (CI)
3. Peer review (2 approvals)
4. Architecture review (for significant changes)
5. UX review (for user-facing changes)

---

## Resources

### Internal

- **Codebase**: GitHub repository
- **Documentation**: `docs/` directory
- **Examples**: `examples/` directory
- **Tests**: `tests/` directory

### External

- **Python**: https://docs.python.org/3/
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/
- **Requests**: https://requests.readthedocs.io/
- **Pytest**: https://docs.pytest.org/

---

## Contact

**Tech Lead**: [Name]
**Senior Developer**: [Name]
**DevOps**: [Name]

**Channels**:
- Slack: #capcat-dev
- Email: dev-team@example.com
- Office hours: Tue/Thu 2-3pm

---

## Quick Command Reference

```bash
# Setup
./scripts/fix_dependencies.sh

# Run Capcat
./capcat fetch hn --count 10

# Tests
pytest
pytest --cov

# Code quality
black .
flake8 core/ sources/

# Documentation
python3 scripts/run_docs.py

# Debug mode
./capcat --debug fetch hn --count 1
```

---

**Last Updated**: 2025-01-06
**Next Review**: Quarterly
**Owner**: Tech Lead
**Status**: Active, living documentation
