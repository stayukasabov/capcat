# RSS News Sources Reference - 2025

**Date Created**: October 2, 2025
**Purpose**: Comprehensive reference of major news sources with working RSS feeds for potential integration into Capcat

---

## CNN Replacement Candidates

### U.S. News Sources

#### 1. NPR (National Public Radio)
- **Status**: Verified working (October 2025)
- **Main Feed**: `https://feeds.npr.org/1002/rss.xml`
- **World News**: `https://feeds.npr.org/1004/rss.xml`
- **National News**: `https://feeds.npr.org/1003/rss.xml`
- **Politics**: `https://feeds.npr.org/1014/rss.xml`
- **Quality**: High - Official, well-maintained feeds
- **robots.txt**: Needs verification
- **Notes**: Best CNN replacement candidate

#### 2. The Guardian (US Edition)
- **Status**: Active (45 feeds available, updated Sept 2025)
- **US News**: `https://www.theguardian.com/us-news/rss`
- **US Politics**: `https://www.theguardian.com/us-news/us-politics/rss`
- **World News**: `https://www.theguardian.com/world/rss`
- **UK News**: `https://www.theguardian.com/uk-news/rss`
- **Europe**: `https://www.theguardian.com/world/europe-news/rss`
- **Quality**: High - Comprehensive international coverage
- **robots.txt**: Needs verification
- **Notes**: 45 specialized feeds across all topics

#### 3. Washington Post
- **Status**: Active
- **World News**: `https://feeds.washingtonpost.com/rss/world`
- **National**: `https://feeds.washingtonpost.com/rss/national`
- **Politics**: `https://feeds.washingtonpost.com/rss/politics`
- **Sports**: `https://feeds.washingtonpost.com/rss/sports`
- **Opinions**: `https://feeds.washingtonpost.com/rss/opinions`
- **Quality**: High - Premium journalism
- **robots.txt**: Needs verification
- **Notes**: Requires RSS Terms of Service agreement

#### 4. New York Times
- **Status**: Active (25-30 feeds available, Feb 2025)
- **Main Domain**: `https://rss.nytimes.com/services/xml/...`
- **Sections**: Breaking news, politics, business, science, health, regional
- **Quality**: High - Premium journalism
- **robots.txt**: Needs verification
- **Notes**: May require RSS generator for some sections

#### 5. NBC News
- **Status**: Active
- **Main Feed**: `https://feeds.nbcnews.com/...`
- **Quality**: High - Major U.S. network
- **robots.txt**: Needs verification
- **Notes**: Multiple section feeds available

#### 6. CBS News
- **Status**: Active
- **Main Feed**: `https://www.cbsnews.com/latest/rss/main`
- **Quality**: High - Major U.S. network
- **robots.txt**: Needs verification
- **Notes**: Simple, straightforward feed structure

---

## International News Sources

#### 7. Al Jazeera
- **Status**: Active
- **Main Feed**: `https://www.aljazeera.com/xml/rss/all.xml`
- **Quality**: High - International perspective
- **robots.txt**: Needs verification
- **Notes**: Strong Middle East and international coverage

#### 8. BBC News
- **Status**: Already implemented
- **Main Feed**: `http://feeds.bbci.co.uk/news/rss.xml`
- **Quality**: High - Established and working
- **robots.txt**: Verified compliant
- **Notes**: Currently active in Capcat

---

## Business & Technology News

#### 9. Bloomberg
- **Status**: Active (with limitations)
- **Quality**: High - Financial news focus
- **robots.txt**: Needs verification
- **Notes**: Some feeds may have limited content

#### 10. TechCrunch
- **Status**: Active
- **Main Feed**: `http://feeds.feedburner.com/TechCrunch/`
- **Quality**: High - Tech industry standard
- **robots.txt**: Needs verification
- **Notes**: Comprehensive tech coverage

---

## Previously Evaluated - Not Recommended

### Reuters
- **Status**: Discontinued (June 2020)
- **Notes**: Official RSS feeds discontinued, only third-party workarounds available

### AP News (Associated Press)
- **Status**: Discontinued
- **Notes**: Official RSS feeds discontinued, only third-party generators available

### CNN
- **Status**: Outdated (Last updated April 2023)
- **Notes**: RSS feeds exist but not maintained (2+ years stale content)
- **Moved to**: `sources/inactive/cnn/`

---

## Implementation Priority Recommendations

### Tier 1 - Immediate Implementation (CNN Replacements)
1. **NPR** - Best overall choice, verified working, official feeds
2. **The Guardian** - Comprehensive coverage, 45 feeds, international perspective
3. **Washington Post** - Quality U.S. + world news

### Tier 2 - Secondary Additions
4. **New York Times** - Premium coverage, may need RSS generator
5. **Al Jazeera** - International perspective, Middle East focus

### Tier 3 - Future Consideration
6. **NBC News / CBS News** - Additional U.S. network coverage if needed
7. **TechCrunch** - If expanding tech coverage beyond current sources

---

## Implementation Checklist (For Each Source)

Before adding any new source, verify:

- [ ] **robots.txt compliance** - Check if ClaudeBot or AI bots are allowed
- [ ] **RSS feed validation** - Verify feed is actively updated (check latest entry date)
- [ ] **Content quality** - Test feed returns useful, complete articles
- [ ] **Rate limiting** - Check for Crawl-delay requirements
- [ ] **Terms of Service** - Review any RSS-specific terms
- [ ] **Paywall status** - Ensure no subscription requirements for RSS content
- [ ] **Anti-bot measures** - Verify no aggressive blocking or CAPTCHAs

---

## Guardian Specialized Feeds Reference

The Guardian offers 45+ specialized RSS feeds across categories:

### News Categories
- World, UK, US, Europe, Asia Pacific, Middle East, Africa, Americas, Australia

### Specialized Topics
- Money/Finance: `theguardian.com/uk/business/rss`
- Culture: `theguardian.com/uk/culture/rss`
- Environment: `theguardian.com/uk/environment/rss`
- Film: `theguardian.com/uk/film/rss`
- Fashion: `theguardian.com/fashion/rss`
- Football/Soccer: `theguardian.com/football/rss`

### Feed Pattern
All Guardian feeds follow pattern: `https://www.theguardian.com/[section]/rss`

---

## Notes on RSS Feed Generators

Some sources (NYT, Washington Post) may require third-party RSS generators for certain sections:
- RSS.app
- Newsloth
- IFTTT

**Caution**: Third-party generators may be less reliable than official feeds. Prefer official RSS feeds when available.

---

## Updates Log

- **October 2, 2025**: Initial document created with CNN replacement research
- **Next**: Implementation of Tier 1 sources (NPR, Guardian, Washington Post)
