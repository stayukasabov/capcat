# Capcat Video Ad — Design Document

**Date:** 2026-03-08
**Source:** `docs/plans/2026-03-08-video-brainstorm-notes.md`
**Audio:** `Video/Audio/AudioVersionFinalNonMastered.mp4` (~110s)
**Output:** 1920×1080 @ 30fps, ~3300 frames

---

## 1. Overview

A ~110s product ad driven by real audio narration. Every sentence in the script maps to an isolated, independently-editable beat component. The background is always cream (`#faf5ee`). Each beat fades its illustration and text in, holds, then fades out. No scene transitions — cuts are invisible because the background never changes.

Audio analysis (librosa/aubio) extracts exact phrase timestamps before any code is written. Word-count estimation cross-checks ambiguous beats.

---

## 2. Tech Stack

| Package | Purpose |
|---------|---------|
| `remotion` | Core: `useCurrentFrame`, `interpolate`, `spring`, `Series`, `Sequence`, `AbsoluteFill`, `staticFile` |
| `@remotion/media` | `<Audio>` component |
| `@remotion/google-fonts/SourceSerif4` | Font loading |
| `lucide-react` | Generic icons (Scene 2–4 where no SVG asset exists) |
| `librosa` (Python, pre-build) | Audio onset/phrase timestamp extraction |

**Rules (from Remotion skills):**
- All animation via `useCurrentFrame()` + `interpolate()` + `spring()` — no CSS transitions
- All assets via `staticFile()` from `public/`
- Every `<Sequence>` gets `premountFor={fps}` for smooth render
- Typewriter: string slicing only — never per-character opacity
- Spring configs: `{ damping: 200 }` smooth / `{ damping: 20, stiffness: 200 }` snappy / `{ damping: 8 }` bouncy

---

## 3. Layout

```
┌──────────────────────────────────────────────┐  y:0
│                                              │
│         ILLUSTRATION ZONE  (648px)           │
│         top 60% of canvas                   │
│                                              │
├──────────────────────────────────────────────┤  y:648
│                                              │
│         TEXT ZONE  (432px)                   │
│         bottom 40% of canvas                │
│         centered horizontally               │
│                                              │
└──────────────────────────────────────────────┘  y:1080
```

**Text sizes:**
- ≤5 words: 52px, weight 400
- ≥6 words: 38px, weight 400
- Font: Source Serif 4
- Color: `#221717`
- "Capcat.org" beat only: 80px, weight 700, color `#f1540d`, full-frame (no zone split)

---

## 4. Design Tokens

From `Video/public/design-system.css` and `Video/src/tokens.ts`:

```ts
paper:          "#faf5ee"   // background, persistent
imprint:        "#221717"   // text
imprintMedium:  "#3a3737"
imprintMuted:   "#827c7c"
accentPrimary:  "#f1540d"   // orange-500
accentLight:    "#ff9463"   // orange-400
dark:           "#1a1212"   // terminal, final fade
obsidianPurple: "#7c3aed"   // Scene 1 beat 8 only
```

---

## 5. Reusable Animation Primitives

### BeatWrapper
Every beat component uses this pattern internally:

```
- frame 0–8:    illustration springs/fades in
- frame 8 to (duration - 10):  holds
- frame (duration - 10) to duration:  illustration + text fade out
- text typewriter starts at frame 4, completes before hold phase
```

Standard spring configs per element type:
- SVG icon reveal: `spring({ damping: 200, durationInFrames: 20 })`
- Icon from off-screen: `spring({ damping: 20, stiffness: 200 })` — snappy
- Cat entrance: `spring({ damping: 8 })` — bouncy elastic
- Text fade-in: `interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" })`
- Exit: `interpolate(frame, [duration - 10, duration], [1, 0], { extrapolateRight: "clamp" })`

