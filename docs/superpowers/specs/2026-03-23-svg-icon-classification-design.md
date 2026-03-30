# SVG Icon Classification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detect SVG icons in article HTML and render them small and inline instead of full-width block, while preserving illustrations at full size.

**Architecture:** A private `_classify_svg_elements()` method added to `HtmlGenerator` in `capcat/htmlgen/generator.py`, slotted into the existing content transformation chain. It uses BeautifulSoup to score each `<img>` and `<svg>` element with weighted heuristics (size, shape, context), adds class `capcat-icon` to elements classified as icons, and returns the modified HTML string. CSS in `capcat/themes/base.css` handles the visual treatment.

**Tech Stack:** BeautifulSoup4 with `"html.parser"` (already a dependency), Python, CSS

---

## Problem

SVG icons scraped from article sources (e.g. social share buttons like Mastodon, Facebook, Reddit) render as full-width block elements because the standard `img` CSS rules apply indiscriminately. These icons — typically square, small, carrying `aria-label`/`role="img"` attributes — should render inline at ~1.5em instead.

## Constraints

- Cannot predict designer intent from position alone — icons may appear anywhere in the body
- Default to **illustration** when signals are ambiguous (safer to render something too large than to shrink a real diagram)
- No new files — classify as a private method on the existing `HtmlGenerator` class

---

## Scoring Model

Each `<img src="*.svg">` and inline `<svg>` element is scored on two counters: `icon_score` and `illustration_score`. The element receives class `capcat-icon` only when `icon_score > illustration_score` (strict greater-than — ties default to illustration).

### Icon signals

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Signal</th>
      <th>Points</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>viewBox</code> is square (width == height)</td>
      <td>3</td>
    </tr>
    <tr>
      <td>Both <code>viewBox</code> dimensions ≤ 64</td>
      <td>3</td>
    </tr>
    <tr>
      <td><code>src</code> starts with <code>data:image/svg</code></td>
      <td>2</td>
    </tr>
    <tr>
      <td><code>aria-label</code> or <code>role="img"</code> attribute present</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Direct parent is <code><li></code>, <code><button></code></td>
      <td>2</td>
    </tr>
    <tr>
      <td>Direct parent is <code><a></code> that is itself a descendant of <code><li></code>, <code><nav></code>, <code><footer></code>, or <code><header></code></td>
      <td>2</td>
    </tr>
    <tr>
      <td>Element has non-whitespace-only sibling text nodes in its parent</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>

Note: The `<a>` parent signal is deliberately narrowed to navigation/footer contexts. In practice, `<a href="..."><img></a>` lightbox wrappers in article body content are already stripped by `_remove_image_anchor_wrappers()` earlier in the transformation chain (before `_classify_svg_elements()` runs), so the `<a>` parent signal only fires for inline `<svg>` elements inside navigation links, not for `<img>` elements.

### Illustration signals

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Signal</th>
      <th>Points</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>viewBox</code> is non-square</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Either <code>viewBox</code> dimension > 200</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Element is sole child of a <code><p></code> that is surrounded by other <code><p></code> sibling elements</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
</div>

### Score walk-through for primary problem case

A typical social share icon: `<img src="data:image/svg+xml;charset=utf-8,..." aria-label="Mastodon" role="img">` inside `<li>`, with `viewBox="0 0 512 512"`.

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Signal</th>
      <th>Points to</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Square viewBox (512 == 512)</td>
      <td>icon +3</td>
    </tr>
    <tr>
      <td>Dims ≤ 64? No (512 > 64)</td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>data:image/svg</code> src</td>
      <td>icon +2</td>
    </tr>
    <tr>
      <td><code>aria-label</code> or <code>role="img"</code> present (one check, max 2 pts)</td>
      <td>icon +2</td>
    </tr>
    <tr>
      <td>Parent is <code><li></code></td>
      <td>icon +2</td>
    </tr>
    <tr>
      <td>Dim > 200 (512 > 200)</td>
      <td>illustration +4</td>
    </tr>
  </tbody>
</table>
</div>

**Result: icon 9 vs illustration 4 → classified as icon.** ✓

### Edge case: 256×256 icon with no accessibility attributes in a bare `<div>`

Icon 3 (square) vs illustration 4 (dim > 200) → classified as illustration. Acceptable — without accessibility markers or list context, there is not enough signal to confidently call it an icon.

---

## viewBox Extraction

For `<img>` elements the viewBox must be extracted from the `src` attribute or HTML `width`/`height` attributes. Three encoding variants must be handled:

**1. Percent-encoded:** `data:image/svg+xml;charset=utf-8,%3Csvg%20viewBox%3D%220%200%20512%20512%22...`
→ `urllib.parse.unquote(src_after_comma)`, then regex for `viewBox`.

**2. Base64-encoded:** `data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgNTEyIDUxMiI...`
→ `base64.b64decode(src_after_comma)`, decode as UTF-8, then regex for `viewBox`.

**3. Raw (unencoded):** `data:image/svg+xml,<svg viewBox="0 0 24 24"...`
→ Regex directly on `src_after_comma`.

