# Capcat Video Presentation — Design Doc
**Date:** 2026-03-05

## Overview

A ~110s product video driven by the existing audio narration (`Video/Audio/AudioVersionFinalNonMastered.mp4`). Text subtitles sync phrase-by-phrase to audio timestamps. Illustrated upper zone shows animated icons per narrative beat. Terminal animation covers the product demo. Cat + Crowd outro closes.

Built with Remotion in `Video/` (existing scaffold). Replaces the old scene-based structure entirely.

---

## Audio

- File: `Video/public/AudioVersionFinalNonMastered.mp4`
- Starts at 0:00 (transcript software added a 1:00:00 offset — ignore it)
- Duration: ~110s → **3300 frames @ 30fps** (add 5s buffer = 3450 frames total)

---

## Layout (1920×1080)

```
┌─────────────────────────────────────────┐  y:0
│                                         │
│     UPPER ZONE  (70% = 756px height)    │
│     icons, illustrations, terminal      │
│                                         │
├─────────────────────────────────────────┤  y:756
│  SUBTITLE STRIP  (30% = 324px height)   │
│  centered phrases, Source Serif 4       │
└─────────────────────────────────────────┘  y:1080
```

Background: `#faf5ee` (paper) throughout, except terminal scene (dark).

---

## Scene Breakdown

### Scene 1 — Browsing Workflow (0–17s | frames 0–510)
**Upper:** Lucide `Globe` + `BookmarkCheck`, spring entrance, centered
**Subtitles:**
- 1s: "This is my browsing workflow."
- 3s: "Open a website, scan, choose article, read, bookmark."
- 12s: "If it has added value, clip with Obsidian."

### Scene 2 — The Problem (17–35s | frames 510–1050)
**Upper:** Lucide `BookmarkX` + `FileQuestion`, spring entrance
**Subtitles:**
- 17s: "I have to dig into the bookmarks and clippings to label, tag, and organize."
- 26s: "And I am still missing valuable information every day."
- 31s: "What if I capture first, catalog later."

### Scene 3 — File-First Model (35–47s | frames 1050–1410)
**Upper:** `Local-Markdown-Storage-icon.svg`, centered, spring entrance
**Subtitles:**
- 35s: "A file first model to extend my reach."
- 38s: "Date, source, a folder with the title."
- 44s: "Structure before I even decide what matters."

### Scene 4 — Markdown Output (47–56s | frames 1410–1680)
**Upper:** `Local-Markdown-Storage-icon.svg` (left) + Lucide `Network` (right), side by side
**Subtitles:**
- 47s: "Markdown files with embedded images."
- 50s: "Clean data for Obsidian Graph."
- 53s: "Workflow and input for any LLM."

### Scene 5 — HTML Output (56–68s | frames 1680–2040)
**Upper:** `HTML-Generation-icon.svg`, centered, spring entrance
**Subtitles:**
- 56s: "HTML version with dark and light theme."
- 59s: "Plus code coloring."
- 62s: "Ready to share, quick to archive, easy to read."

### Scene 6 — Terminal Demo (68–97s | frames 2040–2910)
**Upper:** Full dark terminal window
**Sequence inside terminal:**
- 68s: Shell prompt appears
- 69s: `git clone https://github.com/stayukasabov/capcat.git` — typewriter
- 72s: `Cloning into 'capcat'...` response
- 75s: `./capcat catch` — typewriter
- 76s: ASCII logo animates in:
  ```
       ____
     / ____|                     _
    | |     __ _ _ __   ___ __ _| |_
    | |    / _  |  _ \ / __/ _  | __|
    | |___| (_| | |_) | (_| (_| | |_
     \_____\__,_|  __/ \___\__,_|\__|
                | |
                |_|
  ```
- 78s: TUI menu renders (orange `#d75f00` pointer ▶, questionary layout):
  ```
    What would you like me to do?
    ▶ Catch articles from a bundle of sources
      Catch articles from a list of sources
      Catch from a single source
      Catch a single article by URL
      Manage Sources (add/remove/configure)
      Exit
     (Use arrow keys to navigate)
  ```
- 85s: Pointer animates down through options
- 90s: Summary screen:
  ```
    --------------------
    SUMMARY
    Action: bundle
    Bundle: tech
    --------------------
    Executing command...
  ```
