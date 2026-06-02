# Capcat HTML Output - Typography & Theme Development Reference

This document provides CSS patterns and editorial typography principles for developing Capcat's HTML output themes. Capcat outputs archived news articles and bundles as static HTML files. Themes control reading experience, typographic hierarchy, and visual presentation of that output.

---

## 1. Context: What Capcat Outputs

HTML output from Capcat consists of:

- **Index page** - article cards grid, source labels, bundle metadata
- **Article pages** - long-form prose, headlines, bylines, dates, images, body copy
- **Bundle summary** - multi-source collection overview

Each theme must handle all three page types. Reading comfort and information hierarchy are the primary design goals - these are archival documents for extended reading, not marketing pages.

---

## 2. Fluid Type Scale

Use `clamp()` for all font sizes. This eliminates breakpoints, scales continuously from mobile to wide desktop, and respects browser zoom for accessibility (because the preferred value combines `rem + vw`).

```css
/* Fluid type scale - custom properties on :root */
:root {
  /* step -1 → +5, from mobile min to desktop max */
  --text-sm:   clamp(0.833rem, 0.75rem  + 0.20vw, 0.900rem);
  --text-base: clamp(1.000rem, 0.900rem + 0.25vw, 1.125rem);
  --text-md:   clamp(1.200rem, 1.100rem + 0.40vw, 1.500rem);
  --text-lg:   clamp(1.440rem, 1.200rem + 0.90vw, 2.000rem);
  --text-xl:   clamp(1.728rem, 1.400rem + 1.60vw, 3.000rem);
  --text-2xl:  clamp(2.074rem, 1.600rem + 2.40vw, 4.500rem);
}
```

### Applying the scale to elements

```css
body  { font-size: var(--text-base); }
p     { font-size: var(--text-base); }
small,
.meta,
.caption,
figcaption { font-size: var(--text-sm); }

h4 { font-size: var(--text-md);  line-height: 1.30; }
h3 { font-size: var(--text-lg);  line-height: 1.25; }
h2 { font-size: var(--text-xl);  line-height: 1.15; }
h1 { font-size: var(--text-2xl); line-height: 1.05; }
```

> **Key rule:** Line-height must get tighter as font size increases. Body prose at 1.7; display headings at 1.05-1.10. Never apply body line-height to large display text.

### Recommended tooling for generating scales

- **Utopia** - https://utopia.fyi/type/calculator - two viewports, one ratio, outputs ready-to-paste CSS custom properties. The preferred way to generate the `clamp()` values above for each theme variant.
- **Fluid Type Scale Calculator** (Aleksandr Hovhannisyan) - https://fluid-type-scale.com

---

## 3. Measure - Controlling Line Length

The single most impactful typographic decision for reading comfort. Classic editorial range: **55-75 characters per line**. The `ch` unit approximates one character's width.

```css
/* Article body - the reading column */
article,
.article-body {
  max-inline-size: 65ch;   /* ~65 chars: comfortable long-form read */
  margin-inline: auto;
}

/* Tighter for standfirsts, lede paragraphs, intro text */
.lede,
.standfirst {
  max-inline-size: 55ch;
}

/* Pull quotes and callout blocks - narrow for typographic contrast */
.pullquote,
blockquote {
  max-inline-size: 40ch;
}
```

> `max-inline-size` is the logical property equivalent of `max-width`. Preferred over `max-width` in modern CSS because it respects writing direction.

---

## 4. Vertical Rhythm - The Flow Utility

Andy Bell's "flow" pattern from [Every Layout](https://every-layout.dev). Creates vertical rhythm without fighting cascade specificity. Apply as a utility class on article body containers.

```css
/* Flow utility - consistent vertical spacing between siblings */
.flow { --flow-space: 1em; }

.flow > * + * {
  margin-block-start: var(--flow-space, 1em);
}

/* Override per element type within the flow */
.flow > h2   { --flow-space: 2em;   }
.flow > h3   { --flow-space: 1.75em; }
.flow > pre,
.flow > figure,
.flow > blockquote { --flow-space: 1.5em; }
```

Usage in HTML output templates:

