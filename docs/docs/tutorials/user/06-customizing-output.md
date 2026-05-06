---
layout: default
render_with_liquid: false
---

# Customising Output

Control what Capcat collects and where it goes.

## Article Count

```bash
capcat fetch hn --count 50       # fetch 50 articles
capcat bundle tech --count 10    # 10 per source in bundle
```

Default: 30 per source. Set globally in `Config/Global-settings.yaml`:

```yaml
fetch:
  default_count: 30
```

## HTML Output

Generates browsable HTML alongside Markdown:

```bash
capcat fetch hn --count 20 --html
```

Open `News/hn/index.html` in a browser. Templates are in `Config/themes/`.

## Media Download

```bash
# Images and PDFs
capcat fetch hn --count 20 --html --media

# Single article with full media
capcat single https://example.com/article --html --media
```

`--media` downloads both images (`download_files=True`) and PDFs (`download_pdfs=True`). These are independent flags — `--media` sets both.

Per-source PDF control in YAML:

```yaml
media:
  download_pdfs: false       # this source never downloads PDFs
  max_pdf_size_mb: 5         # cap at 5MB for this source
```

## Output Location

Default: current working directory.

```bash
capcat fetch hn --count 20 --output ~/News
capcat single <url> --output ~/archive
```

Set permanently in `Config/Global-settings.yaml`:

```yaml
output:
  base_dir: "/home/user/News"
```

## Update Existing Articles

Re-fetch articles already collected:

```bash
capcat fetch hn --count 10 --update
```

Without `--update`, already-existing article directories are skipped.

## Output Structure

```
News/
  <source>/
    index.html              ← source article index
    <date>-<slug>/
      article.md
      article.html
      comments.md           ← HN, Lobsters, LessWrong
      comments.html
      media/
        image1.jpg
        document.pdf

Capcats/
  <date>-<slug>/
    article.md
    article.html
    media/
```
