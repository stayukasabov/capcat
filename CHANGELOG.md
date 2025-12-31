# Changelog

All notable changes to Capcat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-31

Version 2.0 represents a complete architectural rewrite with enhanced functionality and improved user experience.

### Added

**Core Features:**
- Unified article processor for consistent handling across all sources
- Specialized source handlers for Twitter, YouTube, Medium, Substack
- Fallback image detection system with intelligent filtering
- Interactive mode with guided workflows (`./capcat catch`)
- Bundle system for topical collections (tech, techpro, news, science, ai, sports)
- HTML generation with professional themes
- Session pooling for improved network performance
- Parallel processing with up to 8 concurrent workers

**Sources (12 total):**
- AI: google-reserch, mitnews
- News: bbc, guardian
- Science: nature, scientificamerican
- Sports: bbcsport
- Tech: ieee, mashable
- TechPro: hn (Hacker News), iq (InfoQ), lb (Lobsters)

**Architecture:**
- Plugin-based architecture with config-driven and custom source support
- Source registry with auto-discovery
- Unified media processor with configurable handling
- Circuit breaker pattern for network resilience
- Rate limiting and ethical scraping compliance
- Comprehensive error handling and recovery

**User Experience:**
- Privacy compliance with username anonymization
- Profile link preservation for attribution
- Media handling: images always downloaded, video/audio/docs with --media flag
- Professional HTML templates with consistent navigation
- Structured folder hierarchy with date-based organization
- Cross-platform compatibility (Windows, macOS, Linux)

**Documentation:**
- Complete documentation website (website/)
- Quick start guide
- Architecture documentation
- API reference
- Tutorial system
- Interactive mode guide

### Changed

- Complete rewrite from v1.x limited functionality
- Improved command-line interface with better argument handling
- Enhanced source management system
- Separated article and comment workflows for better reliability
- Updated privacy policy with comprehensive user anonymization

### Fixed

- BUG-001: list command now properly displays sources grouped by category
- BUG-002: Removed unimplemented config command
- Improved error handling across all modules
- Enhanced network resilience with retry logic

### Removed

- config command (use capcat.yml file instead)
- Legacy fetchhni and fetchlb separate tools (unified into capcat)

### Technical Details

**Tech Stack:**
- Python 3.8+ required
- Requests, BeautifulSoup4, lxml, Pillow
- YAML configuration
- Session pooling
- PEP 8 compliant codebase

**Performance:**
- 94.6% code reduction through hybrid architecture
- Concurrent processing for improved speed
- Efficient media handling with duplicate prevention
- Smart caching with fallback strategies

**Security:**
- No personal data collection
- robots.txt compliance
- Rate limiting (1 request per 10 seconds)
- No paywall circumvention
- Ethical scraping practices

---

## [1.x] - Historical

Limited functionality version with basic Hacker News and Lobsters support.

### Features
- Basic article fetching from Hacker News
- Basic article fetching from Lobsters
- Simple markdown conversion
- Basic comment extraction

---

[2.0.0]: https://github.com/stayukasabov/capcat/releases/tag/v2.0.0
