# Accessibility Remediation Plan for Capcat Documentation Website

**Document Version:** 1.0
**Date:** 2026-01-27
**Target WCAG Level:** AA Compliance
**Estimated Total Effort:** 12-16 hours

---

## Executive Summary

This plan addresses 10 distinct accessibility issues identified in the Capcat documentation website, ranging from WCAG Level A failures (critical) to usability enhancements. Issues span image alt text, heading structure, semantic HTML, ARIA attributes, color contrast, keyboard navigation, and interactive element feedback.

**Critical Finding:** The main heading contains truncated/concatenated text ("Defined with natural language processing. Built with large language models.A Minimum viabl") which violates WCAG 1.3.1 (Info and Relationships) and 2.4.6 (Headings and Labels).

**High-Priority Count:** 7 issues requiring immediate attention
**Medium-Priority Count:** 2 usability improvements
**Low-Priority Count:** 1 enhancement

---

## Table of Contents

1. [Critical Issues (WCAG Level A)](#critical-issues)
2. [High Priority Issues (WCAG Level AA)](#high-priority-issues)
3. [Medium Priority Issues (Usability)](#medium-priority-issues)
4. [Low Priority Issues (Enhancements)](#low-priority-issues)
5. [Implementation Phases](#implementation-phases)
6. [Testing Checklist](#testing-checklist)
7. [Success Criteria](#success-criteria)

---

## Critical Issues (WCAG Level A)

### ISSUE #1: Truncated/Concatenated Heading Structure
**WCAG Criteria:** 1.3.1 Info and Relationships (Level A), 2.4.6 Headings and Labels (Level AA)
**Severity:** Critical
**Effort:** 15 minutes
**Files Affected:**
- `/docs/index.html` (lines 114-117)

**Current State:**
```html
<h2 class="NLP-alert">
  Defined with natural language processing. Built with large language
  models.<br />A Minimum viable product.
</h2>
```

**Issue:** Text appears truncated and concatenated, likely due to CSS or rendering issues.

**Fix Required:**
```html
<h2 class="NLP-alert">
  Defined with natural language processing. Built with large language models.
  <br />
  A Minimum Viable Product.
</h2>
```

**Alternative (Semantic):**
```html
<div class="NLP-alert" role="complementary" aria-label="Project status notice">
  <p>Defined with natural language processing. Built with large language models.</p>
  <p>A Minimum Viable Product.</p>
</div>
```

**Testing:**
- Visual inspection in multiple browsers
- Screen reader announcement test (NVDA, JAWS, VoiceOver)
- Verify complete text reads without truncation

---

## High Priority Issues (WCAG Level AA)

### ISSUE #2: Missing/Improper Alt Text on Images
**WCAG Criteria:** 1.1.1 Non-text Content (Level A)
**Severity:** High
**Effort:** 45 minutes
**Files Affected:**
- `/docs/index.html` (lines 162-239, 497, 515, 522)

**Current State - Feature Icons:**
```html
<img src="icons/Command-Line-Mode-icon.svg" alt="Command-Line Mode" />
<img src="icons/Interactive-Menu-icon.svg" alt="Interactive Menu" />
<img src="icons/Bulk-RSS-Fetching-icon.svg" alt="Bulk RSS Fetching" />
```

**Issue:** Alt text repeats visible heading text without describing the icon's visual content.

**Fix Required:**
```html
<img src="icons/Command-Line-Mode-icon.svg"
     alt="Terminal window icon with command prompt" />
<img src="icons/Interactive-Menu-icon.svg"
     alt="Menu icon with checkboxes and selection indicators" />
<img src="icons/Bulk-RSS-Fetching-icon.svg"
     alt="RSS feed icon with multiple streams converging" />
<img src="icons/Local-Markdown-Storage-icon.svg"
     alt="Document folder icon with Markdown symbol" />
<img src="icons/HTML-Generation-icon.svg"
     alt="Web page icon with HTML brackets" />
<img src="icons/Offline-Accessibility-icon.svg"
     alt="Download icon with checkmark indicating local storage" />
<img src="icons/Your-Own-Sources-icon.svg"
     alt="Plus icon with RSS feed symbol for adding sources" />
```

**Current State - Decorative Images:**
```html
<img src="icons/Crowd.svg" alt="Crowd background illustration" />
<img src="icons/Capcat-Cat-Color.svg"
     alt="Capcat mascot is catching the loading ball from the Capcat progress bar indicator. | Illustration by Stayu Kasabov | Stayux.com" />
```

**Issue:**
1. Background crowd image should be decorative (alt="")
2. Mascot alt text contains attribution which should be in caption/credit

**Fix Required:**
```html
<!-- Background is decorative -->
<img src="icons/Crowd.svg" alt="" role="presentation" />

<!-- Mascot with proper description -->
<img src="icons/Capcat-Cat-Color.svg"
     alt="Capcat mascot catching a loading ball from progress bar" />
<p class="image-credit" aria-label="Image attribution">
  Illustration by Stayu Kasabov | Stayux.com
</p>
```

**Testing:**
- Screen reader verification for each image
- Ensure decorative images are skipped
- Verify functional images convey purpose

---

### ISSUE #3: Code Blocks Lack Semantic Structure
**WCAG Criteria:** 1.3.1 Info and Relationships (Level A)
**Severity:** High
**Effort:** 30 minutes
**Files Affected:**
- `/docs/index.html` (lines 100-108, 532-542)
- All documentation pages with code examples

**Current State:**
```html
<div class="hero-demo">
  <pre class="code-demo"><code>$ ./capcat bundle tech --count 30

Fetching from 3 sources in bundle 'tech'
◯ STARTING HACKER NEWS (30 ITEMS)
...</code></pre>
</div>
```

**Issue:** No programmatic label indicating purpose or language.

**Fix Required:**
```html
<div class="hero-demo">
  <pre class="code-demo" role="region" aria-labelledby="demo-heading">
    <code class="language-bash">$ ./capcat bundle tech --count 30

Fetching from 3 sources in bundle 'tech'
◯ STARTING HACKER NEWS (30 ITEMS)
...</code>
  </pre>
  <button class="copy-code-btn"
          aria-label="Copy command to clipboard">Copy</button>
</div>

<span id="demo-heading" class="visually-hidden">Example command-line usage</span>
```

**Installation Steps Code:**
```html
<div class="install-step">
  <h3>1. Clone Repository</h3>
  <pre role="region" aria-label="Git clone command">
    <code class="language-bash">git clone https://github.com/stayukasabov/capcat.git</code>
  </pre>
  <button class="copy-code-btn"
          aria-label="Copy git clone command">Copy</button>
</div>
```

**CSS Addition Required:**
```css
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

**Testing:**
- Screen reader navigation through code blocks
- Verify labels are announced
- Test copy button functionality with keyboard

---

### ISSUE #4: Color Contrast Failures
**WCAG Criteria:** 1.4.3 Contrast (Minimum) (Level AA)
**Severity:** High
**Effort:** 1 hour
**Files Affected:**
- `/docs/css/main.css`
- `/docs/css/design-system.css`

**Current State - Orange Heading on Beige:**
```css
.NLP-alert {
  color: var(--accent-primary);  /* Orange */
  background-color: var(--bg-color);  /* Beige/cream */
}
```

**Issue:** Likely fails 4.5:1 ratio requirement for normal text.

**Testing Required:**
```bash
# Use browser DevTools or online contrast checker
# Test combinations:
# 1. Orange text (#F1540D) on beige background
# 2. Gray footer text on background
# 3. Link colors on backgrounds
```

**Potential Fixes:**

**Option A: Darken orange text**
```css
.NLP-alert {
  color: #C74300;  /* Darker orange for contrast */
  /* OR increase font-weight to make it large text (3:1 ratio acceptable) */
  font-weight: 700;
}
```

**Option B: Add background contrast**
```css
.NLP-alert {
  background-color: #FFF;
  padding: var(--space-md);
  border-left: 4px solid var(--brand-orange);
}
```

**Footer Text:**
```css
.footer-credit p {
  color: #666666;  /* Test contrast against footer bg */
}

/* If fails, darken to: */
.footer-credit p {
  color: #595959;  /* Ensures 4.5:1 minimum */
}
```

**Testing:**
- Use WebAIM Contrast Checker
- Test all text/background combinations
- Verify in high contrast mode

---

### ISSUE #5: Navigation Menu Missing aria-expanded
**WCAG Criteria:** 4.1.2 Name, Role, Value (Level A)
**Severity:** High
**Effort:** 15 minutes
**Files Affected:**
- `/docs/_includes/header.html` (line 78)
- `/docs/js/main.js` (lines 20-74)

**Current State:**
```html
<button class="mobile-menu-toggle" aria-label="Toggle menu">
  <span></span>
  <span></span>
  <span></span>
</button>
```

```javascript
// main.js already implements this correctly (lines 41, 48)
toggle.setAttribute("aria-expanded", "true");
toggle.setAttribute("aria-expanded", "false");
```

**Issue:** HTML initial state missing aria-expanded.

**Fix Required:**
```html
<button class="mobile-menu-toggle"
        aria-label="Toggle menu"
        aria-expanded="false"
        aria-controls="main-navigation">
  <span></span>
  <span></span>
  <span></span>
</button>

<ul class="nav-links" id="main-navigation">
  <!-- nav items -->
</ul>
```

**JavaScript Update:**
```javascript
// No changes needed - already correct in main.js
```

**Testing:**
- Screen reader announcement of expanded/collapsed state
- Keyboard navigation (Tab, Enter, Escape)
- Touch target size minimum 44×44px

---

### ISSUE #6: Missing Skip-to-Main-Content Link
**WCAG Criteria:** 2.4.1 Bypass Blocks (Level A)
**Severity:** High
**Effort:** 20 minutes
**Files Affected:**
- `/docs/_includes/header.html` (add after opening <body>)
- `/docs/index.html` (add main id)
- `/docs/css/main.css`

**Fix Required - HTML:**
```html
<!-- Add immediately after <body> tag in all pages -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<header class="site-header">
  <!-- existing header -->
</header>

<!-- Add id to main content area -->
<section id="main-content" class="hero">
  <!-- content -->
</section>

<!-- OR if using <main> element -->
<main id="main-content">
  <!-- all page content -->
</main>
```

**Fix Required - CSS:**
```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--brand-orange);
  color: white;
  padding: var(--space-sm) var(--space-md);
  text-decoration: none;
  font-weight: 700;
  z-index: 9999;
  transition: top 0.2s ease-in;
}

.skip-link:focus {
  top: 0;
}
```

**Testing:**
- Tab immediately on page load
- Verify link appears visually
- Click and verify focus moves to main content
- Screen reader announcement

---

### ISSUE #7: Visual Numbered Lists Instead of Semantic <ol>
**WCAG Criteria:** 1.3.1 Info and Relationships (Level A)
**Severity:** High
**Effort:** 30 minutes
**Files Affected:**
- `/docs/index.html` (lines 250-304 - "How Capcat Works" section)

**Current State:**
```html
<div class="workflow-step">
  <div class="step-number">1</div>
  <div class="step-content">
    <h3>Choose Your Interface</h3>
    <p>Start with CLI for speed or TUI for visual exploration.</p>
  </div>
</div>
<!-- Repeated for steps 2-5 -->
```

**Issue:** Visually numbered but not semantically an ordered list.

**Fix Required:**
```html
<ol class="workflow" aria-label="How Capcat works in 5 steps">
  <li class="workflow-step">
    <div class="step-content">
      <h3>Choose Your Interface</h3>
      <p>Start with CLI for speed or TUI for visual exploration.
         Both provide complete functionality.</p>
    </div>
  </li>
  <li class="workflow-step">
    <div class="step-content">
      <h3>Select Sources</h3>
      <p>Pick from 11 configured sources (Hacker News, BBC, Guardian,
         Nature, etc.) or use predefined bundles.</p>
    </div>
  </li>
  <!-- Continue for steps 3-5 -->
</ol>
```

**CSS Update:**
```css
.workflow {
  list-style: none;
  counter-reset: workflow-counter;
}

.workflow-step {
  counter-increment: workflow-counter;
  position: relative;
}

.workflow-step::before {
  content: counter(workflow-counter);
  /* Copy existing .step-number styles */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--brand-orange);
  color: white;
  border-radius: 50%;
  font-size: var(--text-large);
  font-weight: 700;
  margin-bottom: var(--space-sm);
}
```

**Testing:**
- Screen reader announcement of list with 5 items
- Visual appearance unchanged
- Proper semantic structure in accessibility tree

---

## Medium Priority Issues (Usability)

### ISSUE #8: Copy Buttons Need Better Feedback
**WCAG Criteria:** 3.3.1 Error Identification (Level A) - Applied to success feedback
**Severity:** Medium
**Effort:** 45 minutes
**Files Affected:**
- `/docs/js/main.js` (initCodeCopy function)
- `/docs/css/main.css`

**Current State:**
```javascript
function initCodeCopy() {
  // Likely exists but needs verification and enhancement
}
```

**Fix Required:**

**JavaScript Enhancement:**
```javascript
function initCodeCopy() {
  const codeBlocks = document.querySelectorAll('pre code');

  codeBlocks.forEach((block) => {
    const button = document.createElement('button');
    button.className = 'copy-code-btn';
    button.setAttribute('aria-label', 'Copy code to clipboard');
    button.innerHTML = `
      <svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16">
        <path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25v-7.5z"/>
        <path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25v-7.5zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25h-7.5z"/>
      </svg>
      <span class="button-text">Copy</span>
    `;

    const wrapper = block.parentElement;
    wrapper.style.position = 'relative';
    wrapper.appendChild(button);

    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(block.textContent);

        // Visual feedback
        button.classList.add('copied');
        const originalText = button.querySelector('.button-text').textContent;
        button.querySelector('.button-text').textContent = 'Copied!';
        button.setAttribute('aria-label', 'Code copied to clipboard');

        // Announce to screen readers
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'visually-hidden';
        announcement.textContent = 'Code copied to clipboard';
        document.body.appendChild(announcement);

        // Reset after 2 seconds
        setTimeout(() => {
          button.classList.remove('copied');
          button.querySelector('.button-text').textContent = originalText;
          button.setAttribute('aria-label', 'Copy code to clipboard');
          document.body.removeChild(announcement);
        }, 2000);

      } catch (err) {
        button.querySelector('.button-text').textContent = 'Failed';
        button.setAttribute('aria-label', 'Copy failed');

        setTimeout(() => {
          button.querySelector('.button-text').textContent = 'Copy';
          button.setAttribute('aria-label', 'Copy code to clipboard');
        }, 2000);
      }
    });
  });
}
```

**CSS Enhancement:**
```css
.copy-code-btn {
  position: absolute;
  top: var(--space-xs);
  right: var(--space-xs);
  background: var(--imprint-dark);
  color: white;
  border: 1px solid var(--imprint-medium);
  border-radius: var(--radius-sm);
  padding: var(--space-xs) var(--space-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: var(--text-small);
  transition: all 0.2s ease;
}

.copy-code-btn:hover {
  background: var(--brand-orange);
  border-color: var(--brand-orange);
}

.copy-code-btn:focus {
  outline: 2px solid var(--brand-orange);
  outline-offset: 2px;
}

.copy-code-btn.copied {
  background: #28a745;
  border-color: #28a745;
}

.copy-code-btn svg {
  flex-shrink: 0;
}
```

**Testing:**
- Keyboard activation (Tab + Enter)
- Screen reader announcement of success
- Visual feedback visible
- Touch target at least 44×44px

---

### ISSUE #9: Landmark Regions Without Labels
**WCAG Criteria:** 2.4.1 Bypass Blocks (Level A), 4.1.2 Name, Role, Value (Level A)
**Severity:** Medium
**Effort:** 20 minutes
**Files Affected:**
- `/docs/index.html` (multiple sections)
- All documentation pages

**Current State:**
```html
<section id="features" class="section section-alt">
  <!-- content -->
</section>

<section id="how-it-works" class="section">
  <!-- content -->
</section>
```

**Issue:** Multiple generic <section> elements without descriptive labels.

**Fix Required:**
```html
<section id="features"
         class="section section-alt"
         aria-labelledby="features-heading">
  <div class="container">
    <h2 id="features-heading">Two Complete Interfaces, One Powerful Backend</h2>
    <!-- content -->
  </div>
</section>

<section id="how-it-works"
         class="section"
         aria-labelledby="how-heading">
  <div class="container">
    <h2 id="how-heading">How Capcat Works</h2>
    <!-- content -->
  </div>
</section>

<section id="tutorials"
         class="section"
         aria-labelledby="tutorials-heading">
  <div class="container">
    <h2 id="tutorials-heading">Tutorials & Documentation</h2>
    <!-- content -->
  </div>
</section>

<!-- For sections without visible headings -->
<section id="problem"
         class="section"
         aria-label="Problem statement: Information overload">
  <!-- content -->
</section>
```

**Testing:**
- Screen reader landmark navigation (NVDA: D key, JAWS: ; key)
- Verify each section has unique label
- Test landmark list (NVDA: Insert+F7)

---

## Low Priority Issues (Enhancements)

### ISSUE #10: Repeated Link Text Causing Confusion
**WCAG Criteria:** 2.4.4 Link Purpose (In Context) (Level A) - Best Practice Violation
**Severity:** Low
**Effort:** 30 minutes
**Files Affected:**
- `/docs/index.html` (lines 357-417 - Tutorials section)

**Current State:**
```html
<!-- Interactive Menu column -->
<a href="docs/tutorials/user/04-managing-sources.html"
   title="Add, remove, organize sources">Managing Your Sources</a>

<!-- CLI Commands column (duplicate link text) -->
<a href="docs/tutorials/user/04-managing-sources.html"
   title="Add, remove, organize sources">Managing Your Sources</a>
```

**Issue:** Same link text appears twice, causing confusion for screen reader users navigating by links list.

**Fix Required:**
```html
<div class="tutorial-grid">
  <div class="tutorial-card">
    <h3>Interactive Menu</h3>
    <ul>
      <li>
        <a href="docs/tutorials/user/03-interactive-mode.html"
           title="Visual menu system guide">
          Interactive Mode Guide
        </a>
      </li>
      <li>
        <a href="docs/tutorials/user/02-daily-workflow.html"
           title="Daily news collection">
          Daily News Collection Workflow
        </a>
      </li>
      <li>
        <a href="docs/tutorials/user/04-managing-sources.html"
           title="Add, remove, organize sources in interactive mode">
          Managing Your Sources (Interactive)
        </a>
      </li>
      <li>
        <a href="docs/tutorials/user/05-bundles.html"
           title="Group sources efficiently">
          Organizing with Bundles
        </a>
      </li>
    </ul>
  </div>

  <div class="tutorial-card">
    <h3>CLI Commands</h3>
    <ul>
      <li>
        <a href="docs/tutorials/user/01-getting-started.html"
           title="Get started in 5 minutes">
          First 5 Minutes with Capcat
        </a>
      </li>
      <li>
        <a href="docs/tutorials/user/02-daily-workflow.html"
           title="Daily news collection via CLI">
          Daily Workflow (CLI)
        </a>
      </li>
      <li>
        <a href="docs/tutorials/user/04-managing-sources.html"
           title="Add, remove, organize sources via command line">
          Managing Sources (CLI)
        </a>
      </li>
      <li>
        <a href="docs/tutorials/user/05-bundles.html"
           title="Group sources efficiently with CLI commands">
          Organizing Bundles (CLI)
        </a>
      </li>
    </ul>
  </div>

  <div class="tutorial-card">
    <h3>Advanced Topics</h3>
    <ul>
      <!-- unique links, no changes needed -->
    </ul>
  </div>
</div>
```

**Testing:**
- Screen reader links list (NVDA: Insert+F7 → Links tab)
- Verify each link is distinguishable
- Context still clear when read in isolation

---

## Implementation Phases

### Phase 1: Critical Fixes (Day 1 - 2 hours)
**Priority:** Immediate
**Issues:** #1, #5, #6

1. Fix truncated heading text
2. Add aria-expanded to mobile menu
3. Implement skip-to-main-content link

**Deliverable:** Core WCAG Level A compliance restored

---

### Phase 2: Image Accessibility (Day 2 - 1.5 hours)
**Priority:** High
**Issues:** #2

1. Audit all images across all pages
2. Write descriptive alt text for functional images
3. Mark decorative images with alt="" and role="presentation"
4. Move attribution text outside alt attributes

**Deliverable:** All images properly described or marked decorative

---

### Phase 3: Semantic Structure (Day 2-3 - 2 hours)
**Priority:** High
**Issues:** #3, #7

1. Add semantic labels to code blocks
2. Implement visually-hidden class
3. Convert visual numbered list to semantic <ol>
4. Update CSS to maintain visual appearance

**Deliverable:** Proper HTML5 semantic structure throughout

---

### Phase 4: Color Contrast Remediation (Day 3 - 1.5 hours)
**Priority:** High
**Issues:** #4

1. Audit all text/background combinations
2. Test contrast ratios with automated tools
3. Adjust colors or weights to meet 4.5:1 minimum
4. Verify in high contrast mode

**Deliverable:** All text meets WCAG AA contrast requirements

---

### Phase 5: Interactive Enhancements (Day 4 - 2 hours)
**Priority:** Medium
**Issues:** #8, #9

1. Implement enhanced copy button feedback
2. Add ARIA live regions for announcements
3. Label all landmark regions
4. Add focus indicators where missing

**Deliverable:** Enhanced interactive experience for assistive tech users

---

### Phase 6: Link Optimization (Day 5 - 30 minutes)
**Priority:** Low
**Issues:** #10

1. Differentiate repeated link text
2. Enhance title attributes for clarity
3. Test in screen reader links list

**Deliverable:** All links uniquely identifiable

---

## Testing Checklist

### Automated Testing
- [ ] Run axe DevTools on all pages
- [ ] Run WAVE WebAIM evaluation
- [ ] Run Lighthouse accessibility audit
- [ ] Validate HTML with W3C validator
- [ ] Test color contrast with WebAIM checker

### Screen Reader Testing
- [ ] NVDA (Windows) - Latest version
  - [ ] Navigate by headings (H key)
  - [ ] Navigate by landmarks (D key)
  - [ ] Navigate by links (K key)
  - [ ] List all links (Insert+F7)
  - [ ] List all headings (Insert+F7)
- [ ] JAWS (Windows) - Latest version
  - [ ] Same tests as NVDA
- [ ] VoiceOver (macOS) - Latest version
  - [ ] Rotor navigation (Cmd+U)
  - [ ] Web item navigation

### Keyboard Testing
- [ ] Tab through entire page
- [ ] Verify visible focus indicators
- [ ] Test mobile menu (Tab, Enter, Escape)
- [ ] Test skip link (first Tab)
- [ ] Test all interactive elements without mouse
- [ ] Verify no keyboard traps

### Visual Testing
- [ ] Zoom to 200% - no content loss
- [ ] Zoom to 400% - acceptable layout
- [ ] High contrast mode (Windows)
- [ ] Dark mode (if supported)
- [ ] Test in multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test responsive layouts (mobile, tablet, desktop)

### Semantic Testing
- [ ] Inspect accessibility tree in DevTools
- [ ] Verify heading hierarchy (no skipped levels)
- [ ] Verify landmark structure
- [ ] Verify ARIA attributes in use
- [ ] Verify form labels (if applicable)

---

## Success Criteria

### Level A Compliance (Required)
- [ ] All images have appropriate alt text or are marked decorative
- [ ] All form inputs have associated labels
- [ ] Heading hierarchy is logical (no skipped levels)
- [ ] Skip navigation link is present and functional
- [ ] Color is not the only means of conveying information
- [ ] All functionality available via keyboard
- [ ] No keyboard traps exist
- [ ] Page has valid HTML5 structure
- [ ] ARIA attributes used correctly
- [ ] Time limits have accessible controls (N/A for this site)

### Level AA Compliance (Target)
- [ ] Color contrast meets 4.5:1 for normal text
- [ ] Color contrast meets 3:1 for large text (18pt+ or 14pt+ bold)
- [ ] Focus indicators visible and meet contrast requirements
- [ ] Text can be resized to 200% without loss of content
- [ ] Images of text avoided (or meet criteria)
- [ ] Consistent navigation across pages
- [ ] Consistent identification of components
- [ ] Headings and labels are descriptive
- [ ] Focus order is logical and intuitive
- [ ] Link purpose is clear from link text or context

### Functional Criteria
- [ ] Screen reader users can complete all tasks
- [ ] Keyboard-only users can complete all tasks
- [ ] Mobile screen reader users can navigate effectively
- [ ] High contrast mode users can read all content
- [ ] Magnification users can access all content at 200% zoom

### Automated Scan Criteria
- [ ] axe DevTools: 0 violations
- [ ] WAVE: 0 errors, <5 alerts
- [ ] Lighthouse accessibility: 95+ score
- [ ] HTML validator: 0 errors

---

## File Change Summary

### Files Requiring Updates

**Templates:**
- `/docs/index.html` - 8 issues
- `/docs/_includes/header.html` - 2 issues
- `/docs/_includes/footer.html` - Audit for contrast
- All `/docs/docs/*.html` pages - Apply fixes universally

**Stylesheets:**
- `/docs/css/main.css` - Add styles for skip link, visually-hidden, copy buttons, workflow list
- `/docs/css/design-system.css` - Audit and fix color contrast in variables

**Scripts:**
- `/docs/js/main.js` - Enhance copy button feedback function

**New Files:**
- None required (all fixes modify existing files)

---

## Before/After Examples

### Example 1: Code Block Accessibility

**Before:**
```html
<pre class="code-demo"><code>$ ./capcat bundle tech --count 30</code></pre>
```

**After:**
```html
<pre class="code-demo" role="region" aria-label="Example command-line usage">
  <code class="language-bash">$ ./capcat bundle tech --count 30</code>
</pre>
<button class="copy-code-btn" aria-label="Copy command to clipboard">Copy</button>
```

**Screen Reader Experience:**
- Before: "Code block, dollar capcat bundle tech..."
- After: "Region, Example command-line usage. Code block, bash. Dollar capcat bundle tech... Copy button"

---

### Example 2: Workflow List Semantics

**Before:**
```html
<div class="workflow">
  <div class="workflow-step">
    <div class="step-number">1</div>
    <div class="step-content">
      <h3>Choose Your Interface</h3>
    </div>
  </div>
  <!-- 4 more divs -->
</div>
```

**After:**
```html
<ol class="workflow" aria-label="How Capcat works in 5 steps">
  <li class="workflow-step">
    <div class="step-content">
      <h3>Choose Your Interface</h3>
    </div>
  </li>
  <!-- 4 more list items -->
</ol>
```

**Screen Reader Experience:**
- Before: "Choose Your Interface, heading level 3" (no list context)
- After: "List, How Capcat works in 5 steps, 5 items. Item 1 of 5. Choose Your Interface, heading level 3"

---

### Example 3: Image Alt Text

**Before:**
```html
<img src="icons/Command-Line-Mode-icon.svg" alt="Command-Line Mode" />
```

**After:**
```html
<img src="icons/Command-Line-Mode-icon.svg"
     alt="Terminal window icon with command prompt" />
```

**Screen Reader Experience:**
- Before: "Command-Line Mode, graphic" (redundant with visible heading)
- After: "Terminal window icon with command prompt, graphic" (describes visual)

---

## Maintenance Guidelines

### Ongoing Accessibility Practices

1. **New Content Checklist:**
   - [ ] All images have alt text or are marked decorative
   - [ ] Headings follow logical hierarchy
   - [ ] Links have descriptive text
   - [ ] Code blocks have semantic labels
   - [ ] Color contrast checked

2. **Pre-Deployment Testing:**
   - [ ] Run axe DevTools scan
   - [ ] Tab through page with keyboard
   - [ ] Test with one screen reader

3. **Quarterly Audits:**
   - [ ] Full WCAG AA compliance check
   - [ ] Test with multiple assistive technologies
   - [ ] Review and update this plan

4. **Training:**
   - [ ] Share this plan with all content contributors
   - [ ] Provide examples of accessible patterns
   - [ ] Document accessible component library

---

## Resources

### Tools
- **axe DevTools:** https://www.deque.com/axe/devtools/
- **WAVE:** https://wave.webaim.org/
- **Color Contrast Checker:** https://webaim.org/resources/contrastchecker/
- **HTML Validator:** https://validator.w3.org/
- **Screen Readers:**
  - NVDA (Free): https://www.nvaccess.org/
  - JAWS (Trial): https://www.freedomscientific.com/
  - VoiceOver (Built-in macOS/iOS)

### Guidelines
- **WCAG 2.1:** https://www.w3.org/WAI/WCAG21/quickref/
- **ARIA Authoring Practices:** https://www.w3.org/WAI/ARIA/apg/
- **WebAIM:** https://webaim.org/articles/

### Testing Guides
- **NVDA Keyboard Shortcuts:** https://dequeuniversity.com/screenreaders/nvda-keyboard-shortcuts
- **JAWS Keyboard Shortcuts:** https://dequeuniversity.com/screenreaders/jaws-keyboard-shortcuts
- **VoiceOver Gestures:** https://dequeuniversity.com/screenreaders/voiceover-ios-shortcuts

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-27 | TDD Orchestrator | Initial comprehensive remediation plan |

---

**End of Accessibility Remediation Plan**