### Typewriter
```
chars = Math.floor(frame * CHARS_PER_FRAME)
display = text.slice(0, chars)
```
- Speed: 4 chars/frame for normal phrases (52px), 5 chars/frame for longer (38px)
- Blinking cursor: visible while typing, hidden after complete

### In/Out spring pattern (Remotion best practice)
```ts
const inSpring = spring({ frame, fps });
const outSpring = spring({ frame, fps, delay: durationInFrames - 10 });
const scale = inSpring - outSpring;
```

---

## 6. Pre-Implementation Task — Audio Analysis

Before writing any component, run:

```bash
cd "Video/Audio"
python3 - <<'EOF'
import librosa
import json

y, sr = librosa.load("AudioVersionFinalNonMastered.mp4", sr=None)
onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='time')
print(json.dumps([round(float(t), 3) for t in onset_frames]))
EOF
```

Map output timestamps to the 40 beats. Output file: `Video/src/beatTimings.ts`

```ts
export type BeatTiming = {
  id: string;          // e.g. "s1_b1"
  startSec: number;
  durationSec: number;
};

export const beatTimings: BeatTiming[] = [
  // populated from audio analysis + word-count cross-check
];
```

Each `<Series.Sequence>` reads `durationInFrames={Math.round(beat.durationSec * fps)}` from this file. Updating timing = editing one line in `beatTimings.ts`, no component changes.

---

## 7. File Structure

```
Video/
├── public/
│   ├── AudioVersionFinalNonMastered.mp4
│   └── ILLUSTRATION/          ← all SVGs referenced via staticFile()
│       ├── Capcat-Cat-Color.svg
│       ├── Crowd.svg
│       ├── 2023_Obsidian_logo.svg
│       ├── Command-Line-Mode-icon.svg
│       ├── Interactive-Menu-icon.svg
│       ├── Bulk-RSS-Fetching-icon.svg
│       ├── Local-Markdown-Storage-icon.svg
│       ├── HTML-Generation-icon.svg
│       ├── Offline-Accessibility-icon.svg
│       └── Capcat-Logo.svg
└── src/
    ├── Root.tsx                        ← registers CapcatAd composition
    ├── tokens.ts                       ← existing, unchanged
    ├── beatTimings.ts                  ← generated from audio analysis
    ├── compositions/
    │   └── CapcatAd.tsx               ← Audio + Series of all 40 beats
    ├── components/
    │   ├── BeatWrapper.tsx            ← standard fade-in/hold/fade-out shell
    │   ├── Typewriter.tsx             ← reusable typewriter + cursor
    │   ├── IllustrationZone.tsx       ← top 648px container
    │   ├── TextZone.tsx               ← bottom 432px container, centers text
    │   ├── BrowserChrome.tsx          ← CSS-drawn Chrome window (Scene 1)
    │   ├── TUIDisplay.tsx             ← ASCII logo + menu + animated pointer (S6_B2)
    │   └── ProgressDisplay.tsx        ← spinner + dots + counter (S6_B3)
    └── beats/
        ├── s1/   S1_B1 through S1_B8
        ├── s2/   S2_B1 through S2_B4
        ├── s3/   S3_B1 through S3_B2
        ├── s4/   S4_B1 through S4_B14
        ├── s5/   S5_B1 through S5_B3
        ├── s6/   S6_B1 through S6_B5
        └── s7/   S7_B1 through S7_B8
```

**Naming convention:** `S{scene}_B{beat}.tsx` — e.g. `S4_B7.tsx` is Scene 4 beat 7 "Markdown files with embedded images". Pinpoint any component by name for precise edits.

---

## 8. Composition Wiring

`CapcatAd.tsx` structure:
```
<AbsoluteFill style={{ backgroundColor: paper }}>
  <Audio src={staticFile("AudioVersionFinalNonMastered.mp4")} />
  <Series>
    <Series.Sequence durationInFrames={...} premountFor={fps}><S1_B1 /></Series.Sequence>
    <Series.Sequence durationInFrames={...} premountFor={fps}><S1_B2 /></Series.Sequence>
    ... (all 40 beats in order)
  </Series>
</AbsoluteFill>
```

