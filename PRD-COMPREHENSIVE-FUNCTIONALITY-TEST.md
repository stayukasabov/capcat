# PRD: Comprehensive Capcat Functionality Verification

**Status:** DRAFT
**Date:** 2025-12-23
**Priority:** CRITICAL
**Issue:** Documentation describes non-existent or incomplete features

## Problem Statement

Documentation extensively describes features and functions that either:
1. Don't exist in codebase
2. Are incomplete stub implementations
3. Return empty output despite documented behavior

**Evidence:** `cli.py:850-857` - `list_sources_and_bundles()` only prints message, no actual listing logic

## Objective

Verify EVERY feature documented in `docs/` against actual code implementation. Create exhaustive test matrix categorizing features as:
- **WORKING** - Implemented and functional
- **BROKEN** - Stub/incomplete implementation
- **MISSING** - Documented but no code exists

## Feature Categories to Test

### 1. CLI Commands (docs/tutorials/01-cli-commands-exhaustive.md)

#### 1.1 Global Options
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| `--version, -v` | Line 11-16 | cli.py | `./capcat --version` | ? |
| `--verbose, -V` | Line 18-30 | cli.py | `./capcat -V list sources` | ? |
| `--quiet, -q` | Line 32-43 | cli.py | `./capcat -q list sources` | ? |
| `--config, -C FILE` | Line 45-52 | cli.py | `./capcat -C test.yml list sources` | ? |
| `--log-file, -L FILE` | Line 55-67 | cli.py | `./capcat -L test.log list sources` | ? |

#### 1.2 single Command
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Basic URL download | Line 71-100 | capcat.py | `./capcat single https://example.com` | ? |
| `--output, -o DIR` | Line 85-100 | capcat.py | `./capcat single URL -o /tmp/test` | ? |
| `--media, -M` | Line 102-115 | capcat.py | `./capcat single URL --media` | ? |
| `--html, -H` | Line 117-129 | capcat.py | `./capcat single URL --html` | ? |
| `--update, -U` | Line 131-142 | capcat.py | `./capcat single URL --update` | ? |

#### 1.3 fetch Command
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Single source | Line 160-256 | capcat.py | `./capcat fetch hn` | ? |
| Multiple sources | Line 164 | capcat.py | `./capcat fetch hn,bbc` | ? |
| `--count, -c N` | Line 185-195 | capcat.py | `./capcat fetch hn --count 10` | ? |
| `--output, -o DIR` | Line 196-214 | capcat.py | `./capcat fetch hn -o /tmp` | ? |
| `--media, -M` | Line 216-225 | capcat.py | `./capcat fetch hn --media` | ? |
| `--html, -H` | Line 227-235 | capcat.py | `./capcat fetch hn --html` | ? |
| `--update, -U` | Line 237-241 | capcat.py | `./capcat fetch hn --update` | ? |

#### 1.4 bundle Command
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Basic bundle | Line 258-300 | capcat.py | `./capcat bundle tech` | ? |
| `--count, -c N` | Line 283-292 | capcat.py | `./capcat bundle tech --count 10` | ? |
| `--output, -o DIR` | Line 294-299 | capcat.py | `./capcat bundle tech -o /tmp` | ? |
| All predefined bundles | Line 272-279 | bundles.yml | Test each bundle | ? |

#### 1.5 list Command
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| `list sources` | quick-start.md:142 | **cli.py:850** | `./capcat list sources` | **BROKEN** |
| `list bundles` | quick-start.md:146 | cli.py | `./capcat list bundles` | ? |
| `list` (all) | docs/? | cli.py | `./capcat list` | ? |

**CRITICAL BUG FOUND:**
`cli.py:850-857` - Function prints "Listing sources and bundles..." then exits. Comment `# ... (implementation remains the same)` indicates incomplete refactor.

#### 1.6 add-source Command
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Add from RSS | interactive-mode.md:181 | cli.py | `./capcat add-source --url URL` | ? |
| Category selection | interactive-mode.md:189 | cli.py | Verify interactive prompt | ? |
| Bundle addition | interactive-mode.md:191 | cli.py | Verify bundle update | ? |
| Test after add | interactive-mode.md:196 | cli.py | Verify test execution | ? |

