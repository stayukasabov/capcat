# SVG Icon Classification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detect SVG icons in article HTML and add class `capcat-icon` so they render small and inline instead of full-width block.

**Architecture:** Add `_classify_svg_elements(html_content)` as a private method on `ArticleHTMLGenerator` in `capcat/htmlgen/generator.py`, inserted into the existing content transformation chain after `_wrap_source_url_in_div`. It parses with BeautifulSoup, scores each `<img src="*.svg">` and inline `<svg>` element using weighted heuristics, appends class `capcat-icon` to icons, and returns the modified HTML string. CSS in `capcat/themes/base.css` handles visual treatment.

**Tech Stack:** BeautifulSoup4 with `html.parser` (already a dependency), Python stdlib (`re`, `base64`, `urllib.parse`), CSS

**Spec:** `docs/superpowers/specs/2026-03-23-svg-icon-classification-design.md`

---

## File Structure

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>File</th>
      <th>Change</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>capcat/htmlgen/generator.py</code></td>
      <td>Add <code>_classify_svg_elements()</code> method + call it in the chain at line ~597 only (<code>generate_article_html_from_template</code>)</td>
    </tr>
    <tr>
      <td><code>capcat/themes/base.css</code></td>
      <td>Add <code>.capcat-icon</code> CSS rule after line 717</td>
    </tr>
    <tr>
      <td><code>tests/unit/test_htmlgen/test_svg_classifier.py</code></td>
      <td>New test file — 10 test cases</td>
    </tr>
  </tbody>
</table>
</div>

---

## Task 1: CSS rule for `.capcat-icon`

**Files:**
- Modify: `capcat/themes/base.css:717`

Add the icon override rule immediately after the `p img` block (line 717). It must override `display: block`, `margin`, `max-width`, `clear`, `border-radius`, and `box-shadow` from the base `img` rule, and also beat the `p img` rule via explicit `p img.capcat-icon` selector.

- [ ] **Step 1: Open `capcat/themes/base.css` and locate the `p img` block ending at line 717**

It looks like:
```css
/* Images in paragraphs need proper spacing */
p img {
  margin: 2rem auto;
  display: block;
}
```

- [ ] **Step 2: Add the `.capcat-icon` rule immediately after line 717**

```css

/* SVG icons — inline small rendering, overrides block-image defaults */
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

- [ ] **Step 3: Verify the file looks correct**

```bash
grep -n "capcat-icon" capcat/themes/base.css
```
Expected: 5 lines containing `capcat-icon`.

- [ ] **Step 4: Commit**

```bash
git add capcat/themes/base.css
git commit -m "feat: add .capcat-icon CSS rule for inline SVG icon rendering"
```

---

## Task 2: Write the failing tests

**Files:**
- Create: `tests/unit/test_htmlgen/test_svg_classifier.py`

The tests call `ArticleHTMLGenerator()._classify_svg_elements(html)` directly with hand-crafted HTML strings and assert presence/absence of `capcat-icon` in the output.

**Context:** `ArticleHTMLGenerator` lives in `capcat/htmlgen/generator.py` (class defined at line 28). It can be instantiated with no arguments. The method `_classify_svg_elements` does not exist yet — all tests will fail with `AttributeError`.

- [ ] **Step 1: Create the test file**

```python
# tests/unit/test_htmlgen/test_svg_classifier.py
"""Tests for ArticleHTMLGenerator._classify_svg_elements — SVG icon vs illustration classifier."""
from __future__ import annotations
import base64
import urllib.parse
import pytest
from capcat.htmlgen.generator import ArticleHTMLGenerator


@pytest.fixture
def gen() -> ArticleHTMLGenerator:
    return ArticleHTMLGenerator()