`Root.tsx` registers one composition: `id="CapcatAd"`, total `durationInFrames` = sum of all beat durations.

---

## 9. Beat Specifications

### Scene 1 — Browsing Workflow (8 beats)

**S1_B1** — "This is my browsing workflow" (≤5w → 52px)
- Illustration: `BrowserChrome` component — CSS div: title bar with 3 traffic dots, URL bar, empty content area. Centered in IllustrationZone.
- Animation: scale 0→1, spring `{ damping: 200 }` entrance

**S1_B2** — "Open a website" (≤5w → 52px)
- Illustration: `BrowserChrome` with content: abstract colored block layout inside (orange nav bar, cream hero block, 3 article card blocks). Content fades in after browser is stable.
- Animation: block layout `opacity` 0→1 over 15 frames

**S1_B3** — "Scan" (1w → 52px)
- Illustration: Same browser. Scrollbar indicator on right edge slides down. Page content div translates upward.
- Animation: `interpolate(frame, [0, durationInFrames * 0.8], [0, -120])` translateY on content

**S1_B4** — "Choose article" (≤5w → 52px)
- Illustration: One article card gets orange border `2px solid #f1540d`. Cursor dot (8px circle, orange) animates from center to card.
- Animation: cursor `translateX/Y` interpolate, border opacity 0→1

**S1_B5** — "Read" (1w → 52px)
- Illustration: Inside selected card, 8 horizontal lines draw left→right.
- Animation: each line `width` 0→100%, staggered by 6 frames per line

**S1_B6** — "Bookmark" (1w → 52px)
- Illustration: Browser chrome top bar. Bookmark star icon (Lucide `Bookmark`) in top-right of browser. Star fill color interpolates `transparent` → `#f1540d`.
- Animation: `interpolate` on fill + scale 1→1.15→1 pulse

**S1_B7** — "If it has added value" (≥6w → 38px)
- Illustration: Browser stays static from S1_B6.
- Animation: scale pulse `1 → 1.02 → 1` over 20 frames, then holds

**S1_B8** — "Clip with Obsidian" (≤5w → 52px)
- Illustration: `2023_Obsidian_logo.svg` fades in centered over browser. Browser background-color crossfades from `#faf5ee` to `#7c3aed`.
- Animation: logo `opacity` 0→1 (15 frames). Background `interpolate` over 20 frames.

---

### Scene 2 — The Problem (4 beats)

**S2_B1** — "I have to dig into the bookmarks and clippings" (≥6w → 38px)
- Illustration: 5 folder icons (Lucide `Folder`) rain from top, each with slight random rotation (-15° to +15°), stack in a messy pile.
- Animation: each folder `translateY` from -200 to final position, staggered by 8 frames, `rotate` set per folder

**S2_B2** — "To label" (≤5w → 52px)
- Illustration: Label/tag shape (Lucide `Tag`) slides in from right, lands on top of folder pile.
- Animation: `translateX` 400→0, spring `{ damping: 20, stiffness: 200 }`

**S2_B3** — "Tag" (1w → 52px)
- Illustration: Large `#` character in accent orange overlaps the pile.
- Animation: scale 0→1.2→1, spring `{ damping: 8 }` overshoot

**S2_B4** — "And organize" (≤5w → 52px)
- Illustration: Cursor (Lucide `MousePointer2`) moves to top folder, folder translates right, then spring-returns to start. 2 cycles.
- Animation: `interpolate` for cursor movement, `spring` for folder return

---

### Scene 3 — Still Missing (2 beats)

**S3_B1** — "And I am still missing valuable information" (≥6w → 38px)
- Illustration: Large Lucide `Search` sweeps left→right across IllustrationZone. Inner target area is empty/`opacity: 0`.
- Animation: `translateX` -300→+300 over 80% of duration