```html
<article class="flow">
  <h1>Article headline</h1>
  <p class="lede">Standfirst or intro paragraph.</p>
  <p>Body copy begins here...</p>
  <h2>Section heading</h2>
  <p>More body copy.</p>
</article>
```

---

## 5. Body Copy Essentials

```css
article p {
  font-size:   var(--text-base);
  line-height: 1.7;                /* 1.6-1.8 for long-form prose */
  font-kerning: normal;
  font-feature-settings: "kern" 1, "liga" 1;
  font-optical-sizing: auto;       /* use optical variants if the font supports them */
}

/* No text-indent after a heading */
article h2 + p,
article h3 + p,
article h4 + p {
  text-indent: 0;
}
```

---

## 6. Heading Tracking (Letter-spacing)

Display headings benefit from negative letter-spacing. Small UI text (meta, captions, labels) benefits from slight positive tracking. Always use `em` so tracking scales with the font size.

```css
h1 { letter-spacing: -0.03em; }
h2 { letter-spacing: -0.02em; }
h3 { letter-spacing: -0.01em; }

small,
.meta,
.caption,
figcaption,
.label {
  letter-spacing: 0.02em;
}
```

---

## 7. Text Wrap - Preventing Orphans

`text-wrap: balance` and `text-wrap: pretty` are now in Baseline (all modern browsers). Use them to eliminate orphan words and uneven headline wrapping.

```css
/* Even line distribution - for headings and pull quotes */
h1, h2, h3, h4,
.pullquote,
.card-title {
  text-wrap: balance;
}

/* Prevents orphan last word in body paragraphs */
p {
  text-wrap: pretty;
  orphans: 3;  /* also applies in print/PDF contexts */
  widows: 3;
}
```

---

## 8. Optical Margin Alignment & Hanging Punctuation

```css
article {
  hanging-punctuation: first last;  /* hang opening/closing quotes into margin */
  text-align: left;                 /* never justify on screen */
}

/* Manual optical pull for blockquote marks if hanging-punctuation is insufficient */
blockquote p::before {
  margin-inline-start: -0.45em;
}
```

---

## 9. Drop Caps

For article first paragraphs - optional, recommended for long-form `default` and `academic` themes.

```css
/* Modern - CSS initial-letter */
.article-body p:first-of-type::first-letter {
  initial-letter: 3;           /* span 3 lines */
  font-weight: bold;
  margin-inline-end: 0.1em;
}

/* Fallback for browsers without initial-letter support */
@supports not (initial-letter: 3) {
  .article-body p:first-of-type::first-letter {
    float: left;
    font-size: 3.5em;
    line-height: 0.85;
    margin: 0.05em 0.12em 0 0;
  }
}
```

---

## 10. OpenType Features

Enable ligatures and proper numeral variants. These improve typographic quality when the chosen font supports them.

```css
body {
  font-feature-settings:
    "liga" 1,   /* standard ligatures: fi, fl, etc. */
    "calt" 1,   /* contextual alternates */
    "kern" 1;   /* kerning pairs */
}

/* Tabular (fixed-width) numbers for article counts, dates, stats */
.tabular-nums,
.article-count,
.date,
time {
  font-variant-numeric: tabular-nums;
}

/* Old-style figures for body prose (if font supports it) */
.prose-nums {
  font-variant-numeric: oldstyle-nums proportional-nums;
}
```

---

## 11. Hyphenation

```css
article p {
  hyphens: auto;                   /* requires lang attribute on <html> */
  hyphenate-limit-chars: 6 3 3;   /* min word length, chars before/after hyphen */
  overflow-wrap: break-word;
}

/* Prevent hyphenation in headings and UI labels */
h1, h2, h3, h4,
.label,
.tag,
.source-name {
  hyphens: none;
  white-space: normal;
}
```

Set language on the HTML element in the output template:
```html
<html lang="en">
```

---

## 12. Font Loading Strategy - Eliminating FOUT

