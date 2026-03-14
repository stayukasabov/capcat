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

## Visual Direction — CONFIRMED

- Background: `#faf5ee` (paper) — cream, persistent across entire video
- Text: `#221717` (imprint)
- Accent: `#f1540d` (orange-500)
- Accent light: `#ff9463` (orange-400)
- Muted: `#827c7c` (imprint-muted)
- Dark (final fade): `#1a1212`
- Font: Source Serif 4 (weights 300–700 available locally)
- Mono font: SF Mono / Courier New (terminal/TUI beats)
- Feeling: site style, clean, on beat, professional

---

## Architecture — CONFIRMED

- **Each sentence/illustration combination = its own Remotion `<Sequence>` component**
- ~40 individual beat components, named by scene and beat number (e.g. `S1_B1`, `S1_B2`)
- No transitions between beats — background stays cream
- Each beat: illustration fades/springs in → holds → fades out; text types in → holds → fades out
- Only exception: final Scene 7 beat 8 fades entire screen to `#1a1212`

**Your notes:**


---

## Available Illustration Assets (`Video/ILLUSTRATION/`)

| File | Used in |
|------|---------|
| `Capcat-Cat-Color.svg` | Scene 5, beats 2–3 only |
| `Crowd.svg` | Scene 5, beat 3 (behind cat) |
| `2023_Obsidian_logo.svg` | Scene 1, beat 8 |
| `Command-Line-Mode-icon.svg` | Scene 6, beat 1 |
| `Interactive-Menu-icon.svg` | Scene 6, beat 2 |
| `Bulk-RSS-Fetching-icon.svg` | Scene 6, beat 3 |
| `Local-Markdown-Storage-icon.svg` | Scene 4 beat 7, Scene 6 beat 4 |
| `HTML-Generation-icon.svg` | Scene 4, beat 10 |
| `Offline-Accessibility-icon.svg` | Scene 6, beat 5 |
| `Capcat-Logo.svg` | Scene 7, beat 7 (final section before fade to dark) |
| `Your-Own-Sources-icon.svg` | NOT USED |

---

## Cat Mascot — CONFIRMED

- Appears ONLY in Scene 5, beats 2 and 3
- Beat 2: enters from LEFT with motion blur + elastic spring, settles at center
- Beat 3: `Crowd.svg` reveals from center behind the cat
- Size/composition reference: capcat.org hero — cat large, centered, crowd fills background
- No cat in any other scene

---

## Scene 1 — Browsing Workflow

| # | Text | Illustration | Animation |
|---|------|-------------|-----------|
| 1 | "This is my browsing workflow" | CSS-drawn Chrome window (title bar, URL bar, 3 traffic dots) | Window scales in from 0, spring entrance |
| 2 | "Open a website" | Abstract website inside browser: nav, hero, article cards (colored blocks) | Content fades in inside browser frame |
| 3 | "Scan" | Scrollbar indicator moves, page content scrolls upward | `interpolate` scroll Y over 1s |
| 4 | "Choose article" | Orange highlight border on one card, cursor dot moves to it | Cursor animates to card, border pulses |
| 5 | "Read" | 8 horizontal lines draw left→right inside card | Width 0→100% per line, 80ms stagger |
| 6 | "Bookmark" | Browser chrome bookmark star fills orange | Star fill interpolates empty→orange |
| 7 | "If it has added value" | Browser stays static | Slight scale pulse 1→1.02→1 |
| 8 | "Clip with Obsidian" | `2023_Obsidian_logo.svg` fades in over browser; browser bg crossfades to `#7c3aed` | bg color crossfade, logo opacity 0→1 |

**Your notes:**


---

## Scene 2 — The Problem

| # | Text | Illustration | Animation |
|---|------|-------------|-----------|
| 1 | "I have to dig into the bookmarks and clippings" | Chaotic pile of folders/bookmarks, slightly rotated | Folders rain from top, stack with random rotations |
| 2 | "To label" | Label tag attaches to top folder | Tag slides in from right |
| 3 | "Tag" | `#` hashtag overlaps the stack | Scales in with overshoot spring |
| 4 | "And organize" | Cursor tries to drag folder — it slips back | Folder translates, spring returns — 2 cycles |

**Your notes:**


---

## Scene 3 — Still Missing

| # | Text | Illustration | Animation |
|---|------|-------------|-----------|
| 1 | "And I am still missing valuable information" | Magnifying glass sweeps across empty space, nothing found | Glass sweeps left→right, invisible target |
| 2 | "Every day" | Calendar flipping 3 pages, days incrementing | `rotateX` 0→-90°→next page, 3 cycles |

**Your notes:**


---

## Scene 4 — The Solution / File-First Model