**S3_B2** — "Every day" (≤5w → 52px)
- Illustration: Calendar (Lucide `Calendar`) with day number. Pages flip: 3 cycles of `rotateX` 0→-90° with next day revealing underneath via `backface-visibility`.
- Animation: `interpolate` for `rotateX`, day number increments at each flip mid-point

---

### Scene 4 — The Solution / File-First Model (14 beats)

**S4_B1** — "What if I capture first" (≥6w → 38px)
- Illustration: Hand (Lucide `Hand`) open, 6 dots fall from above, hand closes (`HandGrabbing` icon swap at frame 20). Dots freeze inside.
- Animation: dots `translateY` 0→landing, spring; hand icon swap at frame 20

**S4_B2** — "Catalogue later" (≤5w → 52px)
- Illustration: Filing cabinet (Lucide `Archive`) with drawer sliding open.
- Animation: drawer represented by inner div, `translateX` 0→80px, spring `{ damping: 200 }`

**S4_B3** — "Date" (1w → 52px)
- Illustration: Document with today's date (`2026-03-08`) stamped on it. Rubber stamp effect: scale 0→1.2→1 with a brief ink-spread shadow.
- Animation: scale spring `{ damping: 20 }`, box-shadow spreads via `interpolate`

**S4_B4** — "Source" (1w → 52px)
- Illustration: 3 chain links (Lucide `Link`) connecting left→right, drawing in sequence.
- Animation: each link `opacity` + `translateX` staggered by 8 frames

**S4_B5** — "A folder with a title" (≥6w → 38px)
- Illustration: Lucide `FolderOpen` springs in. Small label tab above folder with text "article-title.md" typing out.
- Animation: folder spring entrance, then typewriter on label text

**S4_B6** — "Structure before I even decide what matters" (≥6w → 38px)
- Illustration: Tree diagram — root node → 2 children → 2 grandchildren. Lines draw via SVG `stroke-dashoffset`, nodes appear after their connecting line completes.
- Animation: `stroke-dashoffset` from `pathLength` → 0, staggered per edge

**S4_B7** — "Markdown files with embedded images" (≥6w → 38px)
- Illustration: `Local-Markdown-Storage-icon.svg` centered. Small image thumbnail (`Lucide Image`) inset in bottom-right corner, fades in at frame 15.
- Animation: icon spring entrance, thumbnail `opacity` 0→1 delayed

**S4_B8** — "Clean data for Obsidian graph" (≥6w → 38px)
- Illustration: 6 nodes (small circles, orange + muted) with connecting lines between them — Obsidian graph style. Nodes spring in, edges draw via `stroke-dashoffset`.
- Animation: nodes stagger spring by 8 frames each, edges draw after source node appears

**S4_B9** — "Workflow and input for any LLM" (≥6w → 38px)
- Illustration: Lucide `Brain` (left) → animated arrow drawing right → Lucide `MessageSquare` (right, with `</>` text inside).
- Animation: brain springs in, arrow `stroke-dashoffset` draws, chat bubble springs in after arrow completes

**S4_B10** — "HTML version with Dark and Light Theme" (≥6w → 38px)
- Illustration: `HTML-Generation-icon.svg` centered, then two mini browser windows (dark left, light right) slide apart from center.
- Animation: icon springs in at frame 0, browsers appear at frame 15 and `translateX` apart

**S4_B11** — "Plus Code Coloring" (≤5w → 52px)
- Illustration: Code block (dark bg `#1a1212`, rounded) with 4 lines of pseudo-code. Each token appears with its syntax color (orange, muted, white) staggered.
- Animation: tokens `opacity` 0→1, 4 frames apart per token

**S4_B12** — "Ready to share" (≤5w → 52px)
- Illustration: Lucide `Share2` icon. 3 concentric circles expand outward from it.
- Animation: circles scale 0→2.5 and `opacity` 1→0 in sequence, offset by 15 frames each

