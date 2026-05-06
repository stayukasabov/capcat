---
layout: default
render_with_liquid: false
---

# RSS News Sources Reference

Verified RSS/Atom feeds for use with `capcat add-source`.

## Active Built-in Sources

Config-driven sources included out of the box:

| Source | Category |
|--------|----------|
| BBC News | news |
| BBC Sport | sport |
| Google Research | tech |
| The Guardian | news |
| IEEE Spectrum | tech |
| InfoQ | tech |
| Mashable | tech |
| MIT News | science |
| Nature | science |
| Scientific American | science |

## Adding More Sources

```bash
capcat add-source --url <feed-url>
```

Any standard RSS 2.0 or Atom 1.0 feed works. Capcat auto-detects feed format.

## Finding RSS Feeds

Most news sites expose a feed at predictable paths:

- `/feed`
- `/rss`
- `/feed.xml`
- `/rss.xml`
- `/atom.xml`

Browser extensions like "RSS Feed Finder" locate feeds on any page.

## Validated Sources (Not Built-in)

Feeds verified as of late 2025 that work well with Capcat:

**U.S. News**
- NPR: `https://feeds.npr.org/1002/rss.xml`
- AP News: `https://rsshub.app/apnews/topics/apf-topnews`
- Reuters: `https://feeds.reuters.com/reuters/topNews`

**Tech**
- Ars Technica: `https://feeds.arstechnica.com/arstechnica/index`
- The Verge: `https://www.theverge.com/rss/index.xml`
- Wired: `https://www.wired.com/feed/rss`
- TechCrunch: `https://techcrunch.com/feed/`

**Science**
- New Scientist: `https://www.newscientist.com/feed/home/`
- Phys.org: `https://phys.org/rss-feed/`

**Note:** RSS feed URLs change. Verify before adding.