| # | Text | Illustration | Animation |
|---|------|-------------|-----------|
| 1 | "What if I capture first" | Hand opening to catch falling dots | Items fall, hand closes — spring |
| 2 | "Catalogue later" | Filing cabinet drawer slides open | `translateX` slides out |
| 3 | "Date" | Date stamp onto document | Stamp scale 0→1.1→1, ink splat |
| 4 | "Source" | Chain-link icon | Links connect left→right |
| 5 | "A folder with a title" | Folder, title text types on tab | Folder springs in, text typewriters |
| 6 | "Structure before I even decide what matters" | Tree diagram draws itself (3 nodes, 2 levels) | SVG `stroke-dashoffset` |
| 7 | "Markdown files with embedded images" | `Local-Markdown-Storage-icon.svg` + image thumbnail inset | Icon springs in, thumbnail fades inside |
| 8 | "Clean data for Obsidian graph" | Obsidian graph: nodes + connecting lines | Nodes spring in, edges draw via `stroke-dashoffset` |
| 9 | "Workflow and input for any LLM" | Circuit/brain → arrow → chat bubble | Arrow draws from source to bubble |
| 10 | "HTML version with Dark and Light Theme" | `HTML-Generation-icon.svg` + split dark/light browser | Halves slide apart from center |
| 11 | "Plus Code Coloring" | Code block with syntax-highlighted tokens | Tokens stagger in, colored per type |
| 12 | "Ready to share" | Share icon, concentric ripple | Circles expand from icon |
| 13 | "Quick to Archive" | ZIP folder closes with checkmark | Zipper-close motion + checkmark scale |
| 14 | "Easy to Read" | Open book, clean text lines | Book cover rotates open, lines draw in |

**Your notes:**


---

## Scene 5 — Product Reveal

| # | Text | Illustration | Animation |
|---|------|-------------|-----------|
| 1 | "So I created it" | Dark radial vignette from center | `radial-gradient` expands, bg dims |
| 2 | "Capcat" | `Capcat-Cat-Color.svg` | Enters from LEFT, motion blur + elastic spring, settles center |
| 3 | "Capcat?" | `Crowd.svg` behind cat | Reveals from center behind cat, fast spring `translateY` |

**Your notes:**


---

## Scene 6 — Features

| # | Text | Illustration | Animation |
|---|------|-------------|-----------|
| 1 | "Command Line mode" | `Command-Line-Mode-icon.svg` + terminal types `./capcat fetch hn --count 5` | Icon springs in, typewriter 3 chars/frame |
| 2 | "Interactive menu" | `Interactive-Menu-icon.svg` + exact TUI (see below) | Icon springs in, TUI renders line by line, `▶` moves through all options |
| 3 | "Bulk RSS fetching" | `Bulk-RSS-Fetching-icon.svg` + exact progress display (see below) | Icon springs in, spinner cycles, dots fill, counter increments |
| 4 | "Local Markdown storage" | `Local-Markdown-Storage-icon.svg` | Spring scale entrance |
| 5 | "Offline Accessibility" | `Offline-Accessibility-icon.svg` | Spring scale entrance |

### Beat 2 — Exact TUI

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

`▶` moves down through all options one by one.

### Beat 3 — Exact Progress Format

```
◒ CATCHING ▶  NATURE ◎ ◎ ◎ ◎ ◎ ◎  5/27 (14.8%) (STARTING)
◓ CATCHING ▶  NATURE ◉ ◉ ◉ ◉ ◎ ◎  20/27 (72.2%) (CONVERTING)
◔ CATCHING ▶  NATURE ◉ ◉ ◉ ◉ ◉ ◉  27/27 (100%) (COMPLETE)
```

- Spinner: `◒ → ◓ → ◔ → ◕ → ◒` cycling
- Dots fill left to right: `◎` → `◉`
- Counter and % increment
- Status: STARTING → FETCHING → CONVERTING → COMPLETE

**Your notes:**


---

## Scene 7 — Outro

| # | Text | Illustration | Animation |
|---|------|-------------|-----------|
| 1 | "Archive with confidence" | ZIP file icon closes — sync to zipping sound | Zipper closes, checkmark appears |
| 2 | "Share without limits" | Globe with orbiting share arrows | Globe rotates, 3 arrows orbit |
| 3 | "Free and open source software" | OSI logo (keyhole inside gear) — springs in, **stays on screen** | Logo spring entrance, persists |
| 4 | "For developers, researchers and tech enthusiasts" | OSI logo stays + 3 silhouettes (coder, researcher, enthusiast) stagger in | Silhouettes slide from left |
| 5 | "Capcat.org" | Full-frame center takeover, 80px orange — no text zone | Types out, glow pulse |
| 6 | "Defined with natural language processing" | Word tokens highlight in sequence | Word-by-word orange sweep |
| 7 | "Built with large language models" | `Capcat-Logo.svg` | Logo springs in |
| 8 | "A minimum viable product" | `Capcat-Logo.svg` stays, entire screen fades to `#1a1212` | `backgroundColor` crossfade over 60 frames |

**Your notes:**


---

## Audio Swoosh Sync

Pre-implementation step: run `librosa` or `aubio` on `Video/Audio/AudioVersionFinalNonMastered.mp4` to extract onset timestamps. Map to frame numbers. Hardcode as trigger array.

Expected anchors:
- Scene 5 beat 2: cat entrance
- Scene 5 beat 3: crowd jump
- Scene 7 beat 1: zip sound
- Scene 6 beat transitions
- Key icon springs in Scene 6

**Your notes:**


---

## Beat Timing — CONFIRMED

**Approach: A + B combined**

1. Run `librosa` onset detection on `Video/Audio/AudioVersionFinalNonMastered.mp4` → extract phrase timestamps → primary source for `durationInFrames` per beat
2. Word count × ~0.4s → cross-check and fallback for beats where audio detection is ambiguous
3. Fine-tune in Remotion Studio by scrubbing against audio after first build

Pre-implementation task: run audio analysis script before writing any Sequence code. Output: a `beatTimings.ts` file with `{ beat: string, startSec: number, durationSec: number }[]`.