**S4_B13** — "Quick to Archive" (≤5w → 52px)
- Illustration: ZIP folder — Lucide `FolderArchive`. Zipper line draws across top. Lucide `Check` appears after close.
- Animation: zipper SVG line `stroke-dashoffset`, then check springs in

**S4_B14** — "Easy to Read" (≤5w → 52px)
- Illustration: Lucide `BookOpen`. 5 text lines inside pages draw left→right.
- Animation: book spring entrance, then lines width 0→100% staggered by 5 frames

---

### Scene 5 — Product Reveal (3 beats)

**S5_B1** — "So I created it" (≥6w → 38px)
- Illustration: Radial gradient expands from center — from `#faf5ee` (invisible) to a dark vignette `rgba(26,18,18,0.3)`.
- Animation: `radial-gradient` radius `interpolate` over full duration

**S5_B2** — "Capcat" (1w → 52px)
- Illustration: `Capcat-Cat-Color.svg` — large (400px), centered.
- Animation: enters from LEFT (`translateX` -600→0) with motion blur effect (`filter: blur()` interpolates 8px→0px simultaneously). Spring: `{ damping: 8 }` — elastic overshoot. Cat stays on screen.

**S5_B3** — "Capcat?" (1w → 52px)
- Illustration: `Crowd.svg` was hidden behind cat. Reveals with `translateY` +400→0, spring `{ damping: 12 }`. Cat stays on top (z-index).
- Animation: crowd spring entrance from below. Both cat + crowd hold through duration.

---

### Scene 6 — Features (5 beats)

**S6_B1** — "Command Line mode" (≤5w → 52px)
- Illustration: `Command-Line-Mode-icon.svg` (left half of IllustrationZone, 200px). Right half: dark terminal panel. Types `./capcat fetch hn --count 5` with orange prompt `$`.
- Animation: icon springs in at frame 0. Terminal panel fades in at frame 8. Typewriter starts at frame 15.

**S6_B2** — "Interactive menu" (≤5w → 52px)
- Illustration: `Interactive-Menu-icon.svg` (left). Right: `TUIDisplay` component — full ASCII logo then menu (see exact format in notes). `▶` pointer animates through all 6 options.
- `TUIDisplay` behavior: ASCII logo fades in → menu renders line by line (3 frames each) → pointer starts moving at frame 40, cycles through options at 12 frames per option step.

**S6_B3** — "Bulk RSS fetching" (≤5w → 52px)
- Illustration: `Bulk-RSS-Fetching-icon.svg` (left). Right: `ProgressDisplay` component.
- `ProgressDisplay` behavior:
  - Spinner cycles `◒→◓→◔→◕→◒` at 8 frames per step
  - Dots fill left to right: each `◎→◉` every 6 frames
  - Counter increments from 0/27 to 27/27 over 80% of duration
  - Status: STARTING → FETCHING (at 30%) → CONVERTING (at 70%) → COMPLETE (at 100%)

**S6_B4** — "Local Markdown storage" (≤5w → 52px)
- Illustration: `Local-Markdown-Storage-icon.svg` centered, 280px.
- Animation: spring `{ damping: 200 }` scale entrance

**S6_B5** — "Offline Accessibility" (≤5w → 52px)
- Illustration: `Offline-Accessibility-icon.svg` centered, 280px.
- Animation: spring `{ damping: 200 }` scale entrance

---

### Scene 7 — Outro (8 beats)

**S7_B1** — "Archive with confidence" (≤5w → 52px)
- Illustration: Large ZIP file — `FolderArchive` Lucide icon. Zipper animation draws across. Checkmark springs in on complete.
- Audio sync: zipper draw animation timed to zipping sound onset from `beatTimings.ts`

**S7_B2** — "Share without limits" (≤5w → 52px)
- Illustration: Lucide `Globe2` (center). 3 `Share2` arrows orbit it at 120° intervals.
- Animation: globe spring entrance, arrows orbit via `rotate` on wrapper divs at different phase offsets

