# Team Onboarding Guide

## Welcome to Capcat Development

This comprehensive guide will help new developers and product designers understand Capcat, contribute effectively, and integrate with the team.

---

## Day 1: Environment Setup

### Prerequisites Checklist

Before starting, ensure you have:

```
[ ] Python 3.8+ installed
[ ] Git configured with your credentials
[ ] GitHub account with repo access
[ ] Code editor (VS Code, PyCharm, etc.)
[ ] Terminal/command line proficiency
[ ] Basic understanding of Python
[ ] Familiarity with web scraping concepts
```

### Development Environment Setup

#### Step 1: Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd capcat

# Check out develop branch
git checkout develop

# Create your feature branch
git checkout -b feature/your-name-onboarding
```

#### Step 2: Install Dependencies

```bash
# Automated setup (recommended)
./scripts/fix_dependencies.sh

# Manual setup (if automated fails)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools
```

#### Step 3: Verify Installation

```bash
# Test basic functionality
./capcat list sources

# Run test suite
pytest

# Check code quality
flake8 core/ sources/
black --check .
```

#### Step 4: Configure IDE

**VS Code Configuration** (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true,
  "editor.rulers": [79],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true
  }
}
```

**PyCharm Configuration**:
1. Open Project Settings
2. Python Interpreter → Select venv
3. Tools → Black → Enable format on save
4. Tools → Python Integrated Tools → Set pytest as test runner

---

## Day 1-2: Codebase Exploration

### Recommended Reading Order

1. **Start Here**:
   - `README.md` - Project overview
   - `docs/quick-start.md` - Basic usage
   - `docs/tutorials/user/01-getting-started.md` - First steps

2. **Architecture Understanding**:
   - `docs/architecture.md` - System design
   - `docs/development/01-architecture-logic.md` - Technical details
   - `docs/architecture/components.md` - Component breakdown

3. **Development Practices**:
   - `docs/source-development.md` - Adding sources
   - `docs/testing.md` - Testing strategy
   - `docs/ethical-scraping.md` - Scraping guidelines

### Hands-On Exercises

#### Exercise 1: Run Capcat (10 minutes)

```bash
# Basic fetch command
./capcat fetch hn --count 5

# Check output
cd ../News/news_$(date +%d-%m-%Y)/
ls -la
cat HackerNews_*/01_*/article.md

# Try interactive mode
./capcat catch
```

**Learning Goals**:
- Understand basic CLI usage
- See output structure
- Experience user perspective

#### Exercise 2: Trace Code Flow (30 minutes)

Add print statements to trace execution:

```python
# In capcat.py, add at start of main():
print("DEBUG: Starting main()")

# In cli.py, in parse_arguments():
print(f"DEBUG: Command: {args.command}")

# In source_registry.py, in discover_sources():
print(f"DEBUG: Found {len(sources)} sources")

# Run and observe output
./capcat fetch hn --count 1 2>&1 | grep DEBUG
```

**Learning Goals**:
- Understand execution flow
- Identify key components
- Learn debugging techniques

#### Exercise 3: Read Source Code (45 minutes)

Pick one source and understand it completely:

```bash
# Choose a simple config-driven source
cat sources/active/config_driven/configs/iq.yaml

# Or a complex custom source
cat sources/active/custom/hn/source.py
```

**Learning Goals**:
- Understand source types
- See config vs custom patterns
- Learn scraping techniques

#### Exercise 4: Run Tests (15 minutes)

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_source_registry.py

# Run with coverage
pytest --cov=core --cov=sources

# Run with verbose output
pytest -v tests/test_source_registry.py::TestSourceRegistry::test_discover_sources
```

**Learning Goals**:
- Understand test structure
- See what's tested
- Learn testing patterns

---

## Day 3-4: First Contribution

### Small Tasks for Beginners

#### Task 1: Fix Documentation Typo

```bash
# Find typos in docs
grep -r "teh\|taht\|adn" docs/

# Fix typo
sed -i 's/teh/the/g' docs/architecture.md

# Commit
git add docs/architecture.md
git commit -m "docs: fix typo in architecture.md"
git push origin feature/your-name-onboarding
```

#### Task 2: Add Config-Driven Source

Create a new simple source (estimated time: 30 minutes):

```yaml
# sources/active/config_driven/configs/testsource.yaml
display_name: "Test Source"
base_url: "https://example.com/news/"
category: test

article_selectors:
  - .headline a
  - article h2 a

content_selectors:
  - .article-body
  - article .content

max_articles: 20
```

Test your source:
```bash
# Verify it's discovered
./capcat list sources | grep testsource

# Test fetching
./capcat fetch testsource --count 5
```

#### Task 3: Improve Error Message

Find an unclear error message and improve it:

```python
# Before (unclear)
raise ValueError("Invalid config")