```css
/* Web font declaration */
@font-face {
  font-family: 'ThemeSans';
  src: url('/fonts/theme-sans.woff2') format('woff2');
  font-display: swap;          /* show fallback immediately, swap when loaded */
  font-weight: 100 900;        /* variable font axis range */
  unicode-range: U+0000-00FF;  /* Latin only - reduces file size */
}

/* Metrics-adjusted fallback - reduces layout shift (CLS) during font swap */
@font-face {
  font-family: 'FallbackSans';
  src: local('Arial');
  size-adjust: 96%;            /* match x-height of the web font */
  ascent-override: 95%;
}

body {
  font-family: 'ThemeSans', 'FallbackSans', system-ui, sans-serif;
}
```

> For themes that use system fonts only (e.g. `minimal` theme), skip custom `@font-face` entirely and use the system stack directly - zero FOUT risk and no HTTP requests.

---

## 13. Theme Specifications

The five themes defined in the Capcat TUI menu. Each shares the typographic foundations above but varies in typeface, color, density, and feature set.

### `default` - Clean & Responsive

**Intended use:** General reading, day-to-day archiving  
**Typography:** Inter or system-ui for body; fluid scale, drop caps optional  
**Color:** Light background `#fafaf9`, near-black text `#1c1c1e`  
**Density:** Medium - comfortable card grid on index, generous padding in articles  
**Special features:** Article card grid on index, source color-coding by badge

```css
:root {
  --font-body:     Inter, system-ui, sans-serif;
  --font-heading:  Inter, system-ui, sans-serif;
  --color-bg:      #fafaf9;
  --color-surface: #ffffff;
  --color-text:    #1c1c1e;
  --color-muted:   #6b7280;
  --color-border:  #e5e7eb;
  --color-accent:  #3b82f6;
  --article-width: 65ch;
  --card-radius:   8px;
}
```

---

### `corporate` - Professional

**Intended use:** Business research, sharing with colleagues, professional reports  
**Typography:** System-ui stack, no decorative features, conservative spacing  
**Color:** White background, dark navy headings `#1e293b`, blue accent `#1d4ed8`  
**Density:** High - compact card grid, tighter spacing  
**Special features:** Print-ready stylesheet included, page numbers in `@media print`

```css
:root {
  --font-body:     system-ui, -apple-system, Segoe UI, sans-serif;
  --font-heading:  system-ui, -apple-system, Segoe UI, sans-serif;
  --color-bg:      #ffffff;
  --color-surface: #f8fafc;
  --color-text:    #1e293b;
  --color-muted:   #64748b;
  --color-border:  #cbd5e1;
  --color-accent:  #1d4ed8;
  --article-width: 70ch;
  --card-radius:   4px;
}

@media print {
  body { font-size: 11pt; }
  .no-print { display: none; }
}
```

---

### `academic` - Citation-Ready

**Intended use:** Research archiving, academic reference collections  
**Typography:** Serif body (Georgia or Lora), high contrast, footnote-ready  
**Color:** Off-white `#fffef7`, dark text `#111827`  
**Density:** Wide measure for comfortable scholarly reading, generous leading  
**Special features:** Drop caps on article pages, styled `<cite>` and `<blockquote>`, `hanging-punctuation` enabled

```css
:root {
  --font-body:     Georgia, 'Lora', 'Times New Roman', serif;
  --font-heading:  Georgia, 'Lora', serif;
  --color-bg:      #fffef7;
  --color-surface: #fefce8;
  --color-text:    #111827;
  --color-muted:   #4b5563;
  --color-border:  #d1d5db;
  --color-accent:  #7c3aed;
  --article-width: 68ch;
  --card-radius:   2px;
  --body-leading:  1.8;
}

article p {
  line-height: var(--body-leading, 1.8);
  text-align: left;
  hanging-punctuation: first last;
}
```

---

### `minimal` - Text-Focused

**Intended use:** Distraction-free reading, low-bandwidth contexts, plain output  
**Typography:** System font stack only (no HTTP font requests), reduced decorative CSS  
**Color:** Pure white `#ffffff`, near-black `#111111`  
**Density:** Maximum prose width, no cards on index (list view), no imagery  
**Special features:** Smallest stylesheet footprint; works fully offline with zero external resources

