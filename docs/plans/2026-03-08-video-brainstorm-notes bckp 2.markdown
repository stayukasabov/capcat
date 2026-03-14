# Capcat Video Ad — Brainstorm Working Notes

> Add your notes under any section. Prefix with `NOTE:`. Claude will refine based on your input.

---

## Layout

- Canvas: 1920×1080px, 30fps
- Illustration zone: top 60% (648px)
- Text zone: bottom 40% (432px)
- Short phrases (≤5 words): 52px, Source Serif 4 Regular
- Long phrases (≥6 words): 38px, Source Serif 4 Regular
- Text animation: typewriter left to right, per line

**Your notes:**


---

## Visual Direction

Derived from `Video/public/design-system.css` and capcat.org.

- Background: `#faf5ee` (paper) — warm cream, throughout all scenes
- Text: `#221717` (imprint) — near-black ink
- Accent: `#f1540d` (orange-500) — primary brand orange
- Accent light: `#ff9463` (orange-400)
- Muted: `#827c7c` (imprint-muted)
- Dark (terminal / fade out): `#1a1212`
- Font: Source Serif 4 (weights 300–700 available locally)
- Mono font: SF Mono / Courier New (terminal scenes)
- Feeling: warm editorial, clean, craft. Not flashy. Product-confident.

**Your notes:**
Create a diferent scene in the timeline for each sentence / illustration combination. We should be abble to edit this with precision.

---

## Available Illustration Assets (`Video/ILLUSTRATION/`)

These replace any generic suggestions in the scene tables below.

| File | Used in |
|------|---------|
| `Capcat-Cat-Color.svg` | Scene 5, beats 2–3 only |
| `Crowd.svg` | Scene 5, beat 3 (behind cat) |
| `2023_Obsidian_logo.svg` | Scene 1, beat 8 |
| `Command-Line-Mode-icon.svg` | Scene 6, beat 1 |
| `Interactive-Menu-icon.svg` | Scene 6, beat 2 (alongside TUI) |
| `Bulk-RSS-Fetching-icon.svg` | Scene 6, beat 3 |
| `Local-Markdown-Storage-icon.svg` | Scene 4 beat 7, Scene 6 beat 4 |
| `HTML-Generation-icon.svg` | Scene 4, beat 10 |
| `Offline-Accessibility-icon.svg` | Scene 6, beat 5 |
| `Your-Own-Sources-icon.svg` | TBD — which scene? |
| `Capcat-Logo.svg` | TBD — which scene? |

**Your notes:**
Your-Own-Sources-icon. IGNORE. WE DONT USE IT HERE.
Capcat-Logo.svg - THE FINAL SECTION BEFORE CLOSING OUT TO DARK

---

## Cat Mascot

- Appears ONLY in Scene 5, beats 2 and 3
- Enters from the LEFT with blur + elastic spring, stops at center
- Size and composition: reference the capcat.org hero illustration (cat is large, centered, crowd fills background behind)
- Crowd (`Crowd.svg`) is hidden until beat 3, then reveals from center behind the cat
- No cat in any other scene

**Your notes:**


---

## Scene 1 — Browsing Workflow

| # | Text | Illustration | Animation | Confirmed |
|---|------|-------------|-----------|-----------|
| 1 | "This is my browsing workflow" | CSS-drawn Chrome window (title bar, URL bar, 3 traffic dots) | Window scales in from 0, spring entrance | |
| 2 | "Open a website" | Abstract website inside browser: colored blocks (nav, hero, article cards) | Content fades in inside browser frame | |
| 3 | "Scan" | Scrollbar indicator, page content scrolls upward | `interpolate` scroll Y over 1s | |
| 4 | "Choose article" | Orange highlight border on one card, cursor dot moves to it | Cursor animates to card, border pulses | |
| 5 | "Read" | 8 horizontal lines draw left→right inside card | Width 0→100% per line, 80ms stagger | |
| 6 | "Bookmark" | Browser chrome bookmark star fills orange | Star fill interpolates empty→orange | |
| 7 | "If it has added value" | Browser stays static | Slight scale pulse 1→1.02→1 | |
| 8 | "Clip with Obsidian" | `2023_Obsidian_logo.svg` fades over browser, browser background crossfades to Obsidian purple `#7c3aed` | Background-color crossfade, logo fades in over browser | |

**Your notes:**


---

## Scene 2 — The Problem (Digging)