def _has_icon_class(html: str) -> bool:
    """Return True if any element in html has class capcat-icon."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    return bool(soup.find(class_="capcat-icon"))


def _make_data_uri_percent(viewbox: str = "0 0 512 512") -> str:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"><path d="M0 0"/></svg>'
    return "data:image/svg+xml;charset=utf-8," + urllib.parse.quote(svg)


def _make_data_uri_base64(viewbox: str = "0 0 512 512") -> str:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"><path d="M0 0"/></svg>'
    encoded = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{encoded}"


# ── Test 1: Percent-encoded data URI icon in <li> with aria-label ────────────

def test_percent_encoded_icon_in_li_gets_icon_class(gen):
    src = _make_data_uri_percent("0 0 512 512")
    html = f'<ul><li><img src="{src}" aria-label="Mastodon" role="img"/></li></ul>'
    result = gen._classify_svg_elements(html)
    assert _has_icon_class(result), "Expected capcat-icon on social share icon"


# ── Test 2: Base64-encoded data URI icon in <li> ─────────────────────────────

def test_base64_icon_in_li_gets_icon_class(gen):
    src = _make_data_uri_base64("0 0 512 512")
    html = f'<ul><li><img src="{src}"/></li></ul>'
    result = gen._classify_svg_elements(html)
    assert _has_icon_class(result), "Expected capcat-icon on base64 data URI icon in list"


# ── Test 3: Inline <svg> in <a> inside <nav> ─────────────────────────────────

def test_inline_svg_in_nav_link_gets_icon_class(gen):
    html = '<nav><a href="#"><svg viewBox="0 0 24 24"><path d="M0 0"/></svg></a></nav>'
    result = gen._classify_svg_elements(html)
    assert _has_icon_class(result), "Expected capcat-icon on nav SVG icon"


# ── Test 4: Non-square illustration — no class ───────────────────────────────

def test_non_square_svg_gets_no_class(gen):
    html = '<p><img src="diagram.svg" width="800" height="400"/></p>'
    result = gen._classify_svg_elements(html)
    assert not _has_icon_class(result), "Non-square illustration should not get capcat-icon"


# ── Test 5: Sole-child illustration between paragraphs — no class ────────────

def test_sole_child_between_paragraphs_gets_no_class(gen):
    html = (
        '<p>Before text.</p>'
        '<p><img src="illustration.svg" width="400" height="400"/></p>'
        '<p>After text.</p>'
    )
    result = gen._classify_svg_elements(html)
    assert not _has_icon_class(result), "Sole-child illustration between paragraphs should not get capcat-icon"


# ── Test 6: No size info — fallback to illustration ──────────────────────────

def test_svg_with_no_size_info_gets_no_class(gen):
    html = '<p><img src="unknown.svg"/></p>'
    result = gen._classify_svg_elements(html)
    assert not _has_icon_class(result), "SVG with no size info should default to illustration"


# ── Test 7: Large square without accessibility/context — illustration ─────────

def test_large_square_no_context_gets_no_class(gen):
    html = '<p><img src="chart.svg" width="512" height="512"/></p>'
    result = gen._classify_svg_elements(html)
    assert not _has_icon_class(result), "Large square with no icon signals should not get capcat-icon"


# ── Test 8: Bare img (post-anchor-strip) large square — illustration ──────────

def test_bare_large_square_img_gets_no_class(gen):
    # Simulates state after _remove_image_anchor_wrappers has run
    html = '<div><img src="diagram.svg" width="400" height="400"/></div>'
    result = gen._classify_svg_elements(html)
    assert not _has_icon_class(result), "Large square bare img should not get capcat-icon"


# ── Test 9: Existing class is preserved when capcat-icon is added ─────────────

def test_existing_class_preserved_on_icon(gen):
    src = _make_data_uri_percent("0 0 24 24")
    html = f'<ul><li><img src="{src}" class="social-icon" aria-label="Share"/></li></ul>'
    result = gen._classify_svg_elements(html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(result, "html.parser")
    img = soup.find("img")
    classes = img.get("class", [])
    assert "capcat-icon" in classes, "capcat-icon should be added"
    assert "social-icon" in classes, "existing class should be preserved"


# ── Test 10: Icon inside <p> also gets capcat-icon class ─────────────────────

def test_icon_inside_paragraph_gets_icon_class(gen):
    src = _make_data_uri_percent("0 0 24 24")
    html = f'<p>Share on <img src="{src}" aria-label="Mastodon"/> social media.</p>'
    result = gen._classify_svg_elements(html)
    assert _has_icon_class(result), "Icon inside paragraph with sibling text should get capcat-icon"
```

- [ ] **Step 2: Run the tests to confirm they all fail with AttributeError**

```bash
cd /Volumes/DRIVEB/SYNCA/SynologyDrive/_!0A/_!1-LEARNING/_/_!0-CURRENT-LEARNING/_!0START/_!0NEWS/GEMINI-Capcat-copy/Application
pytest tests/unit/test_htmlgen/test_svg_classifier.py -v 2>&1 | head -30
```

Expected: All 10 tests FAIL with `AttributeError: '_classify_svg_elements'` or similar.

- [ ] **Step 3: Commit the failing tests**

```bash
git add tests/unit/test_htmlgen/test_svg_classifier.py
git commit -m "test: add failing tests for SVG icon classification"
```

---

## Task 3: Implement `_classify_svg_elements`

**Files:**
- Modify: `capcat/htmlgen/generator.py`

Add the method to the `ArticleHTMLGenerator` class. Add the necessary imports at the top of the method body (not at module level — keeps the module import footprint unchanged).

The method must:
1. Parse `html_content` with `BeautifulSoup(html_content, "html.parser")`
2. Walk every `<img>` where `src` ends with `.svg` OR `src` starts with `data:image/svg`, AND every inline `<svg>`
3. Score each with the heuristics below
4. If `icon_score > illustration_score`, append `"capcat-icon"` to the element's class list
5. Return `str(soup)`

### Scoring heuristics (implement as helper `_score_svg_element`)

```python
def _score_svg_element(self, el, soup) -> tuple[int, int]:
    """Return (icon_score, illustration_score) for a BeautifulSoup element."""
    icon = 0
    illus = 0

    # --- Extract viewBox dimensions ---
    vb = self._extract_viewbox(el)  # returns (w, h) or None

    if vb:
        w, h = vb
        if w == h:
            icon += 3               # square
        else:
            illus += 4              # non-square
        if w > 200 or h > 200:
            illus += 4              # large
        if w <= 64 and h <= 64:
            icon += 3               # small

    # --- src signal ---
    src = el.get("src", "")
    if src.startswith("data:image/svg"):
        icon += 2

    # --- Accessibility attributes ---
    if el.get("aria-label") or el.get("role") == "img":
        icon += 2

    # --- Parent context ---
    parent = el.parent
    if parent:
        parent_name = getattr(parent, "name", "")
        if parent_name in ("li", "button"):
            icon += 2
        elif parent_name == "a":
            # Only award points if <a> is inside nav/footer/header/li
            ancestors = {getattr(a, "name", "") for a in parent.parents}
            if ancestors & {"nav", "footer", "header", "li"}:
                icon += 2

    # --- Sole child of <p> between sibling <p> elements ---
    if getattr(parent, "name", "") == "p":
        siblings = [s for s in parent.children
                    if not (hasattr(s, "name") and s.name is None
                            and str(s).strip() == "")]
        if len(siblings) == 1:
            # Check siblings of the <p> itself
            p_siblings = [s for s in parent.parent.children
                          if hasattr(s, "name") and s.name == "p" and s is not parent]
            if p_siblings:
                illus += 2

        # Non-whitespace sibling text → inline icon context
        from bs4 import NavigableString
        text_siblings = [s for s in parent.children
                         if isinstance(s, NavigableString) and str(s).strip()]
        if text_siblings:
            icon += 1

    return icon, illus
```

### viewBox extraction helper

```python
def _extract_viewbox(self, el) -> "tuple[float, float] | None":
    """Extract (width, height) from a BeautifulSoup SVG/img element, or None."""
    import re, base64, urllib.parse

    # Inline <svg>: read viewBox attribute directly
    if getattr(el, "name", "") == "svg":
        vb_attr = el.get("viewBox") or el.get("viewbox", "")
        m = re.search(r'[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)', vb_attr)
        if m:
            return float(m.group(1)), float(m.group(2))
        w = el.get("width")
        h = el.get("height")
        if w and h:
            try:
                return float(w), float(h)
            except ValueError:
                pass
        return None

    # <img>: try explicit width/height attrs first
    w_attr = el.get("width")
    h_attr = el.get("height")

    src = el.get("src", "")
    if src.startswith("data:image/svg"):
        # Extract the data portion after the first comma
        comma = src.find(",")
        if comma == -1:
            return None
        data_part = src[comma + 1:]

        if ";base64," in src:
            try:
                decoded = base64.b64decode(data_part).decode("utf-8", errors="replace")
            except Exception:
                decoded = ""
        else:
            decoded = urllib.parse.unquote(data_part)

        vb_match = re.search(
            r'viewBox=["\']?\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)',
            decoded
        )
        if vb_match:
            return float(vb_match.group(3)), float(vb_match.group(4))

    # Fall back to explicit width/height on <img>
    if w_attr and h_attr:
        try:
            return float(w_attr), float(h_attr)
        except ValueError:
            pass

    return None
```

### Main method

```python
def _classify_svg_elements(self, html_content: str) -> str:
    """Classify <img src="*.svg"> and inline <svg> elements as icons or
    illustrations. Appends class 'capcat-icon' to icons. Uses html.parser.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")

    for el in soup.find_all(["img", "svg"]):
        src = el.get("src", "")
        name = getattr(el, "name", "")
        # Only process SVG-related elements
        if name == "svg" or src.endswith(".svg") or src.startswith("data:image/svg"):
            icon_score, illus_score = self._score_svg_element(el, soup)
            if icon_score > illus_score:
                existing = el.get("class") or []
                el["class"] = existing + ["capcat-icon"]

    return str(soup)