- 93s: Terminal fades out

**Subtitles continue through this scene:**
- 68s: "So I created it."
- 70s: "CapCat."
- 71s: "CapCat."
- 73s: "Command line mode."
- 76s: "Interactive menu."
- 78s: "Bulk RSS fetching."
- 80s: "Local markdown storage."
- 83s: "Offline accessibility."
- 85s: "Archive with confidence."
- 88s: "Share without limits."
- 90s: "Free and open source software."
- 93s: "For developers, researchers, and tech enthusiasts."

### Scene 7 — Outro (97–110s | frames 2910–3300+)
**Upper:**
- `Crowd.svg` fades in full-width background (desaturated/muted)
- `Capcat-Cat-Color.svg` springs in from below center (bouncy: `damping: 8`)

**Bottom strip:** "capcat.org" types out in orange `#f1540d` at 97s

**Subtitles:**
- 97s: "CapCat.org."
- 99s: "Defined with natural language processing."
- 102s: "Built with large language models."
- 105s: "A minimum viable product."

- Final fade to paper white over last 60 frames

---

## Subtitle Component

Reusable `<SubtitleStrip>` component:
- Array of `{ startSec: number, text: string }` cues
- At each cue: opacity 0→1 in 4 frames, holds until next cue − 4 frames, then 0
- Positioned: absolute bottom 0, full width, 324px height, flex center
- Font: Source Serif 4, 36px, `#221717`, centered

---

## Icon Animation Pattern (Scenes 1–5)

- Spring scale 0→1 on scene enter (`damping: 200`, `durationInFrames: 25`)
- Icons size: 180px for single, 140px for paired
- Scene exit: opacity 1→0 over 10 frames
- Paired icons: `display: flex, gap: 80px, alignItems: center`

---

## Terminal Scene Implementation

- Dark background `#1a1212`, rounded corners, full-width in upper zone
- Terminal title bar with 3 dots
- All text: SF Mono / monospace, orange prompt `#f1540d`, muted output `#827c7c`
- Typewriter: string slicing via `useCurrentFrame()`, 3 chars/frame
- ASCII logo: single `<pre>` block, fade+translateY entrance
- TUI menu: rendered as `<pre>` with orange pointer char, pointer position state driven by frame ranges
- No CSS transitions — all via `interpolate()`

---

## File Structure (new/changed)

```
Video/
├── public/
│   ├── AudioVersionFinalNonMastered.mp4   ← copy from Video/Audio/
│   ├── Capcat-Cat-Color.svg
│   ├── Crowd.svg
│   ├── Local-Markdown-Storage-icon.svg
│   ├── HTML-Generation-icon.svg
│   ├── Bulk-RSS-Fetching-icon.svg
│   ├── Command-Line-Mode-icon.svg
│   ├── Interactive-Menu-icon.svg
│   └── Offline-Accessibility-icon.svg
└── src/
    ├── Root.tsx                           ← update: 3450 frames
    ├── tokens.ts                          ← unchanged
    ├── SubtitleStrip.tsx                  ← new: shared subtitle component
    ├── subtitleCues.ts                    ← new: all 30 cue timestamps
    ├── compositions/
    │   └── CapcatIntro.tsx                ← rewrite: audio + 7 scenes
    └── scenes/
        ├── BrowsingScene.tsx              ← new (replaces TitleScene)
        ├── ProblemScene.tsx               ← rewrite
        ├── FileFirstScene.tsx             ← new
        ├── MarkdownScene.tsx              ← new
        ├── HtmlScene.tsx                  ← new (replaces SolutionScene)
        ├── TerminalScene.tsx              ← rewrite (replaces CLIScene)
        └── OutroScene.tsx                 ← rewrite
```

Old scenes `TitleScene.tsx`, `FeaturesScene.tsx`, `SolutionScene.tsx`, `CLIScene.tsx` — replaced.

---

## Dependencies to add

- `lucide-react` — Globe, BookmarkCheck, BookmarkX, FileQuestion, Network icons (MIT)

---

## Verification

```bash
cd /tmp/capcat-video-run
npm install lucide-react
npx remotion studio --port 3001
# Check each scene at start frame, mid frame, end frame
# Verify subtitle text matches audio at each timestamp
```
