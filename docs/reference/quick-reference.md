# Quick Reference

## Source IDs

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>ID</th>
      <th>Name</th>
      <th>Category</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>hn</code></td>
      <td>Hacker News</td>
      <td>tech</td>
    </tr>
    <tr>
      <td><code>lb</code></td>
      <td>Lobsters</td>
      <td>tech</td>
    </tr>
    <tr>
      <td><code>iq</code></td>
      <td>InfoQ</td>
      <td>tech</td>
    </tr>
    <tr>
      <td><code>ieee</code></td>
      <td>IEEE Spectrum</td>
      <td>tech</td>
    </tr>
    <tr>
      <td><code>mashable</code></td>
      <td>Mashable</td>
      <td>tech</td>
    </tr>
    <tr>
      <td><code>bbc</code></td>
      <td>BBC News</td>
      <td>news</td>
    </tr>
    <tr>
      <td><code>guardian</code></td>
      <td>The Guardian</td>
      <td>news</td>
    </tr>
    <tr>
      <td><code>bbcsport</code></td>
      <td>BBC Sport</td>
      <td>sports</td>
    </tr>
    <tr>
      <td><code>nature</code></td>
      <td>Nature</td>
      <td>science</td>
    </tr>
    <tr>
      <td><code>scientificamerican</code></td>
      <td>Scientific American</td>
      <td>science</td>
    </tr>
    <tr>
      <td><code>mitnews</code></td>
      <td>MIT News AI</td>
      <td>ai</td>
    </tr>
    <tr>
      <td><code>google-research</code></td>
      <td>Google Research</td>
      <td>ai</td>
    </tr>
  </tbody>
</table>
</div>

## Bundle Names and Sources

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Bundle</th>
      <th>Source IDs</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>techpro</code></td>
      <td>hn, lb, iq</td>
    </tr>
    <tr>
      <td><code>tech</code></td>
      <td>ieee, mashable</td>
    </tr>
    <tr>
      <td><code>news</code></td>
      <td>bbc, guardian</td>
    </tr>
    <tr>
      <td><code>science</code></td>
      <td>nature, scientificamerican</td>
    </tr>
    <tr>
      <td><code>ai</code></td>
      <td>mitnews, google-research</td>
    </tr>
    <tr>
      <td><code>sports</code></td>
      <td>bbcsport</td>
    </tr>
    <tr>
      <td><code>all</code></td>
      <td>(expands to all sources from all non-empty bundles)</td>
    </tr>
  </tbody>
</table>
</div>

## Output Path Patterns

**Batch mode** (`capcat fetch` / `capcat bundle`):
```
~/Desktop/Vault/News/News_DD-MM-YYYY/Source_DD-MM-YYYY/NN_Title/
```
- `News_DD-MM-YYYY` - date directory for the run
- `Source_DD-MM-YYYY` - per-source subdirectory
- `NN_Title` - zero-padded article index + title slug
- HTML: `News_DD-MM-YYYY/html/index.html` (with `--html` flag)

**Single mode** (`capcat single <url>`):
```
~/Desktop/Vault/Capcats/DD-MM-YYYY-Title/
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

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Flag</th>
      <th>Short</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>--count N</code></td>
      <td><code>-c N</code></td>
      <td>Max articles per source</td>
    </tr>
    <tr>
      <td><code>--html</code></td>
      <td>Generate HTML index</td>
    </tr>
    <tr>
      <td><code>--media</code></td>
      <td>Download video/audio/docs</td>
    </tr>
    <tr>
      <td><code>--log FILE</code></td>
      <td><code>-L FILE</code></td>
      <td>Write log to file</td>
    </tr>
    <tr>
      <td><code>--version</code></td>
      <td>Print version and exit</td>
    </tr>
    <tr>
      <td><code>--help</code></td>
      <td><code>-h</code></td>
      <td>Print usage and exit</td>
    </tr>
  </tbody>
</table>
</div>

## Source Management

On first use, Capcat mirrors all builtin source configs to `Config/sources/active/` in your
project. Edit files there freely - they are never overwritten without your consent.

### Commands

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Command</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>capcat add-source <url></code></td>
      <td>Add a new RSS source (saved to <code>Config/sources/active/config_driven/configs/</code>)</td>
    </tr>
    <tr>
      <td><code>capcat remove-source <id></code></td>
      <td>Remove a source from <code>Config/sources/active/</code></td>
    </tr>
    <tr>
      <td><code>capcat list sources</code></td>
      <td>Show all registered sources</td>
    </tr>
    <tr>
      <td><code>capcat list bundles</code></td>
      <td>Show all available bundles</td>
    </tr>
  </tbody>
</table>
</div>

### Paths

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Path</th>
      <th>Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>Config/sources/active/config_driven/configs/</code></td>
      <td>Per-source YAML/JSON config files</td>
    </tr>
    <tr>
      <td><code>Config/sources/active/custom/</code></td>
      <td>Custom source directories (with <code>source.py</code>)</td>
    </tr>
    <tr>
      <td><code>Config/sources/active/bundles/bundles.yml</code></td>
      <td>Bundle definitions</td>
    </tr>
    <tr>
      <td><code>.capcat/source_hashes.json</code></td>
      <td>Tracks builtin-synced vs user-added sources</td>
    </tr>
  </tbody>
</table>
</div>
