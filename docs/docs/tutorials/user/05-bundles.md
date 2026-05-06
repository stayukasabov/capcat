---
layout: default
render_with_liquid: false
---

# Organising with Bundles

Groups of sources for one-command collection.

## What Are Bundles?

A bundle is a named list of sources in `Config/sources/active/bundles/bundles.yml`. One command fetches all of them.

## List Bundles

```bash
capcat list bundles
```

## Run a Bundle

```bash
capcat bundle tech --count 20
capcat bundle tech --count 20 --html
capcat bundle tech --count 20 --html --media
```

## Run All Bundles

```bash
capcat bundle --all --count 15 --html
```

## Create a Bundle

Edit `Config/sources/active/bundles/bundles.yml`:

```yaml
bundles:
  tech:
    sources:
      - hn
      - lb
      - ieee
      - mitnews
    description: "Tech news"

  morning:
    sources:
      - hn
      - bbc
      - guardian
    description: "Morning briefing"
```

Source names must match what `capcat list sources` shows.

## Tips

- Bundles don't have to be disjoint - a source can appear in multiple bundles
- `--count` applies per source within the bundle, not total
- Bundle runs use the same 8-worker parallel processing as `capcat fetch`
- Combine with cron for scheduled collection: `capcat bundle morning --count 20 --html`
