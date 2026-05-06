---
layout: default
render_with_liquid: false
---

# Add Source

`capcat add-source` automates adding new RSS-based news sources.

## Usage

```bash
capcat add-source --url https://example.com/feed.xml
```

## What It Does

1. Fetches the RSS/Atom feed at the given URL
2. Parses feed metadata (title, site URL, category hints)
3. Generates a YAML config file in `Config/sources/active/config_driven/configs/`
4. Runs a validation check against the live feed
5. Confirms the source is discoverable via `capcat list sources`

## Interactive Flow

If run without `--url`, launches a prompt:

```
Enter RSS/Atom feed URL:
```

After fetching the feed, proposes a display name and config - you can confirm or edit before saving.

## Also Available in TUI

From `capcat catch` → "Manage sources" → "Add source".

## Manual Alternative

Create a YAML file directly in `Config/sources/active/config_driven/configs/`:

```yaml
display_name: "Example News"
base_url: "https://example.com/"
category: tech
rate_limit: 1.0
article_selectors:
  - ".headline a"
content_selectors:
  - "article .body"
```

See [Source Development](/docs/source-development.html) for the full YAML reference.
