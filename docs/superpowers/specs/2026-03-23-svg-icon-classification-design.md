# SVG Icon Classification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detect SVG icons in article HTML and render them small and inline instead of full-width block, while preserving illustrations at full size.

**Architecture:** A private `_classify_svg_elements()` method added to `HtmlGenerator` in `capcat/htmlgen/generator.py`, slotted into the existing content transformation chain. It uses BeautifulSoup to score each `<img>` and `<svg>` element with weighted heuristics (size, shape, context), adds class `capcat-icon` to elements classified as icons, and returns the modified HTML string. CSS in `base.css` handles the visual treatment.

**Tech Stack:** BeautifulSoup4 (already a dependency), Python, CSS

---

## Problem

SVG icons scraped from article sources (e.g. social share buttons like Mastodon, Facebook, Reddit) are rendered as full-width block elements because the standard `img` CSS rules apply to them indiscriminately. These icons — typically square, small, and carrying `aria-label`/`role="img"` attributes — should render inline at ~1.5em instead.

## Constraints

- Cannot predict designer intent from position alone — icons may appear anywhere in the body
- Default to **illustration** when signals are ambiguous (safer to render something too large than to shrink a real diagram)
- No new files — classify as a private method on the existing `HtmlGenerator` class

---

## Scoring Model

Each `<img src="*.svg">` and inline `<svg>` element is scored on two counters: `icon_score` and `illustration_score`. The element receives class `capcat-icon` only when `icon_score > illustration_score`.

### Icon signals

| Signal | Points |
|---|---|
| `viewBox` is square (width == height) | 3 |
| Both `viewBox` dimensions ≤ 64 | 3 |
| `src` starts with `data:image/svg` | 2 |
| `aria-label` or `role="img"` attribute present | 2 |
| Direct parent is `<li>`, `<button>`, or `<a>` | 2 |
| Element has sibling text nodes in its parent (inline context) | 1 |

### Illustration signals

| Signal | Points |
|---|---|
| `viewBox` is non-square | 4 |
| Either `viewBox` dimension > 200 | 4 |
| Element is sole child of a `<p>` that is surrounded by other `<p>` elements | 2 |

### Fallback

When `icon_score == illustration_score` (including zero), classify as **illustration** (no class added).

---

## viewBox Extraction

For `<img src="data:image/svg+xml...">` elements, decode the URI and parse the embedded `viewBox` attribute with a regex. For inline `<svg>` elements, read the `viewBox` attribute directly. For `<img>` tags with explicit `width`/`height` HTML attributes, use those as a proxy when no viewBox is available. If no size information is present, treat as illustration.

---

## Implementation Location

**File:** `capcat/htmlgen/generator.py`

The method is added to the `HtmlGenerator` class and called in `generate_article_html_from_template()` as one more step in the existing transformation chain:

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
    """
```

---

## CSS Treatment

**File:** `capcat/themes/base.css`

Add after the existing `img` block:

```css
img.capcat-icon,
svg.capcat-icon {
    width: 1.5em;
    height: 1.5em;
    display: inline-block;
    vertical-align: middle;
    margin: 0 0.25em;
    border-radius: 0;
    box-shadow: none;
}
```

---

## Testing

Tests live in `tests/unit/test_svg_classifier.py` (new file). They call `_classify_svg_elements()` directly with hand-crafted HTML strings and assert the presence or absence of `capcat-icon` class.

### Cases to cover

| Case | Expected |
|---|---|
| `<img>` with `data:image/svg+xml` + `aria-label` + in `<li>` | `capcat-icon` |
| `<img>` with square 512×512 viewBox + `role="img"` | `capcat-icon` |
| Inline `<svg viewBox="0 0 24 24">` inside `<a>` | `capcat-icon` |
| `<img src="diagram.svg">` with wide non-square viewBox | no class |
| `<img src="illustration.svg">` as sole child of `<p>` between paragraphs | no class |
| `<img>` with no size info at all | no class (fallback) |
| `<img>` with square viewBox but > 200px, standalone in `<p>` | no class (illustration wins) |