| # | Text | Illustration | Animation | Confirmed |
|---|------|-------------|-----------|-----------|
| 1 | "I have to dig into the bookmarks and clippings" | Chaotic pile of folders/bookmarks, slightly rotated | Folders rain from top, stack with random rotations | |
| 2 | "To label" | Label tag SVG attaches to top folder | Tag slides in from right | |
| 3 | "Tag" | `#` hashtag symbol overlaps the stack | Scales in with overshoot spring | |
| 4 | "And organize" | Cursor tries to drag folder — it slips back | Folder translates, spring returns to start — 2 cycles | |

**Your notes:**


---

## Scene 3 — Still Missing

| # | Text | Illustration | Animation | Confirmed |
|---|------|-------------|-----------|-----------|
| 1 | "And I am still missing valuable information" | Magnifying glass sweeps across empty space, nothing found | Glass sweeps left→right, invisible target | |
| 2 | "Every day" | Calendar flipping 3 pages, days incrementing | `rotateX` 0→-90°→next page, 3 cycles | |

**Your notes:**


---

## Scene 4 — The Solution / File-First Model

| # | Text | Illustration | Animation | Confirmed |
|---|------|-------------|-----------|-----------|
| 1 | "What if I capture first" | Hand opening to catch falling dots/stars | Items fall, hand closes — spring | |
| 2 | "Catalogue later" | Filing cabinet drawer slides open | `translateX` slides out | |
| 3 | "Date" | Date stamp onto document | Stamp scale 0→1.1→1, ink splat effect | |
| 4 | "Source" | Chain-link / URL bar icon | Links connect left→right | |
| 5 | "A folder with a title" | Folder icon, title text types on tab | Folder springs in, text typewriters on tab | |
| 6 | "Structure before I even decide what matters" | Tree diagram draws itself (3 nodes, 2 levels) | SVG `stroke-dashoffset` animates | |
| 7 | "Markdown files with embedded images" | `Local-Markdown-Storage-icon.svg` with image thumbnail inset | Icon springs in, thumbnail fades inside | |
| 8 | "Clean data for Obsidian graph" | Obsidian graph: dots + connecting lines | Nodes spring in, edges draw via `stroke-dashoffset` | |
| 9 | "Workflow and input for any LLM" | Circuit/brain icon → arrow → chat bubble | Arrow draws from source to bubble | |
| 10 | "HTML version with Dark and Light Theme" | `HTML-Generation-icon.svg` + split dark/light browser halves | Halves slide apart from center | |
| 11 | "Plus Code Coloring" | Code block with syntax-highlighted tokens | Tokens stagger in, colored per type | |
| 12 | "Ready to share" | Share icon, concentric ripple | Circles expand from icon | |
| 13 | "Quick to Archive" | ZIP folder closes with checkmark | Zipper-close motion + checkmark scale | |
| 14 | "Easy to Read" | Open book, clean text lines appear | Book cover rotates open, lines draw in | |

**Your notes:**


---

## Scene 5 — Product Reveal

| # | Text | Illustration | Animation | Confirmed |
|---|------|-------------|-----------|-----------|
| 1 | "So I created it" | Dark radial vignette expands from center | `radial-gradient` grows, background dims | |
| 2 | "Capcat" | `Capcat-Cat-Color.svg` — full reveal | Enters from LEFT with motion blur + elastic spring, settles at center | ✓ |
| 3 | "Capcat?" | `Crowd.svg` — behind cat | Crowd reveals from center behind cat, fast spring `translateY` | ✓ |

Reference: capcat.org hero composition — cat large, centered, crowd fills background.

**Your notes:**


---

## Scene 6 — Features

| # | Text | Illustration | Animation | Confirmed |
|---|------|-------------|-----------|-----------|
| 1 | "Command Line mode" | `Command-Line-Mode-icon.svg` + terminal types `./capcat fetch hn --count 5` | Icon springs in, typewriter 3 chars/frame | |
| 2 | "Interactive menu" | `Interactive-Menu-icon.svg` + full TUI below (see exact format) | Icon springs in, TUI renders line by line, triangle pointer moves down through all options | ✓ |
| 3 | "Bulk RSS fetching" | `Bulk-RSS-Fetching-icon.svg` + exact progress display (see format) | Icon springs in, spinner rotates, progress animates | ✓ |
| 4 | "Local Markdown storage" | `Local-Markdown-Storage-icon.svg` | Spring scale entrance | ✓ |
| 5 | "Offline Accessibility" | `Offline-Accessibility-icon.svg` | Spring scale entrance | ✓ |

### Scene 6 Beat 2 — Exact TUI Format