#### 1.7 remove-source Command
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Interactive removal | interactive-mode.md:255 | cli.py | `./capcat remove-source` | ? |
| Backup creation | interactive-mode.md:278 | cli.py | Verify `.capcat-backups/` | ? |
| Undo capability | interactive-mode.md:288 | cli.py | `./capcat remove-source --undo` | ? |

#### 1.8 generate-config Command
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Interactive wizard | interactive-mode.md:215 | cli.py | `./capcat generate-config` | ? |
| All config options | interactive-mode.md:224-236 | cli.py | Test full wizard | ? |
| Output creation | interactive-mode.md:238 | cli.py | Verify YAML file | ? |

### 2. Interactive Mode (docs/interactive-mode.md)

#### 2.1 Main Menu
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Launch interactive | Line 7-11 | core/interactive.py | `./capcat catch` | ? |
| Main menu display | Line 15-28 | core/interactive.py | Verify menu appears | ? |
| Arrow key navigation | Line 30-33 | core/interactive.py | Test navigation | ? |

#### 2.2 Bundle Flow
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Bundle selection | Line 40-64 | core/interactive.py | Select bundle | ? |
| HTML prompt | Line 42 | core/interactive.py | Test HTML prompt | ? |
| Execution | Line 43 | core/interactive.py | Verify execution | ? |

#### 2.3 Multi-Source Flow
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Checkbox selection | Line 76-97 | core/interactive.py | Test spacebar | ? |
| Multiple selection | Line 100 | core/interactive.py | Select multiple | ? |
| Execution | Line 81-84 | core/interactive.py | Verify execution | ? |

#### 2.4 Single Source Flow
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Source list | Line 104-122 | core/interactive.py | View list | ? |
| Selection | Line 107 | core/interactive.py | Select source | ? |
| Execution | Line 108 | core/interactive.py | Verify execution | ? |

#### 2.5 Single URL Flow
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| URL input | Line 128-145 | core/interactive.py | Enter URL | ? |
| HTML prompt | Line 141 | core/interactive.py | Test prompt | ? |
| Execution | Line 134 | core/interactive.py | Verify download | ? |

#### 2.6 Source Management Submenu
| Feature | Doc Reference | Code Location | Test Command | Status |
|---------|---------------|---------------|--------------|--------|
| Submenu display | Line 163-178 | core/interactive.py | Verify menu | ? |
| Add RSS source | Line 181-207 | core/interactive.py | Test flow | ? |
| Generate config | Line 215-242 | core/interactive.py | Test wizard | ? |
| Remove sources | Line 255-290 | core/interactive.py | Test removal | ? |
| List sources | Line 292-331 | core/interactive.py | **Test output format** | ? |
| Test source | Line 333-366 | core/interactive.py | Test functionality | ? |

### 3. Architecture Components (docs/architecture.md)

#### 3.1 Source Registry
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| Auto-discovery | Line 99-116 | core/source_system/source_registry.py | Verify discovery | ? |
| Source count | Line 106 | registry | Verify 20+ sources | ? |
| Validation | Line 114 | registry | Test validation | ? |

#### 3.2 Factory Pattern
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| Source creation | Line 118-134 | core/source_system/source_factory.py | Test creation | ? |
| Performance monitoring | Line 127 | factory | Verify metrics | ? |
| Session pool | Line 134 | factory | Test pooling | ? |

#### 3.3 Performance Monitoring
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| SourceMetrics | Line 136-158 | core/source_system/performance_monitor.py | Test metrics | ? |
| Success rate | Line 151 | monitor | Verify calculation | ? |
| Response time | Line 146 | monitor | Test tracking | ? |

#### 3.4 Validation Engine
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| Basic validation | Line 160-174 | core/source_system/validation_engine.py | Test syntax | ? |
| Network validation | Line 166 | validator | Test connectivity | ? |
| Selector validation | Line 167 | validator | Test CSS selectors | ? |
| Deep validation | Line 168 | validator | Test live content | ? |

