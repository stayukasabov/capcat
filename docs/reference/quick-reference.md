# Quick Reference

## Source IDs

| ID | Name | Category |
|----|------|----------|
| `hn` | Hacker News | tech |
| `lb` | Lobsters | tech |
| `iq` | InfoQ | tech |
| `ieee` | IEEE Spectrum | tech |
| `mashable` | Mashable | tech |
| `bbc` | BBC News | news |
| `guardian` | The Guardian | news |
| `bbcsport` | BBC Sport | sports |
| `nature` | Nature | science |
| `scientificamerican` | Scientific American | science |
| `mitnews` | MIT News AI | ai |
| `google-reserch` | Google Research | ai |

## Bundle Names and Sources

| Bundle | Source IDs |
|--------|------------|
| `techpro` | hn, lb, iq |
| `tech` | ieee, mashable |
| `news` | bbc, guardian |
| `science` | nature, scientificamerican |
| `ai` | mitnews, google-reserch |
| `sports` | bbcsport |
| `all` | (expands to all sources from all non-empty bundles) |

## Output Path Patterns

**Batch mode** (`capcat fetch` / `capcat bundle`):
```
~/Desktop/Vault/News/News_DD-MM-YYYY/Source_DD-MM-YYYY/NN_Title/
```
- `News_DD-MM-YYYY` — date directory for the run
- `Source_DD-MM-YYYY` — per-source subdirectory
- `NN_Title` — zero-padded article index + title slug
- HTML: `News_DD-MM-YYYY/html/index.html` (with `--html` flag)

**Single mode** (`capcat single <url>`):
```
~/Desktop/Vault/Capcats/cc_DD-MM-YYYY-Title/
```

## Common Commands

```bash
capcat fetch hn --count 10          # fetch 10 HN articles
capcat fetch hn,bbc --count 15      # multiple sources
capcat bundle techpro               # run bundle
capcat bundle all                   # run all bundles
capcat single https://example.com/  # single article
capcat catch                        # interactive TUI
capcat list sources                 # show registered sources
capcat --version                    # print version
```

## Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--count N` | `-c N` | Max articles per source |
| `--html` | | Generate HTML index |
| `--media` | | Download video/audio/docs |
| `--log FILE` | `-L FILE` | Write log to file |
| `--version` | | Print version and exit |
| `--help` | `-h` | Print usage and exit |

## Source Management

On first fetch, Capcat mirrors all builtin source configs to `Config/sources/active/` in your
project. Edit files there freely — they are never overwritten without your consent.

### Commands

| Command | Description |
|---------|-------------|
| `capcat add-source <url>` | Add a new RSS source (saved to `Config/sources/active/config_driven/configs/`) |
| `capcat remove-source <id>` | Remove a source from `Config/sources/active/` |
| `capcat list sources` | Show all registered sources |
| `capcat list bundles` | Show all available bundles |

### Paths

| Path | Purpose |
|------|---------|
| `Config/sources/active/config_driven/configs/` | Per-source YAML/JSON config files |
| `Config/sources/active/custom/` | Custom source directories (with `source.py`) |
| `Config/sources/active/bundles/bundles.yml` | Bundle definitions |
| `.capcat/source_hashes.json` | Tracks builtin-synced vs user-added sources |