```
       ____
     / ____|                     _
    | |     __ _ _ __   ___ __ _| |_
    | |    / _  |  _ \ / __/ _  | __|
    | |___| (_| | |_) | (_| (_| | |_
     \_____\__,_|  __/ \___\__,_|\__|
                | |
                |_|

   What would you like me to do?
   (Use arrow keys to navigate)
 ▶ Catch articles from a bundle of sources
   Catch articles from a list of sources
   Catch from a single source
   Catch a single article by URL
   Manage Sources (add/remove/configure)
   Exit
```

Triangle `▶` moves down through all options one by one.

### Scene 6 Beat 3 — Exact Progress Format

```
◒ CATCHING ▶  NATURE ◎ ◎ ◎ ◎ ◎ ◎  5/27 (14.8%) (COMPLETE)
```

Animation progression:
```
◓ CATCHING ▶  NATURE ◉ ◉ ◉ ◉ ◎ ◎  20/27 (72.2%) (CONVERTING)
```

- Spinner character rotates: `◒ → ◓ → ◔ → ◕ → ◒` (cycle)
- Dots fill left to right: `◎` empty → `◉` filled
- Counter increments: `n/27 (x%)`
- Status text changes: STARTING → FETCHING → CONVERTING → COMPLETE

**Your notes:**


---

## Scene 7 — Outro

| # | Text | Illustration | Animation | Confirmed |
|---|------|-------------|-----------|-----------|
| 1 | "Archive with confidence" | ZIP file icon closes (zipping animation) — sync to zipping sound in audio | Zipper closes, checkmark appears on completion | ✓ |
| 2 | "Share without limits" | Globe with orbiting share arrows | Globe rotates, 3 arrows orbit | |
| 3 | "Free and open source software" | OSI logo: keyhole inside a gear (Open Source Initiative symbol) | Logo springs in, stays on screen | ✓ |
| 4 | "For developers, researchers and tech enthusiasts" | OSI logo STAYS in illustration zone while text writes below | Three silhouettes (coder, researcher, enthusiast) stagger in alongside persistent OSI icon | ✓ |
| 5 | "Capcat.org" | Full-frame center, 80px orange, no subtitle strip — full frame takeover | Types out, then glow pulse | |
| 6 | "Defined with natural language processing" | Text tokens highlighted in sequence | Word-by-word orange highlight sweep | |
| 7 | "Built with large language models" | Stacked transformer blocks (4 layers) | Layers slide up | |
| 8 | "A minimum viable product" | Screen fades to `#1a1212` | `backgroundColor` crossfade over 60 frames | |

**Your notes:**


---

## Audio Swoosh Sync

**Approach:** `useAudioData()` + `visualizeAudio()` from `@remotion/media-utils`.
At transient peaks above threshold → `spring` scale pulse on active illustration element.

Alternatively: run audio through offline analysis tool before implementation to extract exact transient timestamps, then hardcode them as an array of frame numbers. Tools that can do this:
- **Essentia.js** — browser-based audio analysis, onset detection
- **aubio** (CLI) — `aubioonset` command outputs timestamps of onset events
- **Python librosa** — `librosa.onset.onset_detect()` — most accurate

Recommended: run `aubio` or `librosa` on `AudioVersionFinalNonMastered.mp4` to get a list of swoosh/accent timestamps, then map those frames to animation triggers in `subtitleCues.ts`.

**Expected sync anchors:**
- Scene 5 cat entrance ("Capcat")
- Scene 5 crowd jump ("Capcat?")
- Scene 7 zip sound ("Archive with confidence")
- Scene transitions
- Key feature icons in Scene 6

**Your notes:**


---

## Open Questions

- [ ] `Your-Own-Sources-icon.svg` — which scene does this belong to?
- Your-Own-Sources-icon. IGNORE. WE DONT USE IT HERE.
- [ ] `Capcat-Logo.svg` — which scene does this belong to?
- Capcat-Logo.svg - THE FINAL SECTION BEFORE CLOSING OUT TO DARK
- [ ] Scene transitions between scenes — style to define (fade? slide? wipe?)
- THE BACKGROUND STAYS IN THE STYLE OF THE SITE. YOU CHANGE WITH FADE IN OUT IN THE FINAL SCENE. THERE IS NO TRANSITION BETWEN SCENES. THE TYPED TEXT AND ILUUSTRATION FADE OUT IN THE END OF THE SCENES.
- [ ] Visual Direction notes — add your feeling/style input above
- THE SITE STYLE. CLEAN. ON BEAT. PROFFESIONAL
- [ ] Scene 1: is the CSS-drawn browser correct, or should it be an SVG illustration instead? 
- BROWSER IS CORRECT DIRECTION
- [ ] Scene 2–4: any of the "imagine adequate" illustrations need replacing with assets from ILLUSTRATION folder? 
- NO

**Your notes:**
