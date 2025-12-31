# Daily News Collection Workflow

Set up an efficient daily routine for collecting news with Capcat.

## What You'll Learn

- Fetch from multiple sources at once
- Use bundles for organized collection
- Generate browsable HTML versions
- Establish a daily routine

## The Morning Routine

### Option 1: Quick Tech News

Collect 20 articles from tech sources:

```bash
./capcat bundle tech --count 20 --html
```

This fetches from:
- IEEE Spectrum
- Mashable
- Gizmodo

Result: Organized folders with articles and HTML for browser reading.

### Option 2: Professional Developer News

Get deeper technical content:

```bash
./capcat bundle techpro --count 15 --html
```

This fetches from:
- Hacker News (with comments)
- Lobsters
- InfoQ

### Option 3: Mixed News Diet

Get everything:

```bash
./capcat bundle news --count 10
./capcat bundle tech --count 15
./capcat bundle science --count 10
```

## The Evening Routine

### Catch Up on Saved Articles

Check your saved articles:

```bash
cd ../News/news_$(date +%d-%m-%Y)
ls -la
```

Open the HTML index (if you used --html):
```bash
open Hacker_News_DD-MM-YYYY/index.html
```

### Add Interesting Single Articles

Found something interesting during the day?

```bash
./capcat single https://interesting-article.com/story --html
```

Saved in `../Capcats/` for quick access.

## Weekly Deep Dive

### Saturday Research Collection

Collect more articles for weekend reading:

```bash
./capcat bundle science --count 30 --html --media
./capcat bundle ai --count 25 --html
```

The `--media` flag downloads videos and PDFs for offline reading.

## Custom Daily Bundle

### Create Your Personal Bundle

Edit your bundle configuration:

```bash
vim sources/active/bundles.yml
```

Add your custom bundle:

```yaml
daily:
  description: "My daily news bundle"
  sources:
    - hn
    - bbc
    - nature
    - mitnews
  default_count: 15
```

Use it:

```bash
./capcat bundle daily --html
```

## Automation with Cron

### Set Up Daily Auto-Collection

Edit crontab:

```bash
crontab -e
```

Add morning collection (8 AM):

```
0 8 * * * cd /path/to/Capcat/Application && ./capcat bundle tech --count 20 --html >> ~/capcat.log 2>&1
```

Add evening collection (6 PM):

```
0 18 * * * cd /path/to/Capcat/Application && ./capcat bundle news --count 15 --html >> ~/capcat.log 2>&1
```

Check your log:

```bash
tail -f ~/capcat.log
```

## Pro Tips

**Save Time:**
- Use `--html` flag for browser reading
- Skip `--html` for Markdown-only (faster)
- Use smaller counts for daily (10-20), larger for weekly (30-50)

**Stay Organized:**
- Articles auto-organize by date
- Each source gets its own folder
- HTML indexes make browsing easy

**Don't Miss Content:**
- Bundle 'all' sources: `./capcat bundle all --count 10`
- Test new sources: `./capcat fetch newsource --count 3`
- Check source health: `./capcat list sources`

## Example Daily Script

Create `daily-news.sh`:

```bash
#!/bin/bash
# Daily news collection script

DATE=$(date +%d-%m-%Y)
LOG="$HOME/capcat-$DATE.log"

echo "Collecting news for $DATE..." | tee -a "$LOG"

# Morning tech news
./capcat bundle tech --count 20 --html >> "$LOG" 2>&1

# General news
./capcat bundle news --count 15 --html >> "$LOG" 2>&1

# AI updates
./capcat bundle ai --count 10 --html >> "$LOG" 2>&1

echo "Collection complete!" | tee -a "$LOG"
```

Make executable and run:

```bash
chmod +x daily-news.sh
./daily-news.sh
```

## Next Steps

**Customize further:**
- [Managing Your Sources](04-managing-sources.html) - Add/remove sources
- [Bundles](05-bundles.html) - Create custom bundles
- [Automation](07-automation.html) - Advanced scheduling

**Technical details:**
- [CLI Commands Exhaustive](../01-cli-commands-exhaustive.html) - All command options
- [Configuration Exhaustive](../03-configuration-exhaustive.html) - System settings

## Quick Reference

```bash
# Morning routine
./capcat bundle tech --count 20 --html

# Evening catch-up
./capcat bundle news --count 15

# Weekend deep dive
./capcat bundle science --count 30 --html --media

# Check what's available
./capcat list bundles

# Custom bundle
./capcat bundle mybundle --count 25
```
