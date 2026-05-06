---
layout: default
render_with_liquid: false
---

# Interactive Mode

Capcat's TUI — full operation without memorising CLI flags.

## Launch

```bash
capcat catch
```

## Main Menu

```
What would you like me to do?

> Catch articles from a bundle of sources
  Catch articles from a single source
  Catch a single article by URL
  Manage sources
  Settings
  Exit
```

Navigate with arrow keys, select with Enter.

## Bundle Fetch

Select "Catch articles from a bundle of sources" to choose a named bundle and article count. Equivalent to `capcat bundle <name> --count N`.

## Single Source Fetch

Select "Catch articles from a single source" to pick any active source and set count. Equivalent to `capcat fetch <source> --count N`.

## Single Article

Select "Catch a single article by URL" and paste a URL. Equivalent to `capcat single <url>`.

## Manage Sources

Submenu for source management:

- **Add source** — enter an RSS/Atom URL; Capcat fetches the feed, proposes a name, and creates the config
- **Remove source** — interactive list; supports dry-run, backup, and undo
- **List sources** — shows all active sources with category

## PDF Prompt

When fetching, Capcat asks:

```
Download PDFs?
> Yes
  No
  Source defaults
```

- "Yes" — download all PDFs found
- "No" — skip PDFs for this run
- "Source defaults" — use per-source `media.download_pdfs` setting

## HTML Output

The TUI does not currently expose an HTML toggle. Use the CLI flag `--html` if you need HTML output alongside Markdown.

## Theme

Orange accent (`fg:#d75f00`) on selection and pointers, provided by the `questionary` library.
