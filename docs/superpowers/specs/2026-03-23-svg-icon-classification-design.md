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

| Signal | Points |
|---|---|
| `viewBox` is square (width == height) | 3 |
| Both `viewBox` dimensions ≤ 64 | 3 |
| `src` starts with `data:image/svg` | 2 |
| `aria-label` or `role="img"` attribute present | 2 |
| Direct parent is `<li>`, `<button>` | 2 |
| Direct parent is `<a>` that is itself a descendant of `<li>`, `<nav>`, `<footer>`, or `<header>` | 2 |
| Element has non-whitespace-only sibling text nodes in its parent | 1 |

Note: The `<a>` parent signal is deliberately narrowed to navigation/footer contexts. In practice, `<a href="..."><img></a>` lightbox wrappers in article body content are already stripped by `_remove_image_anchor_wrappers()` earlier in the transformation chain (before `_classify_svg_elements()` runs), so the `<a>` parent signal only fires for inline `<svg>` elements inside navigation links, not for `<img>` elements.

### Illustration signals

| Signal | Points |
|---|---|
| `viewBox` is non-square | 4 |
| Either `viewBox` dimension > 200 | 4 |
| Element is sole child of a `<p>` that is surrounded by other `<p>` sibling elements | 2 |

### Score walk-through for primary problem case

A typical social share icon: `<img src="data:image/svg+xml;charset=utf-8,..." aria-label="Mastodon" role="img">` inside `<li>`, with `viewBox="0 0 512 512"`.

| Signal | Points to |
|---|---|
| Square viewBox (512 == 512) | icon +3 |
| Dims ≤ 64? No (512 > 64) | — |
| `data:image/svg` src | icon +2 |
| `aria-label` or `role="img"` present (one check, max 2 pts) | icon +2 |
| Parent is `<li>` | icon +2 |
| Dim > 200 (512 > 200) | illustration +4 |

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

| # | Case | Expected |
|---|---|---|
| 1 | `<img src="data:image/svg+xml;charset=utf-8,..." aria-label="Mastodon" role="img">` in `<li>`, viewBox `0 0 512 512` | `capcat-icon` |
| 2 | `<img src="data:image/svg+xml;base64,...">`  square 512×512 viewBox, in `<li>` | `capcat-icon` |
| 3 | Inline `<svg viewBox="0 0 24 24">` inside `<a>` inside `<nav>` | `capcat-icon` |
| 4 | `<img src="diagram.svg">` with wide non-square viewBox `0 0 800 400` | no class |
| 5 | `<img src="illustration.svg">` as sole child of `<p>` between other `<p>` elements | no class |
| 6 | `<img>` with no size info at all | no class (fallback) |
| 7 | Square 512×512 `<img>` with no aria-label, no list context, standalone in `<p>` | no class (illustration wins on dim > 200) |
| 8 | Bare `<img src="diagram.svg">` square 400×400, no accessibility attrs, no list context — simulates post-`_remove_image_anchor_wrappers` state | no class (illustration wins: dim > 200, no countering icon signals) |
| 9 | Icon already has a `class` attribute — `capcat-icon` must be appended, not replace | existing class preserved |
| 10 | Icon inside `<p>` (verifies specificity fix — rendered inline, not block) | `capcat-icon` and `display:inline-block` wins |