# After (helpful)
raise ValidationError(
    "Invalid source configuration",
    details=f"Missing required field: {missing_field}",
    suggestion=f"Add '{missing_field}' to config file",
    example=f"{missing_field}: value_here"
)
```

---

## Week 1: Deep Dive Sessions

### Architecture Deep Dive (2 hours)

**Session Goals**:
- Understand hybrid architecture
- Learn source registry pattern
- Understand processing pipeline

**Activities**:
1. Draw architecture diagram from memory
2. Explain data flow for article fetching
3. Identify design patterns used
4. Discuss architectural decisions

**Homework**:
- Read: `docs/development/01-architecture-logic.md`
- Exercise: Add a new extraction strategy
- Question: Why hybrid architecture vs. single approach?

### User Interface Deep Dive (1.5 hours)

**Session Goals**:
- Understand user workflows
- Learn design principles
- Experience interactive mode

**Activities**:
1. Test interactive mode workflows
2. Complete user journey exercises
3. Review usability principles
4. Identify interface improvements

**Homework**:
- Read: Interactive mode documentation
- Exercise: Observe someone using Capcat
- Question: Which persona are you most like?

### Testing Deep Dive (1 hour)

**Session Goals**:
- Understand testing strategy
- Write effective tests
- Use testing tools

**Activities**:
1. Write unit test for utility function
2. Write integration test for source
3. Run test coverage report
4. Fix failing test

**Homework**:
- Read: `docs/testing.md`
- Exercise: Achieve 90% coverage on new module
- Question: What's hard to test and why?

---

## Week 2: Collaboration Practices

### Code Review Guidelines

#### Submitting Code for Review

1. **Create Pull Request**:
```bash
# Ensure branch is up to date
git checkout develop
git pull origin develop
git checkout feature/your-feature
git rebase develop

# Push to GitHub
git push origin feature/your-feature

# Create PR via GitHub UI
```

2. **PR Description Template**:
```markdown
## What does this PR do?
Brief description of changes

## Why is this needed?
Problem being solved or feature being added

## How was this tested?
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing performed
- [ ] Documentation updated

## Checklist
- [ ] Code follows PEP 8
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Screenshots (if UI changes)
[Attach screenshots]

## Related Issues
Fixes #123
```

3. **Respond to Feedback**:
```bash
# Make requested changes
[edit files]

# Commit changes
git add .
git commit -m "review: address feedback on error handling"

# Push updates
git push origin feature/your-feature
```

#### Reviewing Code from Others

**Review Checklist**:

```
Code Quality:
[ ] Follows PEP 8 style guide
[ ] No code duplication
[ ] Functions are single-purpose
[ ] Variable names are descriptive
[ ] Comments explain "why" not "what"

Functionality:
[ ] Solves stated problem
[ ] Edge cases handled
[ ] Error handling present
[ ] No obvious bugs

Testing:
[ ] Tests included
[ ] Tests cover edge cases
[ ] Tests pass locally

Documentation:
[ ] Docstrings present
[ ] README updated if needed
[ ] Breaking changes documented

Security:
[ ] No hardcoded secrets
[ ] Input validation present
[ ] No SQL injection risks
[ ] No XSS vulnerabilities
```

**Review Comment Templates**:

```markdown
# Suggestion
Consider extracting this logic into a separate function for reusability.

# Question
Why did you choose approach A over approach B?

# Nitpick (optional fix)
Minor: This could be a list comprehension for readability

# Blocking (must fix)
This introduces a security vulnerability: [explain]

# Praise
Nice solution! This is much cleaner than the previous approach.
```

### Git Workflow

#### Branch Naming Convention

```
feature/short-description    # New features
bugfix/issue-number          # Bug fixes
docs/what-documenting        # Documentation
refactor/what-refactoring    # Code refactoring
test/what-testing            # Test additions
```

#### Commit Message Format

```
type: short description (max 50 chars)

Longer description if needed (wrap at 72 chars).
Explain what and why, not how.

Fixes #123
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples**:
```bash
git commit -m "feat: add RSS feed introspection for auto-config"

git commit -m "fix: handle timeout errors in article fetcher

Previously, timeout errors would crash the entire batch.
Now individual article failures are logged and processing continues.

Fixes #234"

git commit -m "docs: add user journey map for researcher persona"
```

### Communication Practices

#### Daily Standups (Async)

Post in team chat:
```
Yesterday: Completed source addition feature
Today: Working on error handling improvements
Blockers: Need review on PR #456
```

#### Weekly Planning

1. Review sprint goals
2. Assign tasks
3. Identify dependencies
4. Schedule pair programming

#### Documentation Updates