```

- [ ] **Step 1: Add imports (inside method bodies, not at module top)**

The helpers use `re`, `base64`, `urllib.parse` — all stdlib, imported inside the methods to avoid polluting the module namespace.

- [ ] **Step 2: Add `_extract_viewbox` to `ArticleHTMLGenerator`**

Place it after `_wrap_source_url_in_div` (definition starts at line ~1575). Copy the code from above exactly.

- [ ] **Step 3: Add `_score_svg_element` to `ArticleHTMLGenerator`**

Place it immediately after `_extract_viewbox`.

- [ ] **Step 4: Add `_classify_svg_elements` to `ArticleHTMLGenerator`**

Place it immediately after `_score_svg_element`.

- [ ] **Step 5: Run tests — expect them to pass now**

```bash
pytest tests/unit/test_htmlgen/test_svg_classifier.py -v
```

Expected: 10/10 PASS.

If any fail, read the failure output carefully. Common issues:
- `_extract_viewbox` not finding the viewBox in a data URI → check the regex groups (groups 3 and 4 are width/height, not 1 and 2)
- `_score_svg_element` returning wrong counts → add a debug `print(icon, illus)` temporarily

- [ ] **Step 6: Commit**

```bash
git add capcat/htmlgen/generator.py
git commit -m "feat: add _classify_svg_elements to ArticleHTMLGenerator"
```

---

## Task 4: Wire into the transformation chain

**Files:**
- Modify: `capcat/htmlgen/generator.py:~597`

Wire the call into `generate_article_html_from_template()` only — the template-based "new, reliable" path. The legacy `generate_article_html()` at line ~460 is NOT updated (it is not used for template rendering).

- [ ] **Step 1: Find the correct call site**

```bash
grep -n "_wrap_source_url_in_div" capcat/htmlgen/generator.py
```

Expected: two lines. The one at ~597 is inside `generate_article_html_from_template()`. The one at ~506 is inside the legacy `generate_article_html()` — leave that one alone.

- [ ] **Step 2: Add the call after `_wrap_source_url_in_div` at line ~597 only**

Before:
```python
            html_content = self._wrap_source_url_in_div(html_content)
