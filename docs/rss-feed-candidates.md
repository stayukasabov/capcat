# RSS Feed Candidates for Testing

Feeds not currently in capcat sources, verified against robots.txt on 2026-03-24.

## Clean — No robots.txt Barriers

| # | Source | RSS URL | Category | Notes |
|---|--------|---------|----------|-------|
| 1 | TechCrunch | `https://techcrunch.com/feed/` | Tech news | 20 items, summaries |
| 2 | VentureBeat | `https://venturebeat.com/feed/` | AI/Tech | 7–8 items, AI/enterprise focus |
| 3 | MIT Technology Review | `https://www.technologyreview.com/feed/` | AI/Tech | Full article content in feed |
| 4 | OpenAI News | `https://openai.com/news/rss.xml` | AI | 200+ items, very active |
| 5 | Google DeepMind | `https://deepmind.google/blog/rss.xml` | AI research | 150 items, well-maintained |
| 6 | Hugging Face Blog | `https://huggingface.co/blog/feed.xml` | AI/ML | 500+ items, high volume |
| 7 | Simon Willison's Weblog | `https://simonwillison.net/atom/everything/` | AI commentary | Highly respected dev/AI blog |
| 8 | Phys.org | `https://phys.org/rss-feed/` | Science | 30 items, broad science coverage |
| 9 | ScienceDaily | `https://www.sciencedaily.com/rss/all.xml` | Science | 50 items, reliable research news |
| 10 | WSJ World News | `https://feeds.a.dj.com/rss/RSSWorldNews.xml` | World news | Free headlines/summaries, articles paywalled |

## Test Manually

Unreachable from automated check (CDN blocks) but expected to work:

| Source | RSS URL | Category |
|--------|---------|----------|
| The Verge | `https://www.theverge.com/rss/index.xml` | Tech |
| Wired | `https://www.wired.com/feed/rss` | Tech |
| Ars Technica | `https://arstechnica.com/feed/` | Tech |
| Deutsche Welle | `https://rss.dw.com/rss/engl` | World news |

## arXiv (Academic Papers — PDF Downloads)

Crawl-delay: 15s required. `/abs` and `/pdf` paths are allowed.

| # | Source | RSS URL | Category |
|---|--------|---------|----------|
| 1 | arXiv AI | `http://export.arxiv.org/rss/cs.AI` | Artificial Intelligence |
| 2 | arXiv ML | `http://export.arxiv.org/rss/cs.LG` | Machine Learning |
| 3 | arXiv CS | `http://export.arxiv.org/rss/cs` | All Computer Science |
| 4 | arXiv Physics | `http://export.arxiv.org/rss/physics` | Physics |
| 5 | arXiv Math | `http://export.arxiv.org/rss/math` | Mathematics |

## Avoid — robots.txt Blocks AI/Bot Crawlers

| Source | Reason |
|--------|--------|
| Al Jazeera | Explicitly blocks `anthropic-ai`, `ClaudeBot` with `Disallow: /` |
| NPR News | Explicitly blocks Anthropic and major AI crawlers with `Disallow: /` |
| Bloomberg Technology | Blocks feed aggregators (Feedly, etc.) and AI crawlers |
