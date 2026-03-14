# Capcat Video Ad — Brainstorm Working Notes

> Add your notes under each section. Prefix with `NOTE:`. Claude will refine based on your input.

---

## Layout

- Illustration zone: top 60% (648px of 1080px)
- Text zone: bottom 40% (432px)
- Short phrases (≤5 words): 52px
- Long phrases (≥6 words): 38px
- Typewriter animation: left to right, per line
- Font: Source Serif 4

**Your notes:**


---

## Visual Direction

Single unified style. To be defined with your input.

**Your notes:**


---

## Cat Mascot

The cat (`Capcat-Cat-Color.svg`) is present in every scene — it is a permanent character, not a reveal. Its role, position, and expression/reaction per scene needs to be defined.

Questions to answer:
- Where is the cat anchored (corner, bottom, side)?
- Does the cat react to scene content (lean, look, gesture)?
- Does the cat scale or stay constant size?
- Is the cat always visible or does it enter/exit per scene?

**Your notes:**
The cat is only in the defined scene with the sequence: Cat illustration reviel, stays on screen, the crowd shows behind. Print screen the Capcat.org site illustraion for correct proportion and composition.
Anchored in the center of the screen. Comes from the left with blur animation and ellastic effect and stops at the center. It is visible in the TWO sentences: Capcat. and Capcat? (crowd illustraion is revieled from the center but behind the cat.

---

## Scene 1 — Browsing Workflow

| # | Text | Illustration Idea | Animation Idea | Notes |
|---|------|-------------------|----------------|-------|
| 1 | "This is my browsing workflow" | CSS-drawn Chrome window centered | Window scales in from 0, spring entrance | |
| 2 | "Open a website" | Abstract website inside browser (colored blocks: nav, hero, cards) | Content fades into browser area | |
| 3 | "Scan" | Scrollbar indicator moves, page content scrolls up | `interpolate` scroll Y over 1s | |
| 4 | "Choose article" | One card gets orange highlight border + cursor dot moves to it | Cursor animates to card, border pulses | |
| 5 | "Read" | 8 horizontal lines draw left→right inside card | Width 0→100% per line, 80ms stagger | |
| 6 | "Bookmark" | Browser chrome bookmark star activates, fills orange | Star fill interpolates empty→orange | |
| 7 | "If it has added value" | Browser stays static | Slight scale pulse 1→1.02→1 | |
| 8 | "Clip with Obsidian" | Browser background recolors to Obsidian purple `#7c3aed` | Background-color crossfade + hue-rotate | |

**Cat in this scene:**

**Your notes:**


---

## Scene 2 — The Problem (Digging)

| # | Text | Illustration Idea | Animation Idea | Notes |
|---|------|-------------------|----------------|-------|
| 1 | "I have to dig into the bookmarks and clippings" | Stack of folders/bookmarks in a chaotic pile, slightly tilted | Folders rain down from top, stack with slight rotations | |
| 2 | "To label" | Label tag SVG appears on top folder | Tag slides in from right, attaches | |
| 3 | "Tag" | `#` hashtag symbol overlaps the stack | Scales in with overshoot spring | |
| 4 | "And organize" | Arrow cursor tries to drag folder — folder slips back | Folder translates, eases back to start — 2 cycles | |

**Cat in this scene:**

**Your notes:**


---

## Scene 3 — Still Missing

| # | Text | Illustration Idea | Animation Idea | Notes |
|---|------|-------------------|----------------|-------|
| 1 | "And I am still missing valuable information" | Magnifying glass scanning empty space, nothing found | Glass sweeps left→right, target inside is invisible | |
| 2 | "Every day" | Calendar flipping 3 pages, days incrementing | Page flip `rotateX` 0→-90°→next page, 3 cycles | |

**Cat in this scene:**

**Your notes:**


---

## Scene 4 — The Solution / File-First Model

| # | Text | Illustration Idea | Animation Idea | Notes |
|---|------|-------------------|----------------|-------|
| 1 | "What if I capture first" | Hand (SVG outline) opening to catch falling items (stars/dots) | Items fall, hand closes — spring | |
| 2 | "Catalogue later" | Filing cabinet drawer slides open | Drawer `translateX` slides out | |
| 3 | "Date" | `2026-03-08` stamps onto a document | Rubber stamp scale 0→1.1→1, ink splat | |
| 4 | "Source" | URL bar / chain-link icon | Chain links connect left→right | |
| 5 | "A folder with a title" | Folder icon, title text appears on tab | Folder springs in, text types on tab | |
| 6 | "Structure before I even decide what matters" | Tree diagram drawing itself (3 nodes, 2 levels) | SVG stroke `stroke-dashoffset` animates | |
| 7 | "Markdown files with embedded images" | `.md` file icon with small image thumbnail inset | File springs in, thumbnail fades inside | |
| 8 | "Clean data for Obsidian graph" | Obsidian graph view: dots + connecting lines | Nodes spring in, edges draw via `stroke-dashoffset` | |
| 9 | "Workflow and input for any LLM" | Brain/circuit icon + arrow → LLM chat bubble | Arrow draws from brain to chat bubble | |
| 10 | "HTML version with Dark and Light Theme" | Split-screen: left dark browser, right light browser | Halves slide apart from center | |
| 11 | "Plus Code Coloring" | Code block with syntax-highlighted tokens | Tokens fade in staggered, colored per type | |
| 12 | "Ready to share" | Share icon, ripple outward | Concentric circles expand from icon | |
| 13 | "Quick to Archive" | Folder zips shut with checkmark | Zipper-close motion + checkmark scale | |
| 14 | "Easy to Read" | Open book, clean lines of text appear | Book opens (cover rotates), lines draw in | |

**Cat in this scene:**

**Your notes:**


---

## Scene 5 — Product Reveal

| # | Text | Illustration Idea | Animation Idea | Notes |
|---|------|-------------------|----------------|-------|
| 1 | "So I created it" | Dark radial vignette from center, anticipation build | `radial-gradient` expands, bg dims | |
| 2 | "Capcat" | `Capcat-Cat-Color.svg` — big reveal moment | Scale 0→1, bouncy spring `damping: 6` | |
| 3 | "Capcat?" | Crowd SVG explodes from behind cat | Crowd `translateY` +300→0, fast spring | |

**Cat in this scene:**

**Your notes:**


---

## Scene 6 — Features

| # | Text | Illustration Idea | Animation Idea | Notes |
|---|------|-------------------|----------------|-------|
| 1 | "Command Line mode" | Terminal types `./capcat fetch hn --count 5` | Typewriter 3 chars/frame, blinking cursor | |
| 2 | "Interactive menu" | Terminal clears, types `./capcat catch`, TUI menu renders | Prompt appears, menu lines stagger in | |
| 3 | "Bulk RSS fetching" | Progress bar: `[████████░░] 80% fetching...` | Width interpolates 0→100%, counter increments | |
| 4 | "Local Markdown storage" | `Local-Markdown-Storage-icon.svg` from capcat website | Spring scale entrance | |
| 5 | "Offline Accessibility" | `Offline-Accessibility-icon.svg` from capcat website | Spring scale entrance | |

**Cat in this scene:**

**Your notes:**
2.Interactive menu, move the triangle seletion down as in the real app:

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
   
---

3.Progress bar is not accurate here. It is this with animation of progress:
◒ CATCHING ▶  NATURE ◎ ◎ ◎ ◎ ◎ ◎  5/27 (14.8%) (COMPLETE)
Animation progress:
◓ CATCHING ▶  NATURE ◉ ◉ ◉ ◉ ◎ ◎  20/27 (72.2%) (CONVERTING)
---

## Scene 7 — Outro

| # | Text | Illustration Idea | Animation Idea | Notes |
|---|------|-------------------|----------------|-------|
| 1 | "Archive with confidence" | Vault/lock icon, closes and locks | Lock shackle closes, keyhole appears | |
| 2 | "Share without limits" | Globe with orbiting share arrows | Globe rotates, 3 arrows orbit | |
| 3 | "Free and open source software" | GitHub Octocat outline + `</>` brackets | Octocat springs in, brackets expand | |
| 4 | "For developers, researchers and tech enthusiasts" | Three avatar silhouettes (coder, microscope, lightbulb) | Silhouettes slide in from left, staggered | |
| 5 | "Capcat.org" | Full-frame center, 80px orange, no subtitle strip | Types out, glow pulse | |
| 6 | "Defined with natural language processing" | Text tokens highlighted: defined→language→processing | Word-by-word orange highlight sweep | |
| 7 | "Built with large language models" | Stacked transformer blocks (4 layers) | Layers slide up | |
| 8 | "A minimum viable product" | Screen fades to dark `#1a1212` | `backgroundColor` crossfade over 60 frames | |

**Cat in this scene:**

**Your notes:**
1. You have a zipping sound. USE ARCHIVE ILLUSTRATION/ ZIP. ETC
3. The Open Source Initiative (OSI) Logo: A key symbol is the keyhole inside a gear, representing the "openness" of the source code.
4. THE FOSS ICON STAYS WHILE TEXT IN THE BOTTOM PART IS WRITTEN.

---

## Audio Swoosh Sync

Strategy: use `useAudioData()` + `visualizeAudio()` from `@remotion/media-utils` to detect transients. At each peak above threshold, trigger a `spring` scale pulse on the active illustration element.

Expected sync anchors (to confirm against audio):
- Scene transitions
- Cat reveal (Scene 5 beat 2)
- Crowd jump (Scene 5 beat 3)
- Key noun entrances: "Markdown", "HTML", "Obsidian", "Capcat.org"
- Progress bar completion (Scene 6 beat 3)

**Your notes:**


---

## Open Questions

- [ ] Where is the cat anchored across scenes?
ANSWER: IT IS ONLY APPEARING IN THE MENTIONED SCENE AND TEXT. NOT ANYWHERE ELSE
- [ ] Do we have a transcript with timestamps? (needed for precise swoosh mapping)
ANSWER: YOU SHOULD DETECT THE SOUNDS. THINK ABOUT USING AUDIO ANALISYS. OR PROPOSE A TOOL WHICH CAN SOLVE THIS PROBLEM
- [ ] Is there a `Crowd.svg` asset? (not found in `Video/public/`)
- You have all in the folder ILLUSTRATION. Read the files and incorporate the icons into the adequate SCENE (replacing your suggestions before)
- [ ] Is there an `obsidian-icon.svg`? (referenced in Scene 1, not in `Video/public/`)
ANSWER: Yes, in the ILLUSTRATION folder
- [ ] What is the overall visual style / feeling? (to be defined in Visual Direction above)
- Use Playwrhigt to print screen Capcat.org and DESIGN SYSTEM FOR COLORS.