```
After:
```python
            html_content = self._wrap_source_url_in_div(html_content)
            html_content = self._classify_svg_elements(html_content)
```

- [ ] **Step 3: Run the full test suite to confirm nothing is broken**

```bash
pytest tests/unit/test_htmlgen/ -v 2>&1 | tail -20
```

Expected: all existing tests still pass, all 10 new tests pass.

- [ ] **Step 4: Commit**

```bash
git add capcat/htmlgen/generator.py
git commit -m "feat: wire _classify_svg_elements into HTML generation chain"
```

---

## Task 5: Reinstall and smoke test

- [ ] **Step 1: Reinstall capcat**

```bash
pipx install -e . --force 2>&1 | tail -3
```

Expected: `installed package capcat X.X.X`

- [ ] **Step 2: Regenerate an existing article that has social share icons**

```bash
capcat single "https://shkspr.mobi/blog/2026/03/bored-of-eating-your-own-dogfood-try-smelling-your-own-farts/" --output /tmp/capcat-icon-test
```

Then open:
`/tmp/capcat-icon-test/html/article.html`

Expected: the Mastodon/Facebook/Reddit share icons appear as small inline images (~1.5em) next to their list items, not as full-width blocks.

- [ ] **Step 3: Version bump and final commit**

```bash
# Edit capcat/__init__.py: bump patch version (e.g. 1.4.2 → 1.4.3)
git add capcat/__init__.py
git commit -m "bump: version to X.X.X"
pipx install -e . --force 2>&1 | tail -3
```