```css
:root {
  --font-body:     system-ui, -apple-system, sans-serif;
  --font-heading:  system-ui, -apple-system, sans-serif;
  --color-bg:      #ffffff;
  --color-text:    #111111;
  --color-muted:   #555555;
  --color-border:  #dddddd;
  --color-accent:  #000000;
  --article-width: 68ch;
}

/* No card grid on index - use a simple article list */
.index-grid {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
```

---

### `dark` - Low-Light Optimized

**Intended use:** Extended reading sessions, evening use, low-light environments  
**Typography:** Inter or system-ui; slightly increased body size for screen readability in dark conditions  
**Color:** Dark surface `#0f172a`, desaturated text `#e2e8f0`, muted accent  
**Density:** Medium - same layout as `default`, inverted palette  
**Special features:** Reduced blue light (avoid pure `#ffffff` text on pure `#000000` - use warm dark backgrounds and slightly warm text)

```css
:root {
  --font-body:     Inter, system-ui, sans-serif;
  --font-heading:  Inter, system-ui, sans-serif;
  --color-bg:      #0f172a;
  --color-surface: #1e293b;
  --color-text:    #e2e8f0;
  --color-muted:   #94a3b8;
  --color-border:  #334155;
  --color-accent:  #60a5fa;
  --article-width: 65ch;
  --card-radius:   8px;
}

/* Avoid pure white for long reading - desaturate */
body {
  color: var(--color-text);          /* #e2e8f0, not #ffffff */
  background-color: var(--color-bg); /* #0f172a, not #000000 */
}

/* Images - reduce harshness */
img {
  opacity: 0.9;
  filter: brightness(0.95);
}
```

---

## 14. Shared Theme Architecture

All themes should extend a single `base.css` and override only variables and theme-specific rules. This keeps maintenance cost low.

```
themes/
  base.css          ← fluid scale, flow utility, measure, all typographic rules
  default.css       ← variable overrides + card grid styles
  corporate.css     ← variable overrides + print styles
  academic.css      ← variable overrides + serif body + drop caps
  minimal.css       ← variable overrides + list index (no grid)
  dark.css          ← variable overrides + image treatment
```

HTML output template loads `base.css` first, then the selected theme:

```html
<link rel="stylesheet" href="./css/base.css">
<link rel="stylesheet" href="./css/{{ theme }}.css">
```

---

## 15. Reference Resources

| Resource | URL | Purpose |
|---|---|---|
| Utopia type calculator | https://utopia.fyi/type/calculator | Generate fluid `clamp()` scales for each theme |
| Fluid Type Scale Calculator | https://fluid-type-scale.com | Alternative generator |
| Every Layout | https://every-layout.dev | Source of flow utility and layout primitives |
| Piccalilli - fluid type tutorial | https://piccalil.li/blog/fluid-typography-with-css-clamp/ | Deep-dive reference |
| Clagnut.com | https://clagnut.com/blog/2395 | Richard Rutter's web typography techniques |
| iA.net/topics | https://ia.net/topics | Live example of type-only editorial design |
| Wakamai Fondue | https://wakamaifondue.com | Inspect OpenType features of any font file |
| Fonts In Use | https://fontsinuse.com | Real-world editorial typography examples |

---

## 16. CSS Checklist per Theme

Before shipping a theme, verify:

- [ ] Fluid type scale uses `rem + vw` preferred value (not `px + vw`) - preserves browser zoom
- [ ] Body measure capped at `65-68ch` on article pages
- [ ] Line-height ≥ 1.6 for body, ≤ 1.15 for display headings
- [ ] `text-wrap: balance` on all headings
- [ ] `text-wrap: pretty` on all body paragraphs
- [ ] `hyphens: auto` on body paragraphs with `lang` attribute on `<html>`
- [ ] `font-optical-sizing: auto` set on body
- [ ] `letter-spacing` negative on headings, slightly positive on captions/meta
- [ ] `hanging-punctuation: first last` on article body (academic, default themes)
- [ ] `font-display: swap` on any custom `@font-face` declarations
- [ ] Fallback font has `size-adjust` to minimise layout shift
- [ ] Dark theme avoids pure `#000000` background and pure `#ffffff` text
- [ ] Print styles present on `corporate` theme
- [ ] All five themes work from the same `base.css` with variable overrides only
