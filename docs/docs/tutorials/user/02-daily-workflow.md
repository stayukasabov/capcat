---
layout: default
render_with_liquid: false
---

# Daily News Collection Workflow

Efficient routines for regular use.

## Option 1: Bundle (recommended)

Bundles are named groups of sources. One command, multiple sources:

```bash
capcat bundle tech --count 20 --html
```

List available bundles:

```bash
capcat list bundles
```

Run all bundles:

```bash
capcat bundle --all --count 15 --html
```

## Option 2: Multiple Sources

```bash
capcat fetch hn lb ieee --count 10 --html
```

## Option 3: Interactive

```bash
capcat catch
```

Select "Catch articles from a bundle of sources" — no flags to remember.

## With Media

```bash
capcat bundle tech --count 20 --html --media
```

Downloads images and PDFs alongside articles. Output size increases significantly.

## Scheduled with Cron

```cron
# Every morning at 07:00
0 7 * * * /home/user/.local/bin/capcat bundle tech --count 30 --html --output ~/News
```

## Update Existing Articles

```bash
capcat fetch hn --count 10 --html --update
```

`--update` re-fetches articles that already exist locally.

## Output Structure

```
News/
  hn/
    index.html
    2026-05-06-<title>/
      article.md
      article.html
      comments.md
      comments.html
      media/
```