#### 3.5 Session Pooling
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| Global session | Line 236-253 | core/session_pool.py | Verify singleton | ? |
| Connection pool | Line 241-242 | session_pool | Test pool size | ? |
| Reuse | Line 249 | session_pool | Verify reuse | ? |

#### 3.6 Unified Media Processing
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| MediaEmbeddingProcessor | Line 349-372 | core/media_embedding_processor.py | Test integration | ? |
| MediaConfigManager | Line 374-392 | core/media_config.py | Test configs | ? |
| URL processing | Line 402-407 | processor | Test strategies | ? |
| Markdown integration | Line 409-413 | processor | Test replacement | ? |

#### 3.7 Template System
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| Template variants | Line 580-605 | templates/ | Verify files | ? |
| Navigation logic | Line 607-612 | html_generator.py | Test logic | ? |
| Source detection | Line 614-618 | html_generator.py | Test patterns | ? |

#### 3.8 Simple Protection System
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| Aggregator detection | Line 463-505 | core/simple_protection.py | Test detection | ? |
| Image filtering | Line 491-495 | simple_protection | Test filters | ? |
| --media flag | Line 517-534 | simple_protection | Test flag | ? |

#### 3.9 HTML Generation
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| Factory pattern | Line 686-710 | core/html_generator.py | Test factory | ? |
| Config-driven | Line 712-732 | htmlgen/*/config.yaml | Test configs | ? |
| Template override | Line 734-738 | htmlgen/*/templates/ | Test overrides | ? |
| Comment processing | Line 740-745 | generator | Test privacy | ? |

### 4. Source Development (docs/source-development.md)

#### 4.1 Config-Driven Sources
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| YAML creation | Line 65-137 | sources/active/config_driven/configs/ | Create test source | ? |
| RSS config | Line 77-81 | config.yaml | Test RSS extraction | ? |
| Article selectors | Line 84-87 | config.yaml | Test discovery | ? |
| Content selectors | Line 90-94 | config.yaml | Test extraction | ? |
| Image processing | Line 106-130 | config.yaml | Test download | ? |

#### 4.2 Custom Sources
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| Directory structure | Line 203-212 | sources/active/custom/ | Verify structure | ? |
| BaseSource | Line 226-388 | source.py | Test implementation | ? |
| get_articles() | Line 239-285 | source.py | Test method | ? |
| get_article_content() | Line 287-314 | source.py | Test method | ? |
| get_comments() | Line 316-353 | source.py | Test method | ? |

#### 4.3 Template Integration
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| Template config | Line 159-175 | config.yaml | Test integration | ? |
| Variants | Line 177-182 | config.yaml | Test selection | ? |
| Navigation | Line 184-188 | config.yaml | Test links | ? |

### 5. Testing Framework (docs/testing.md - if exists)

#### 5.1 Test Scripts
| Feature | Expected Location | Test Command | Status |
|---------|-------------------|--------------|--------|
| Comprehensive source test | test_comprehensive_sources.py | `python test_comprehensive_sources.py` | ? |
| Validation engine test | test_validation_engine.py | `python test_validation_engine.py` | ? |
| Performance monitor test | test_performance_monitor.py | `python test_performance_monitor.py` | ? |
| Source management test | tests/test_source_management_menu.py | `python -m pytest tests/` | ? |

### 6. Configuration System (docs/configuration.md - if exists)

#### 6.1 Config Priority
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| CLI args priority | architecture.md:556 | core/config.py | Test override | ? |
| ENV vars | architecture.md:557 | core/config.py | Test ENV | ? |
| capcat.yml | architecture.md:558 | core/config.py | Test file | ? |
| Defaults | architecture.md:559 | core/config.py | Test defaults | ? |

#### 6.2 Config File
| Feature | Doc Reference | Code Location | Test | Status |
|---------|---------------|---------------|------|--------|
| Network config | architecture.md:564-568 | capcat.yml | Verify settings | ? |
| Processing config | architecture.md:570-573 | capcat.yml | Verify settings | ? |
| Logging config | architecture.md:575-577 | capcat.yml | Verify settings | ? |

