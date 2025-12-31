# First 5 Minutes with Capcat

Get Capcat running and collect your first articles in under 5 minutes.

## What You'll Learn

- Install and verify Capcat
- Run your first article fetch
- Understand the output structure

## Prerequisites

- Python 3.8 or higher
- Internet connection
- 5 minutes of time

## Step 1: Verify Installation

Check if Capcat is ready:

```bash
./capcat --version
```

Expected output:
```
Capcat v2.0.0
```

If you see an error, run the fix script:

```bash
./scripts/fix_dependencies.sh
```

## Step 2: Your First Fetch

Collect 5 articles from Hacker News:

```bash
./capcat fetch hn --count 5
```

You'll see:
```
Processing hn articles...
[Progress indicators]
Successfully processed 5 articles
```

## Step 3: Check Your Results

Articles are saved in:
```
../News/news_DD-MM-YYYY/Hacker_News_DD-MM-YYYY/
```

Each article is in its own folder:
```
01_Article_Title/
├── article.md          # Article content in Markdown
├── images/             # Downloaded images
└── html/               # HTML version (if --html flag used)
```

## Step 4: Try a Single Article

Grab a specific article by URL:

```bash
./capcat single https://example.com/article
```

Result saved in:
```
../Capcats/cc_DD-MM-YYYY-Article-Title/
```

## What Just Happened?

You ran Capcat in two modes:
- **fetch** - Collect from a news source
- **single** - Grab one specific article

Capcat automatically:
- Downloaded article content
- Converted HTML to clean Markdown
- Downloaded and embedded images
- Organized everything by date and source

## Next Steps

**Ready for more?**
- [Daily News Collection](02-daily-workflow.html) - Set up your routine
- [Interactive Mode](03-interactive-mode.html) - Use the visual menu

**Need technical details?**
- [CLI Commands Exhaustive](../01-cli-commands-exhaustive.html) - Every command option documented

## Quick Reference

```bash
# Fetch articles
./capcat fetch SOURCE --count N

# Fetch with HTML
./capcat fetch SOURCE --count N --html

# Grab single article
./capcat single URL

# List available sources
./capcat list sources

# Interactive menu
./capcat catch
```
