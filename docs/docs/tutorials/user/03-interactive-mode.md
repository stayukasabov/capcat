---
layout: default
render_with_liquid: false
---

# Interactive Mode

Full TUI - no command memorisation needed.

## Launch

```bash
capcat catch
```

## Navigation

- Arrow keys to move
- Enter to select
- Ctrl+C to exit at any point

## Main Menu Options

| Option | Equivalent CLI |
|--------|---------------|
| Catch articles from a bundle | `capcat bundle <name>` |
| Catch articles from a single source | `capcat fetch <source>` |
| Catch a single article by URL | `capcat single <url>` |
| Manage sources | `capcat add-source` / `capcat remove-source` |
| Settings | - |
| Exit | - |

## Bundle Fetch Flow

1. Select "Catch articles from a bundle of sources"
2. Choose a bundle from the list
3. Enter article count (or accept default)
4. Answer PDF download prompt: Yes / No / Source defaults
5. Watch progress bar as articles fetch

## Single Source Fetch Flow

1. Select "Catch articles from a single source"
2. Choose a source from the list
3. Enter article count
4. Answer PDF prompt
5. Articles saved to `News/<source>/`

## Single Article Flow

1. Select "Catch a single article by URL"
2. Paste the article URL
3. Article saved to `Capcats/`

## Manage Sources

Add or remove sources without touching config files:

- **Add** - enter RSS URL, Capcat generates the YAML config
- **Remove** - pick from list, backup created automatically

## Tips

- Use interactive mode for exploration; use CLI for scripts and cron
- The PDF prompt "Source defaults" respects per-source `media.download_pdfs` in YAML