## Testing Methodology

### Phase 1: Quick Smoke Tests (Priority: HIGH)
Test documented CLI commands to identify broken/stub functions:

```bash
# Test list commands (KNOWN BROKEN)
./capcat list sources          # FAIL: Only prints message
./capcat list bundles          # Status unknown
./capcat list                  # Status unknown

# Test basic commands
./capcat --version             # Expected: version output
./capcat --help                # Expected: help text

# Test single command
./capcat single https://news.ycombinator.com

# Test fetch command
./capcat fetch hn --count 3

# Test bundle command
./capcat bundle tech --count 3

# Test interactive mode
./capcat catch
```

### Phase 2: Feature Matrix Testing (Priority: MEDIUM)
Systematically test each table entry above:
1. Execute test command
2. Verify expected output matches documentation
3. Mark status: WORKING / BROKEN / MISSING
4. Document actual behavior if different

### Phase 3: Integration Testing (Priority: MEDIUM)
Test complex workflows:
1. Add source → List → Test → Remove
2. Bundle fetch → HTML generation → Verification
3. CLI args priority testing
4. Error handling verification

### Phase 4: Documentation Audit (Priority: LOW)
For each BROKEN/MISSING feature:
1. Determine if feature should exist
2. Update docs to match reality OR
3. Create implementation ticket

## Test Output Format

```markdown
### Test Results: [Feature Category]

| Feature | Test Command | Expected | Actual | Status |
|---------|--------------|----------|--------|--------|
| list sources | `./capcat list sources` | Categorized source list | "Listing sources and bundles..." | **BROKEN** |
| ... | ... | ... | ... | ... |

#### Discrepancies

**Feature: list sources**
- **Doc Claims:** docs/quick-start.md:142-147 - Outputs categorized source list
- **Code Reality:** cli.py:850-857 - Stub function, prints message only
- **Impact:** HIGH - Core discovery feature non-functional
- **Recommendation:** Implement function or remove from docs
```

## Acceptance Criteria

1. ✓ All table entries tested and marked with status
2. ✓ Critical path workflows functional (single, fetch, bundle, catch)
3. ✓ Documentation updated to reflect reality
4. ✓ Broken features either fixed or documented as unavailable
5. ✓ Test results published in `TEST-RESULTS-COMPREHENSIVE.md`

## Timeline

- Phase 1 (Smoke Tests): 1 hour
- Phase 2 (Feature Matrix): 4-6 hours
- Phase 3 (Integration): 2-3 hours
- Phase 4 (Documentation Audit): 2-3 hours
- **Total:** 9-13 hours

## Deliverables

1. **TEST-RESULTS-COMPREHENSIVE.md** - Complete test results matrix
2. **BUGS-CRITICAL.md** - List of broken critical features
3. **BUGS-MINOR.md** - List of broken non-critical features
4. **DOCS-FIXES.md** - Required documentation updates
5. **IMPLEMENTATION-BACKLOG.md** - Features to implement

## Known Issues (Pre-Test)

1. **cli.py:850** - `list_sources_and_bundles()` incomplete
   - Impact: HIGH
   - User-facing: YES
   - Documented: YES (multiple locations)

2. **Potential suspects** (require testing):
   - Interactive mode completeness
   - Source management flows
   - HTML generation
   - Template system integration
   - Validation engine functionality

## Success Metrics

- **Critical Features Working:** >95%
- **Documented Features Implemented:** >90%
- **Test Coverage:** 100% of documented features
- **Documentation Accuracy:** 100% alignment with code

## Risk Assessment

**Risk: Extensive documentation inaccuracy**
- Likelihood: HIGH (confirmed 1 critical bug, suspect many more)
- Impact: HIGH (user trust, functionality discovery)
- Mitigation: Comprehensive testing, honest documentation updates

---

**Next Steps:**
1. Execute Phase 1 smoke tests
2. Document all broken features
3. Prioritize fixes based on user impact
4. Update documentation for unfixable items