**When to Update Docs**:
- Adding new feature → Update relevant guide
- Fixing bug → Add to troubleshooting
- Changing API → Update API reference
- Learning something non-obvious → Add to docs

**Where to Document**:
- Architecture changes → `docs/architecture.md`
- New features → `docs/`
- Bug fixes → Changelog
- HOWTOs → `docs/developer/`

---

## Development Workflows

### Adding a New Config-Driven Source

**Time Estimate**: 15-30 minutes

```bash
# Step 1: Create YAML config
cat > sources/active/config_driven/configs/newsource.yaml <<'EOF'
display_name: "New Source"
base_url: "https://newsource.com/articles/"
category: tech

article_selectors:
  - .article-title a
  - h2.headline a

content_selectors:
  - article .content
  - .article-body

image_selectors:
  - article img
  - .featured-image img

max_articles: 30
timeout: 30
EOF

# Step 2: Test discovery
./capcat list sources | grep newsource

# Step 3: Test fetching
./capcat fetch newsource --count 5 --debug

# Step 4: Verify output
ls -la ../News/news_$(date +%d-%m-%Y)/NewsSource_*/

# Step 5: Add to bundle (optional)
echo "    - newsource" >> sources/active/bundles.yml

# Step 6: Commit
git add sources/active/config_driven/configs/newsource.yaml
git commit -m "feat: add NewsSource config-driven source"
```

### Adding a New Custom Source

**Time Estimate**: 2-4 hours

```bash
# Step 1: Create source directory structure
mkdir -p sources/active/custom/newsource
cd sources/active/custom/newsource

# Step 2: Create source.py
cat > source.py <<'EOF'
from core.source_system.base_source import BaseSource, Article
from typing import List

class NewSource(BaseSource):
    """
    Custom source implementation for NewsSource.com
    """

    def __init__(self, config, session=None):
        super().__init__(config, session)
        self.api_base = "https://api.newsource.com/v1"

    def get_articles(self, count=30) -> List[Article]:
        """
        Fetch articles from NewsSource

        Args:
            count: Number of articles to fetch

        Returns:
            List of Article objects
        """
        articles = []

        # Implement fetching logic
        # ...

        return articles
EOF

# Step 3: Create config.yaml
cat > config.yaml <<'EOF'
display_name: "New Source"
source_id: newsource
source_type: custom
category: tech
has_comments: false
EOF

# Step 4: Create __init__.py
touch __init__.py

# Step 5: Test source
cd ../../../../  # Back to project root
./capcat fetch newsource --count 5

# Step 6: Write tests
cat > tests/test_newsource.py <<'EOF'
import pytest
from sources.active.custom.newsource.source import NewSource

def test_newsource_initialization():
    source = NewSource(config, session=None)
    assert source.id == 'newsource'

def test_newsource_fetch_articles():
    source = NewSource(config, session=None)
    articles = source.get_articles(count=5)
    assert len(articles) == 5
EOF

# Step 7: Run tests
pytest tests/test_newsource.py

# Step 8: Commit
git add sources/active/custom/newsource/
git add tests/test_newsource.py
git commit -m "feat: add custom NewsSource implementation"
```

### Fixing a Bug

**Workflow**:

```bash
# Step 1: Reproduce the bug
./capcat fetch hn --count 10  # Error occurs

# Step 2: Write failing test
cat > tests/test_bugfix.py <<'EOF'
def test_error_handling_in_fetch():
    # This should not raise exception
    source.fetch_article("invalid-url")
    # Should log error and continue
EOF

# Step 3: Run test to confirm failure
pytest tests/test_bugfix.py  # FAILS

# Step 4: Fix the bug
# Edit relevant file

# Step 5: Run test to confirm fix
pytest tests/test_bugfix.py  # PASSES

# Step 6: Run full test suite
pytest

# Step 7: Manual verification
./capcat fetch hn --count 10  # No error

# Step 8: Commit
git add [changed files]
git commit -m "fix: handle invalid URLs in article fetcher

Previously, invalid URLs would crash the entire batch.
Now individual failures are logged and processing continues.

Fixes #234"
```

---

## Common Tasks

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_source_registry.py

# Specific test function
pytest tests/test_source_registry.py::test_discover_sources

# With coverage
pytest --cov=core --cov=sources --cov-report=html

# With verbose output
pytest -v

# Stop on first failure
pytest -x

# Run only failed tests
pytest --lf
```

### Code Quality Checks

```bash
# Format code with Black
black .

# Check formatting (don't modify)
black --check .

# Lint with flake8
flake8 core/ sources/ capcat.py cli.py

# Type checking with mypy
mypy core/ sources/

# Security audit
bandit -r core/ sources/

# All checks (CI simulation)
./scripts/run_checks.sh
```

### Documentation Generation

```bash
# Generate all documentation
python3 scripts/run_docs.py