**S7_B3** — "Free and open source software" (≥6w → 38px)
- Illustration: OSI logo — keyhole inside gear — rendered as SVG inline (no external asset). Springs in, **stays on screen** for S7_B4.
- Animation: scale spring `{ damping: 200 }`

**S7_B4** — "For developers, researchers and tech enthusiasts" (≥6w → 38px)
- Illustration: OSI logo stays (left). 3 silhouettes (coder: `</>` icon, researcher: `FlaskConical`, enthusiast: `Lightbulb`) slide in from left, staggered 12 frames each.
- Animation: OSI holds. Silhouettes `translateX` -300→0, spring `{ damping: 20, stiffness: 200 }`

**S7_B5** — "Capcat.org" (1w special)
- SPECIAL: full-frame takeover. No zone split. Text centered at absolute center.
- Text: 80px, weight 700, `#f1540d`. Typewriter. Cursor blinks while typing.
- After typing completes: glow pulse — `textShadow` `0 0 0px #f1540d` → `0 0 30px #f1540d` → `0 0 0px` over 20 frames
- No illustration zone active. Background remains cream.

**S7_B6** — "Defined with natural language processing" (≥6w → 38px)
- Illustration: The phrase itself displayed large (52px) in illustration zone. Each word highlights orange in sequence — word-by-word sweep using `background-color` per word span.
- Animation: word highlight `interpolate` per word, 8 frames per word

**S7_B7** — "Built with large language models" (≥6w → 38px)
- Illustration: `Capcat-Logo.svg` centered, springs in, holds.
- Animation: scale spring `{ damping: 200 }`

**S7_B8** — "A minimum viable product" (≥6w → 38px)
- Illustration: `Capcat-Logo.svg` stays. Entire `AbsoluteFill` background crossfades `#faf5ee` → `#1a1212` over full duration. Text color crossfades `#221717` → `#faf5ee` to stay legible.
- Animation: `backgroundColor` + `color` `interpolate` over 60 frames

---

## 10. Audio Sync Triggers

After running librosa, map these specific beats to detected onset times:

| Beat | Expected trigger |
|------|-----------------|
| S5_B2 | Cat entrance — sync to narration peak "Capcat" |
| S5_B3 | Crowd entrance — sync to narration peak "Capcat?" |
| S7_B1 | Zipper draw start — sync to zipping sound onset |

All other beats use `startSec` from `beatTimings.ts` for their `from` position in `<Series>`.

---

## 11. Remotion Studio Navigation

Each beat maps directly to a named file. To edit any beat:
1. Open `Video/src/beats/s{N}/S{N}_B{M}.tsx`
2. Preview in Remotion Studio — beat starts at its `from` frame (sum of all preceding beat durations)
3. Scrub within that beat's frame range to verify illustration + text timing
4. Edit only that file — no other component is affected

To update timing: edit `beatTimings.ts` only.
To update illustration: edit the specific `S{N}_B{M}.tsx` only.
To update text: edit the specific `S{N}_B{M}.tsx` only.

---

## 12. Verification Checklist

- [ ] Audio analysis script runs cleanly on `AudioVersionFinalNonMastered.mp4`
- [ ] `beatTimings.ts` has all 40 entries with `startSec` + `durationSec`
- [ ] All SVGs from `ILLUSTRATION/` are copied to `Video/public/ILLUSTRATION/`
- [ ] Audio file copied to `Video/public/`
- [ ] Total composition frames = sum of all beat durations × 30
- [ ] Audio plays through all 40 beats without offset
- [ ] S5_B2 cat enters from left with elastic bounce
- [ ] S6_B2 TUI pointer cycles through all 6 menu options
- [ ] S6_B3 spinner + dots animate, counter increments to 27/27
- [ ] S7_B5 "Capcat.org" is full-frame, no zone split
- [ ] S7_B8 fades to `#1a1212`