Detection: check the prefix after `data:image/svg+xml`:
- Contains `;base64,` → base64
- Contains `;charset` or starts with `,%` → percent-encoded
- Otherwise → raw

**Regex for viewBox** (applied after decoding):
```python
re.search(r'viewBox=["\']?\s*(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)', decoded)
```
Groups 3 and 4 are width and height. Both single and double quotes are handled by the `["\']?` pattern.

For inline `<svg>` elements: read the `viewBox` attribute directly from the tag.

For `<img>` tags with explicit `width`/`height` HTML attributes and no parseable `viewBox`: use those values as a proxy.

If no size information is available: treat as illustration (no points awarded for size signals).

---

## Implementation Location

**File:** `capcat/htmlgen/generator.py`

The method is added to the `HtmlGenerator` class. It is called in **`generate_article_html_from_template()`** only (line ~554, the template-based path marked "new, reliable"). The legacy `generate_article_html()` method (line ~460) is not updated — it is the old code path not used for template rendering.

Insertion point in `generate_article_html_from_template()`:

```python
html_content = self._wrap_source_url_in_div(html_content)
html_content = self._classify_svg_elements(html_content)   # ← new step
```

**Method signature:**
```python
def _classify_svg_elements(self, html_content: str) -> str:
    """Classify <img src="*.svg"> and inline <svg> elements as icons or
    illustrations using weighted heuristics. Adds class 'capcat-icon' to
    elements classified as icons. Illustrations are left untouched.
    Uses html.parser (no lxml/html5lib dependency).
    """
```

**Class attribute merging:** when adding `capcat-icon`, use BeautifulSoup's class list API to append rather than replace:
```python
existing = element.get("class") or []
element["class"] = existing + ["capcat-icon"]
```

---

## CSS Treatment

**File:** `capcat/themes/base.css`

The existing `p img` rule (specificity 0-1-1) would win over `img.capcat-icon` (also 0-1-1) for icons inside `<p>` tags because it appears earlier in the file. To ensure icons in paragraphs render correctly, use a more specific selector that covers the `<p>` case explicitly:

```css
img.capcat-icon,
svg.capcat-icon,
p img.capcat-icon,
p svg.capcat-icon {
    width: 1.5em;
    height: 1.5em;
    display: inline-block;
    vertical-align: middle;
    margin: 0 0.25em;
    border-radius: 0;
    box-shadow: none;
    max-width: unset;
    clear: none;
}
```

`max-width: unset` removes the inherited `max-width: 100%` from the base `img` rule.

---

## Testing

**File:** `tests/unit/test_htmlgen/test_svg_classifier.py` (new file, matches existing `test_htmlgen/` convention)

Tests instantiate `HtmlGenerator` and call `_classify_svg_elements()` directly with hand-crafted HTML strings, asserting presence or absence of `capcat-icon` class in the output.

### Cases to cover

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Case</th>
      <th>Expected</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td><code><img src="data:image/svg+xml;charset=utf-8,..." aria-label="Mastodon" role="img"></code> in <code><li></code>, viewBox <code>0 0 512 512</code></td>
      <td><code>capcat-icon</code></td>
    </tr>
    <tr>
      <td>2</td>
      <td><code><img src="data:image/svg+xml;base64,..."></code>  square 512×512 viewBox, in <code><li></code></td>
      <td><code>capcat-icon</code></td>
    </tr>
    <tr>
      <td>3</td>
      <td>Inline <code><svg viewBox="0 0 24 24"></code> inside <code><a></code> inside <code><nav></code></td>
      <td><code>capcat-icon</code></td>
    </tr>
    <tr>
      <td>4</td>
      <td><code><img src="diagram.svg"></code> with wide non-square viewBox <code>0 0 800 400</code></td>
      <td>no class</td>
    </tr>
    <tr>
      <td>5</td>
      <td><code><img src="illustration.svg"></code> as sole child of <code><p></code> between other <code><p></code> elements</td>
      <td>no class</td>
    </tr>
    <tr>
      <td>6</td>
      <td><code><img></code> with no size info at all</td>
      <td>no class (fallback)</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Square 512×512 <code><img></code> with no aria-label, no list context, standalone in <code><p></code></td>
      <td>no class (illustration wins on dim > 200)</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Bare <code><img src="diagram.svg"></code> square 400×400, no accessibility attrs, no list context — simulates post-<code>_remove_image_anchor_wrappers</code> state</td>
      <td>no class (illustration wins: dim > 200, no countering icon signals)</td>
    </tr>
    <tr>
      <td>9</td>
      <td>Icon already has a <code>class</code> attribute — <code>capcat-icon</code> must be appended, not replace</td>
      <td>existing class preserved</td>
    </tr>
    <tr>
      <td>10</td>
      <td>Icon inside <code><p></code> (verifies specificity fix — rendered inline, not block)</td>
      <td><code>capcat-icon</code> and <code>display:inline-block</code> wins</td>
    </tr>
  </tbody>
</table>
</div>