# Generate API docs only
python3 scripts/doc_generator.py

# Generate diagrams
python3 scripts/generate_diagrams.py

# Generate user guides
python3 scripts/generate_user_guides.py

# View generated docs
open docs/index.md
```

---

## Debugging Tips

### Common Issues and Solutions

#### Issue: ModuleNotFoundError

```bash
# Problem: Module not found when running tests
ModuleNotFoundError: No module named 'core'

# Solution 1: Activate venv
source venv/bin/activate

# Solution 2: Install in editable mode
pip install -e .

# Solution 3: Add to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

#### Issue: Test Failures

```bash
# Problem: Tests fail unexpectedly
================================ FAILURES =================================

# Solution 1: Check test isolation
pytest --verbose -x  # Stop on first failure

# Solution 2: Clear pytest cache
rm -rf .pytest_cache
pytest --cache-clear

# Solution 3: Run single test with print statements
pytest -s tests/test_file.py::test_function
```

#### Issue: Import Errors in Sources

```bash
# Problem: Source not discovered by registry
./capcat list sources  # Source not in list

# Solution 1: Check file structure
ls -la sources/active/custom/yoursource/
# Must have: __init__.py, source.py, config.yaml

# Solution 2: Validate config
python3 -c "import yaml; yaml.safe_load(open('sources/active/custom/yoursource/config.yaml'))"

# Solution 3: Check Python syntax
python3 -m py_compile sources/active/custom/yoursource/source.py
```

### Debugging Techniques

#### Technique 1: Add Debug Logging

```python
import logging
logger = logging.getLogger(__name__)

def problematic_function():
    logger.debug(f"Input: {input_value}")
    result = do_something(input_value)
    logger.debug(f"Result: {result}")
    return result

# Run with debug flag
./capcat --debug fetch hn --count 1
```

#### Technique 2: Use Python Debugger

```python
def problematic_function():
    import pdb; pdb.set_trace()  # Breakpoint
    result = do_something()
    return result

# When breakpoint hits:
# (Pdb) print(variable)
# (Pdb) step  # Step into function
# (Pdb) next  # Next line
# (Pdb) continue  # Continue execution
```

#### Technique 3: Interactive Testing

```bash
# Start Python REPL
python3

>>> from sources.active.custom.hn.source import HackerNewsSource
>>> from core.source_system.source_registry import get_source_registry
>>> registry = get_source_registry()
>>> source = registry.get_source('hn')
>>> articles = source.get_articles(count=1)
>>> print(articles[0].title)
```

---

## Resources

### Internal Resources

- **Documentation**: `docs/` directory
- **Architecture diagrams**: `docs/diagrams/`
- **API reference**: `docs/api/`
- **Testing guide**: `docs/testing.md`
- **Code examples**: `examples/` directory

### External Resources

**Python**:
- [Python Documentation](https://docs.python.org/3/)
- [Real Python Tutorials](https://realpython.com/)
- [PEP 8 Style Guide](https://pep8.org/)

**Web Scraping**:
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Documentation](https://requests.readthedocs.io/)
- [Scrapy Tutorial](https://docs.scrapy.org/en/latest/intro/tutorial.html)

**Testing**:
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://realpython.com/pytest-python-testing/)

### Team Contacts

- **Product Owner**: [Name]
- **Tech Lead**: [Name]
- **DevOps**: [Name]

---

## Success Checklist

### End of Week 1

```
[ ] Environment setup complete
[ ] Capcat runs successfully
[ ] Can fetch articles from all sources
[ ] Read all required documentation
[ ] Completed hands-on exercises
[ ] Attended all deep dive sessions
[ ] Created first pull request
```

### End of Week 2

```
[ ] First PR merged
[ ] Added or fixed a source
[ ] Wrote tests with >80% coverage
[ ] Participated in code review
[ ] Updated documentation
[ ] Comfortable with git workflow
[ ] Understand architecture completely
```

### End of Month 1

```
[ ] Independently added new feature
[ ] Led code review for others
[ ] Improved documentation
[ ] Solved complex bug
[ ] Contributed to architecture decisions
[ ] Mentored new team member
```

---

## Next Steps

After completing this onboarding:

1. **Choose Specialization**:
   - Source development
   - Core architecture
   - Testing infrastructure
   - Documentation
   - DevOps/deployment

2. **Take Ownership**:
   - Become expert in specific component
   - Lead feature development
   - Improve testing coverage
   - Enhance documentation

3. **Contribute to Community**:
   - Answer issues on GitHub
   - Write blog posts
   - Create tutorials
   - Speak at meetups

---

**Document Status**: Living document
**Last Updated**: 2025-01-06
**Owner**: Tech Lead
**Feedback**: Submit improvements via PR
