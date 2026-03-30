# RSS Feed Candidates for Testing

Feeds not currently in capcat sources, verified against robots.txt on 2026-03-24.

## Clean — No robots.txt Barriers

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Source</th>
      <th>RSS URL</th>
      <th>Category</th>
      <th>Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>TechCrunch</td>
      <td><code>https://techcrunch.com/feed/</code></td>
      <td>Tech news</td>
      <td>20 items, summaries</td>
    </tr>
    <tr>
      <td>2</td>
      <td>VentureBeat</td>
      <td><code>https://venturebeat.com/feed/</code></td>
      <td>AI/Tech</td>
      <td>7–8 items, AI/enterprise focus</td>
    </tr>
    <tr>
      <td>3</td>
      <td>MIT Technology Review</td>
      <td><code>https://www.technologyreview.com/feed/</code></td>
      <td>AI/Tech</td>
      <td>Full article content in feed</td>
    </tr>
    <tr>
      <td>4</td>
      <td>OpenAI News</td>
      <td><code>https://openai.com/news/rss.xml</code></td>
      <td>AI</td>
      <td>200+ items, very active</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Google DeepMind</td>
      <td><code>https://deepmind.google/blog/rss.xml</code></td>
      <td>AI research</td>
      <td>150 items, well-maintained</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Hugging Face Blog</td>
      <td><code>https://huggingface.co/blog/feed.xml</code></td>
      <td>AI/ML</td>
      <td>500+ items, high volume</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Simon Willison's Weblog</td>
      <td><code>https://simonwillison.net/atom/everything/</code></td>
      <td>AI commentary</td>
      <td>Highly respected dev/AI blog</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Phys.org</td>
      <td><code>https://phys.org/rss-feed/</code></td>
      <td>Science</td>
      <td>30 items, broad science coverage</td>
    </tr>
    <tr>
      <td>9</td>
      <td>ScienceDaily</td>
      <td><code>https://www.sciencedaily.com/rss/all.xml</code></td>
      <td>Science</td>
      <td>50 items, reliable research news</td>
    </tr>
    <tr>
      <td>10</td>
      <td>WSJ World News</td>
      <td><code>https://feeds.a.dj.com/rss/RSSWorldNews.xml</code></td>
      <td>World news</td>
      <td>Free headlines/summaries, articles paywalled</td>
    </tr>
  </tbody>
</table>
</div>

## Test Manually

Unreachable from automated check (CDN blocks) but expected to work:

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Source</th>
      <th>RSS URL</th>
      <th>Category</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>The Verge</td>
      <td><code>https://www.theverge.com/rss/index.xml</code></td>
      <td>Tech</td>
    </tr>
    <tr>
      <td>Wired</td>
      <td><code>https://www.wired.com/feed/rss</code></td>
      <td>Tech</td>
    </tr>
    <tr>
      <td>Ars Technica</td>
      <td><code>https://arstechnica.com/feed/</code></td>
      <td>Tech</td>
    </tr>
    <tr>
      <td>Deutsche Welle</td>
      <td><code>https://rss.dw.com/rss/engl</code></td>
      <td>World news</td>
    </tr>
  </tbody>
</table>
</div>

## arXiv (Academic Papers — PDF Downloads)

Crawl-delay: 15s required. `/abs` and `/pdf` paths are allowed.

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Source</th>
      <th>RSS URL</th>
      <th>Category</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>arXiv AI</td>
      <td><code>http://export.arxiv.org/rss/cs.AI</code></td>
      <td>Artificial Intelligence</td>
    </tr>
    <tr>
      <td>2</td>
      <td>arXiv ML</td>
      <td><code>http://export.arxiv.org/rss/cs.LG</code></td>
      <td>Machine Learning</td>
    </tr>
    <tr>
      <td>3</td>
      <td>arXiv CS</td>
      <td><code>http://export.arxiv.org/rss/cs</code></td>
      <td>All Computer Science</td>
    </tr>
    <tr>
      <td>4</td>
      <td>arXiv Physics</td>
      <td><code>http://export.arxiv.org/rss/physics</code></td>
      <td>Physics</td>
    </tr>
    <tr>
      <td>5</td>
      <td>arXiv Math</td>
      <td><code>http://export.arxiv.org/rss/math</code></td>
      <td>Mathematics</td>
    </tr>
  </tbody>
</table>
</div>

## Avoid — robots.txt Blocks AI/Bot Crawlers

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Source</th>
      <th>Reason</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Al Jazeera</td>
      <td>Explicitly blocks <code>anthropic-ai</code>, <code>ClaudeBot</code> with <code>Disallow: /</code></td>
    </tr>
    <tr>
      <td>NPR News</td>
      <td>Explicitly blocks Anthropic and major AI crawlers with <code>Disallow: /</code></td>
    </tr>
    <tr>
      <td>Bloomberg Technology</td>
      <td>Blocks feed aggregators (Feedly, etc.) and AI crawlers</td>
    </tr>
  </tbody>
</table>
</div>
