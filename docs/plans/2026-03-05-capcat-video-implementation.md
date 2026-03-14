# Capcat Video Presentation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a ~110s Remotion video driven by real audio, with 7 illustrated scenes, phrase-synced subtitles, a terminal/TUI demo, and a spring-animated cat outro.

**Architecture:** Single `CapcatIntro` composition (3450 frames @ 30fps). `<Audio>` component plays the narration. `<SubtitleStrip>` is an absolute overlay positioned at bottom of frame, always visible. Seven scene components fill the upper 70% zone, sequenced with `<Series>`. Terminal scene replicates the actual Capcat TUI (ASCII logo + questionary menu). Outro uses spring physics for the cat entrance.

**Tech Stack:** Remotion 4.0, React 18, TypeScript, `@remotion/google-fonts` (Source Serif 4), `@remotion/transitions` (fade/slide/wipe between scenes), `lucide-react` (MIT, for generic icons), existing Capcat SVG assets.

**Design doc:** `docs/plans/2026-03-05-capcat-video-design.md`

**Run location:** Project must be run from `/tmp/capcat-video-run` (symlink/copy without `!` in path — Webpack restriction). Source of truth files live in `Video/` in the repo; keep them in sync.

---

## Setup Checklist (do before Task 1)

```bash
# 1. Copy audio to public/
cp "Video/Audio/AudioVersionFinalNonMastered.mp4" /tmp/capcat-video-run/public/
cp "Video/Audio/AudioVersionFinalNonMastered.mp4" "Video/public/"

# 2. Copy any missing icons to public/
cp docs/icons/Crowd.svg /tmp/capcat-video-run/public/
cp docs/icons/Crowd.svg Video/public/
cp docs/icons/Interactive-Menu-icon.svg /tmp/capcat-video-run/public/
cp docs/icons/Interactive-Menu-icon.svg Video/public/

# 3. Install packages
cd /tmp/capcat-video-run
npm install lucide-react
npx remotion add @remotion/transitions   # adds @remotion/transitions to package.json

# 4. Start studio (keep running in background)
npx remotion studio --port 3001
```

### Frame budget with transitions

6 transitions total. Each 15f except Terminal→Outro which is 20f.
Total overlap = 5×15 + 1×20 = **95 frames**

| Scene | Raw frames |
|-------|-----------|
| BrowsingScene | 510 |
| ProblemScene | 540 |
| FileFirstScene | 360 |
| MarkdownScene | 270 |
| HtmlScene | 360 |
| TerminalScene | 870 |
| OutroScene | 540 |
| **Sum** | **3450** |
| Minus transitions | −95 |
| **Composition total** | **3355** → use **3360** |

Root.tsx must use **3360 frames**.

Also mirror all src/ changes back to the repo:
```bash
# After each task, rsync src/ back
rsync -a /tmp/capcat-video-run/src/ "Video/src/"
```

---

## Task 1: Update Root + subtitle cue data

**Files:**
- Modify: `Video/src/Root.tsx`
- Create: `Video/src/subtitleCues.ts`

**Step 1: Update Root.tsx to 3360 frames**

Replace entire content of `Video/src/Root.tsx`:

```tsx
import React from "react";
import { Composition } from "remotion";
import { CapcatIntro } from "./compositions/CapcatIntro";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="CapcatIntro"
      component={CapcatIntro}
      durationInFrames={3360}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
```

**Step 2: Create `Video/src/subtitleCues.ts`**

```ts
export type SubtitleCue = {
  startSec: number;
  text: string;
};

// All timestamps relative to 0:00 of the audio file.
// Source: Video/Script/AudioVersionFinalTranscript-Timeline.txt
// (transcript software added 1:00:00 offset — already subtracted here)
export const subtitleCues: SubtitleCue[] = [
  { startSec: 1,   text: "This is my browsing workflow." },
  { startSec: 3,   text: "Open a website, scan, choose article, read, bookmark." },
  { startSec: 12,  text: "If it has added value, clip with Obsidian." },
  { startSec: 17,  text: "I have to dig into the bookmarks and clippings to label, tag, and organize." },
  { startSec: 26,  text: "And I am still missing valuable information every day." },
  { startSec: 31,  text: "What if I capture first, catalog later." },
  { startSec: 35,  text: "A file first model to extend my reach." },
  { startSec: 38,  text: "Date, source, a folder with the title." },
  { startSec: 44,  text: "Structure before I even decide what matters." },
  { startSec: 47,  text: "Markdown files with embedded images." },
  { startSec: 50,  text: "Clean data for Obsidian Graph." },
  { startSec: 53,  text: "Workflow and input for any LLM." },
  { startSec: 56,  text: "HTML version with dark and light theme." },
  { startSec: 59,  text: "Plus code coloring." },
  { startSec: 62,  text: "Ready to share, quick to archive, easy to read." },
  { startSec: 68,  text: "So I created it." },
  { startSec: 70,  text: "CapCat." },
  { startSec: 71,  text: "CapCat." },
  { startSec: 73,  text: "Command line mode." },
  { startSec: 76,  text: "Interactive menu." },
  { startSec: 78,  text: "Bulk RSS fetching." },
  { startSec: 80,  text: "Local markdown storage." },
  { startSec: 83,  text: "Offline accessibility." },
  { startSec: 85,  text: "Archive with confidence." },
  { startSec: 88,  text: "Share without limits." },
  { startSec: 90,  text: "Free and open source software." },
  { startSec: 93,  text: "For developers, researchers, and tech enthusiasts." },
  { startSec: 97,  text: "CapCat.org." },
  { startSec: 99,  text: "Defined with natural language processing." },
  { startSec: 102, text: "Built with large language models." },
  { startSec: 105, text: "A minimum viable product." },
];
```

**Step 3: Verify in studio**

Navigate to frame 0 in Remotion Studio. Composition should show as 3360 frames (1:52.00).

**Step 4: Sync to repo**

```bash
rsync -a /tmp/capcat-video-run/src/ "Video/src/"
```

---

## Task 2: SubtitleStrip component

**Files:**
- Create: `Video/src/SubtitleStrip.tsx`

**Step 1: Create `Video/src/SubtitleStrip.tsx`**

```tsx
import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/SourceSerif4";
import { subtitleCues } from "./subtitleCues";
import { colors, fonts } from "./tokens";

const { fontFamily } = loadFont("normal", {
  weights: ["400"],
  subsets: ["latin"],
});

export const SubtitleStrip: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Find the active cue: last cue whose startSec <= current second
  const currentSec = frame / fps;
  let activeCue = null;
  let activeCueIndex = -1;
  for (let i = 0; i < subtitleCues.length; i++) {
    if (subtitleCues[i].startSec <= currentSec) {
      activeCue = subtitleCues[i];
      activeCueIndex = i;
    }
  }

  if (!activeCue) return null;

  const cueStartFrame = Math.round(activeCue.startSec * fps);
  const nextCueStartFrame =
    activeCueIndex < subtitleCues.length - 1
      ? Math.round(subtitleCues[activeCueIndex + 1].startSec * fps)
      : frame + 60;

  const fadeInEnd = cueStartFrame + 4;
  const fadeOutStart = nextCueStartFrame - 4;
  const fadeOutEnd = nextCueStartFrame;

  const opacity = interpolate(
    frame,
    [cueStartFrame, fadeInEnd, fadeOutStart, fadeOutEnd],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: 324,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        paddingLeft: 120,
        paddingRight: 120,
        opacity,
      }}
    >
      <div
        style={{
          fontFamily,
          fontSize: 36,
          fontWeight: 400,
          color: colors.imprint,
          textAlign: "center",
          lineHeight: 1.4,
        }}
      >
        {activeCue.text}
      </div>
    </div>
  );
};
```

**Step 2: Verify**

In studio, scrub to frame 30 (1s). Bottom strip should show "This is my browsing workflow."
Scrub to frame 90 (3s). Should show "Open a website..."

**Step 3: Sync**

```bash
rsync -a /tmp/capcat-video-run/src/ "Video/src/"
```

---

## Task 3: BrowsingScene (0–17s)

**Files:**
- Create: `Video/src/scenes/BrowsingScene.tsx`

Scene covers local frames 0–510. Shows Lucide `Globe` + `BookmarkCheck` in upper zone. Upper zone = top 756px of the 1080px frame. Lower 324px is left empty (SubtitleStrip overlays it).

**Step 1: Create `Video/src/scenes/BrowsingScene.tsx`**

```tsx
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Globe, BookmarkCheck } from "lucide-react";
import { colors } from "../tokens";

const UPPER_HEIGHT = 756;

export const BrowsingScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const globeScale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 25 });
  const globeOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  const bookmarkScale = spring({
    frame: frame - Math.round(2 * fps),
    fps,
    config: { damping: 200 },
    durationInFrames: 25,
  });
  const bookmarkOpacity = interpolate(
    frame,
    [Math.round(2 * fps), Math.round(2 * fps) + 15],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Fade out last 10 frames
  const sceneOpacity = interpolate(frame, [500, 510], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: colors.paper, opacity: sceneOpacity }}>
      <div
        style={{
          height: UPPER_HEIGHT,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 80,
        }}
      >
        <div style={{ transform: `scale(${globeScale})`, opacity: globeOpacity }}>
          <Globe size={180} color={colors.imprintMedium} strokeWidth={1.5} />
        </div>
        <div style={{ transform: `scale(${bookmarkScale})`, opacity: bookmarkOpacity }}>
          <BookmarkCheck size={180} color={colors.accentPrimary} strokeWidth={1.5} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

**Step 2: Verify**

Preview frame 0–510 in studio. Two icons spring in side by side in upper zone.

---

## Task 4: ProblemScene (17–35s)

**Files:**
- Create: `Video/src/scenes/ProblemScene.tsx` (replace existing)

```tsx
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BookmarkX, FileQuestion } from "lucide-react";
import { colors } from "../tokens";

const UPPER_HEIGHT = 756;

export const ProblemScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const xScale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 25 });
  const xOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  const qScale = spring({
    frame: frame - Math.round(2 * fps),
    fps,
    config: { damping: 200 },
    durationInFrames: 25,
  });
  const qOpacity = interpolate(
    frame,
    [Math.round(2 * fps), Math.round(2 * fps) + 15],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const sceneOpacity = interpolate(frame, [340, 360], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: colors.paper, opacity: sceneOpacity }}>
      <div
        style={{
          height: UPPER_HEIGHT,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 80,
        }}
      >
        <div style={{ transform: `scale(${xScale})`, opacity: xOpacity }}>
          <BookmarkX size={180} color={colors.accentPrimary} strokeWidth={1.5} />
        </div>
        <div style={{ transform: `scale(${qScale})`, opacity: qOpacity }}>
          <FileQuestion size={180} color={colors.imprintMedium} strokeWidth={1.5} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

---

## Task 5: FileFirstScene (35–47s)

**Files:**
- Create: `Video/src/scenes/FileFirstScene.tsx`

```tsx
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { colors } from "../tokens";

const UPPER_HEIGHT = 756;

export const FileFirstScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 25 });
  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const sceneOpacity = interpolate(frame, [340, 360], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: colors.paper, opacity: sceneOpacity }}>
      <div
        style={{
          height: UPPER_HEIGHT,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div style={{ transform: `scale(${scale})`, opacity }}>
          <Img src={staticFile("Local-Markdown-Storage-icon.svg")} style={{ width: 220, height: 220 }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

---

## Task 6: MarkdownScene (47–56s)

**Files:**
- Create: `Video/src/scenes/MarkdownScene.tsx`

```tsx
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Network } from "lucide-react";
import { colors } from "../tokens";

const UPPER_HEIGHT = 756;

export const MarkdownScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const mdScale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 25 });
  const mdOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  const netScale = spring({
    frame: frame - Math.round(2 * fps),
    fps,
    config: { damping: 200 },
    durationInFrames: 25,
  });
  const netOpacity = interpolate(
    frame,
    [Math.round(2 * fps), Math.round(2 * fps) + 15],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const sceneOpacity = interpolate(frame, [250, 270], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: colors.paper, opacity: sceneOpacity }}>
      <div
        style={{
          height: UPPER_HEIGHT,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 80,
        }}
      >
        <div style={{ transform: `scale(${mdScale})`, opacity: mdOpacity }}>
          <Img src={staticFile("Local-Markdown-Storage-icon.svg")} style={{ width: 180, height: 180 }} />
        </div>
        <div style={{ transform: `scale(${netScale})`, opacity: netOpacity }}>
          <Network size={180} color={colors.accentPrimary} strokeWidth={1.5} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

---

## Task 7: HtmlScene (56–68s)

**Files:**
- Create: `Video/src/scenes/HtmlScene.tsx`

```tsx
import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { colors } from "../tokens";

const UPPER_HEIGHT = 756;

export const HtmlScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 25 });
  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const sceneOpacity = interpolate(frame, [340, 360], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: colors.paper, opacity: sceneOpacity }}>
      <div
        style={{
          height: UPPER_HEIGHT,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div style={{ transform: `scale(${scale})`, opacity }}>
          <Img src={staticFile("HTML-Generation-icon.svg")} style={{ width: 220, height: 220 }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

---

## Task 8: TerminalScene (68–97s, 870 local frames)

This is the most complex scene. It replaces `CLIScene.tsx`.

**Files:**
- Create: `Video/src/scenes/TerminalScene.tsx`

The scene has 5 internal phases driven by local `frame`:

| Local frame | Global time | What happens |
|-------------|-------------|--------------|
| 0 | 68s | Terminal window fades in |
| 30 | 69s | `git clone ...` types out |
| 90 | 72s | Clone response appears |
| 210 | 75s | `./capcat catch` types out |
| 270 | 76s | ASCII logo slides in |
| 360 | 78s | TUI menu renders line by line |
| 510 | 85s | Pointer moves down then up, settles at option 1 |
| 660 | 90s | Summary block appears |
| 750 | 93s | Terminal fades out |

**Step 1: Create `Video/src/scenes/TerminalScene.tsx`**

```tsx
import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { colors, fonts } from "../tokens";

const UPPER_HEIGHT = 756;
const CHARS_PER_FRAME = 3;

const ASCII_LOGO = `       ____
     / ____|                     _
    | |     __ _ _ __   ___ __ _| |_
    | |    / _  |  _ \\  / __/ _  | __|
    | |___| (_| | |_) | (_| (_| | |_
     \\_____\\__,_|  __/ \\___\\__,_|\\__|
                | |
                |_|`;

const MENU_LINES = [
  "  What would you like me to do?",
  "",
  "  ▶ Catch articles from a bundle of sources",
  "    Catch articles from a list of sources",
  "    Catch from a single source",
  "    Catch a single article by URL",
  "    Manage Sources (add/remove/configure)",
  "    Exit",
  "",
  "   (Use arrow keys to navigate)",
];

const SUMMARY = `  --------------------
  SUMMARY
  Action: bundle
  Bundle: tech
  --------------------

  Executing command...`;

function typewriter(text: string, frame: number, startFrame: number): string {
  const chars = Math.max(0, (frame - startFrame) * CHARS_PER_FRAME);
  return text.slice(0, chars);
}

export const TerminalScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phase frames (local)
  const F_CLONE_START   = Math.round(1 * fps);   // 30
  const F_RESPONSE      = Math.round(3 * fps);   // 90
  const F_CATCH_START   = Math.round(7 * fps);   // 210
  const F_LOGO          = Math.round(9 * fps);   // 270
  const F_MENU          = Math.round(12 * fps);  // 360
  const F_POINTER_MOVE  = Math.round(17 * fps);  // 510
  const F_SUMMARY       = Math.round(22 * fps);  // 660
  const F_FADE_OUT      = Math.round(25 * fps);  // 750

  // Terminal window entrance
  const termOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  // git clone typewriter
  const cloneText = typewriter(
    "git clone https://github.com/stayukasabov/capcat.git",
    frame,
    F_CLONE_START
  );

  // Clone response
  const responseOpacity = interpolate(frame, [F_RESPONSE, F_RESPONSE + 10], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  // ./capcat catch typewriter
  const catchText = typewriter("./capcat catch", frame, F_CATCH_START);

  // ASCII logo
  const logoOpacity = interpolate(frame, [F_LOGO, F_LOGO + 15], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const logoY = interpolate(frame, [F_LOGO, F_LOGO + 20], [20, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  // Menu: lines appear one by one, each line 6 frames apart
  const menuLines = MENU_LINES.map((line, i) => {
    const lineStart = F_MENU + i * 6;
    const op = interpolate(frame, [lineStart, lineStart + 6], [0, 1], {
      extrapolateLeft: "clamp", extrapolateRight: "clamp",
    });
    return { line, op };
  });

  // Pointer animation: cycles through options 1→4→1
  const pointerIndex = (() => {
    if (frame < F_POINTER_MOVE) return 0;
    const elapsed = frame - F_POINTER_MOVE;
    const cycleFrames = Math.round(1.5 * fps); // 45 frames per move
    const step = Math.floor(elapsed / cycleFrames);
    const sequence = [0, 1, 2, 3, 2, 1, 0];
    return sequence[Math.min(step, sequence.length - 1)];
  })();

  // Replace pointer in menu line 2 based on pointerIndex
  const menuOptions = [
    "Catch articles from a bundle of sources",
    "Catch articles from a list of sources",
    "Catch from a single source",
    "Catch a single article by URL",
    "Manage Sources (add/remove/configure)",
    "Exit",
  ];
  const animatedMenuLines = frame >= F_POINTER_MOVE
    ? [
        "  What would you like me to do?",
        "",
        ...menuOptions.map((opt, i) =>
          i === pointerIndex ? `  ▶ ${opt}` : `    ${opt}`
        ),
        "",
        "   (Use arrow keys to navigate)",
      ]
    : MENU_LINES;

  // Summary
  const summaryOpacity = interpolate(frame, [F_SUMMARY, F_SUMMARY + 15], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  // Fade out
  const sceneOpacity = interpolate(frame, [F_FADE_OUT, F_FADE_OUT + 30], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{ backgroundColor: colors.paper, opacity: sceneOpacity }}
    >
      {/* Upper zone: terminal window */}
      <div
        style={{
          height: UPPER_HEIGHT,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 80px",
        }}
      >
        <div
          style={{
            opacity: termOpacity,
            backgroundColor: "#1a1212",
            borderRadius: 12,
            width: "100%",
            maxHeight: 680,
            overflow: "hidden",
            padding: "24px 32px",
            boxShadow: "0 8px 40px rgba(0,0,0,0.5)",
            border: "1px solid rgba(255,255,255,0.06)",
            fontFamily: fonts.mono,
            fontSize: 22,
            lineHeight: 1.7,
          }}
        >
          {/* Title bar */}
          <div style={{ display: "flex", gap: 8, marginBottom: 20, alignItems: "center" }}>
            <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#ff5f56" }} />
            <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#ffbd2e" }} />
            <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#27c93f" }} />
            <span style={{ color: colors.imprintMuted, marginLeft: 12, fontSize: 18 }}>
              capcat — zsh
            </span>
          </div>

          {/* git clone command */}
          {frame >= F_CLONE_START && (
            <div style={{ color: colors.orange400 }}>
              <span style={{ color: colors.accentPrimary }}>$ </span>
              {cloneText}
              {cloneText.length < 53 && (
                <span style={{ color: colors.accentPrimary }}>▌</span>
              )}
            </div>
          )}

          {/* Clone response */}
          {frame >= F_RESPONSE && (
            <div style={{ opacity: responseOpacity, color: colors.imprintMuted }}>
              {"  Cloning into 'capcat'..."}
              <br />
              {"  remote: Enumerating objects... done."}
              <br />
              {"  Receiving objects: 100% done."}
            </div>
          )}

          {/* ./capcat catch */}
          {frame >= F_CATCH_START && (
            <div style={{ color: colors.orange400, marginTop: 8 }}>
              <span style={{ color: colors.accentPrimary }}>$ </span>
              {catchText}
              {catchText.length < 14 && (
                <span style={{ color: colors.accentPrimary }}>▌</span>
              )}
            </div>
          )}

          {/* ASCII logo */}
          {frame >= F_LOGO && (
            <pre
              style={{
                opacity: logoOpacity,
                transform: `translateY(${logoY}px)`,
                color: colors.accentPrimary,
                fontFamily: fonts.mono,
                fontSize: 18,
                lineHeight: 1.4,
                margin: "8px 0",
                whiteSpace: "pre",
              }}
            >
              {ASCII_LOGO}
            </pre>
          )}

          {/* TUI Menu */}
          {frame >= F_MENU && frame < F_SUMMARY && (
            <div>
              {(frame >= F_POINTER_MOVE ? animatedMenuLines : menuLines).map((item, i) => {
                const entry = menuLines[i];
                const lineOp = frame >= F_POINTER_MOVE
                  ? 1
                  : (entry?.op ?? 0);
                const isPointer = frame >= F_POINTER_MOVE &&
                  i >= 2 && i <= 7 &&
                  animatedMenuLines[i]?.startsWith("  ▶");

                return (
                  <div
                    key={i}
                    style={{
                      opacity: frame >= F_POINTER_MOVE ? 1 : menuLines[i]?.op ?? 0,
                      color: isPointer ? colors.accentPrimary : colors.imprintMuted,
                      fontFamily: fonts.mono,
                      fontSize: 22,
                      lineHeight: 1.6,
                      whiteSpace: "pre",
                    }}
                  >
                    {frame >= F_POINTER_MOVE ? animatedMenuLines[i] : (menuLines[i]?.line ?? "")}
                  </div>
                );
              })}
            </div>
          )}

          {/* Summary */}
          {frame >= F_SUMMARY && (
            <pre
              style={{
                opacity: summaryOpacity,
                color: colors.orange300,
                fontFamily: fonts.mono,
                fontSize: 22,
                lineHeight: 1.6,
                margin: 0,
                whiteSpace: "pre",
              }}
            >
              {SUMMARY}
            </pre>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

**Step 2: Verify**

In studio, scrub to frame 2040 (68s). Terminal appears. At 2250 (75s), `./capcat catch` should be typing. At 2310 (77s), ASCII logo visible. At 2430 (81s), TUI menu fully rendered.

---

## Task 9: OutroScene (97–110s, 390 local frames)

**Files:**
- Modify: `Video/src/scenes/OutroScene.tsx` (replace existing)

```tsx
import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/SourceSerif4";
import { colors, fontSizes, fonts, spacing } from "../tokens";

const { fontFamily } = loadFont("normal", {
  weights: ["700"],
  subsets: ["latin"],
});

const UPPER_HEIGHT = 756;

export const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Crowd fades in immediately
  const crowdOpacity = interpolate(frame, [0, 30], [0, 0.35], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  // Cat spring bounces in from below at frame 0
  const catProgress = spring({
    frame,
    fps,
    config: { damping: 8, stiffness: 80 }, // bouncy
    durationInFrames: 45,
  });
  const catY = interpolate(catProgress, [0, 1], [300, 0]);

  // "capcat.org" types in at frame 0 in orange
  const urlChars = Math.max(0, frame * 4);
  const urlText = "capcat.org".slice(0, urlChars);

  // Final fade out over last 60 frames
  const finalFade = interpolate(
    frame,
    [durationInFrames - 60, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: colors.paper, opacity: finalFade }}>
      {/* Crowd background — full width, upper zone */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: UPPER_HEIGHT, overflow: "hidden" }}>
        <Img
          src={staticFile("Crowd.svg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity: crowdOpacity,
            filter: "grayscale(40%) brightness(1.1)",
          }}
        />
      </div>

      {/* Cat centered in upper zone */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: UPPER_HEIGHT,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transform: `translateY(${catY}px)`,
        }}
      >
        <Img
          src={staticFile("Capcat-Cat-Color.svg")}
          style={{ width: 300, height: 300 }}
        />
      </div>

      {/* capcat.org typewriter in subtitle strip */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 324,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            fontFamily,
            fontSize: 56,
            fontWeight: 700,
            color: colors.accentPrimary,
            letterSpacing: 2,
          }}
        >
          {urlText}
          {urlText.length < 10 && (
            <span style={{ opacity: frame % 10 < 5 ? 1 : 0 }}>▌</span>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

**Step 2: Verify**

Scrub to frame 2910 (97s). Crowd fades in, cat bounces, "capcat.org" types out. Cat should have visible bounce (3–4 oscillations before settling).

---

## Task 10: CapcatIntro composition (wire everything)

**Files:**
- Modify: `Video/src/compositions/CapcatIntro.tsx` (replace entirely)

This is the final assembly. `<Audio>` plays the narration. `<Series>` sequences all 7 scenes. `<SubtitleStrip>` is an absolute overlay on top of everything.

**Note on frame counts per scene:**
| Scene | Duration | Frames |
|-------|----------|--------|
| BrowsingScene | 0–17s | 510 |
| ProblemScene | 17–35s | 540 |
| FileFirstScene | 35–47s | 360 |
| MarkdownScene | 47–56s | 270 |
| HtmlScene | 56–68s | 360 |
| TerminalScene | 68–97s | 870 |
| OutroScene | 97–115s | 540 |
| **Total** | | **3450** |

**Step 1: Replace `Video/src/compositions/CapcatIntro.tsx`**

`TransitionSeries` replaces `Series`. Each `<TransitionSeries.Transition>` between scenes
overlaps both neighbours by its duration, shortening the total timeline by that amount.

`SubtitleStrip` is placed **outside** `TransitionSeries` as a direct child of `AbsoluteFill`
so it receives the global composition frame — required for audio-synced subtitle timing.

Per-scene `sceneOpacity` fade-out code in individual scenes can be removed — transitions
handle the visual handoff. The existing code won't break if left in, but it causes a
double-fade. Remove the `interpolate(frame, [N, N+10], [1, 0])` opacity lines from each scene.

```tsx
import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import {
  TransitionSeries,
  linearTiming,
  springTiming,
} from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { BrowsingScene } from "../scenes/BrowsingScene";
import { ProblemScene } from "../scenes/ProblemScene";
import { FileFirstScene } from "../scenes/FileFirstScene";
import { MarkdownScene } from "../scenes/MarkdownScene";
import { HtmlScene } from "../scenes/HtmlScene";
import { TerminalScene } from "../scenes/TerminalScene";
import { OutroScene } from "../scenes/OutroScene";
import { SubtitleStrip } from "../SubtitleStrip";

// Transition durations (frames)
const T = 15;   // standard transition
const T_OUT = 20; // terminal → outro (softer close)

export const CapcatIntro: React.FC = () => {
  return (
    <AbsoluteFill>
      {/* Audio — global, not inside any Sequence */}
      <Audio src={staticFile("AudioVersionFinalNonMastered.mp4")} />

      {/* Scene sequence with transitions */}
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={510}>
          <BrowsingScene />
        </TransitionSeries.Sequence>

        {/* Browsing → Problem: fade — same emotional space */}
        <TransitionSeries.Transition
          presentation={fade()}
          timing={springTiming({ config: { damping: 200 }, durationInFrames: T })}
        />

        <TransitionSeries.Sequence durationInFrames={540}>
          <ProblemScene />
        </TransitionSeries.Sequence>

        {/* Problem → FileFirst: slide from right — solution pivot */}
        <TransitionSeries.Transition
          presentation={slide({ direction: "from-right" })}
          timing={springTiming({ config: { damping: 200 }, durationInFrames: T })}
        />

        <TransitionSeries.Sequence durationInFrames={360}>
          <FileFirstScene />
        </TransitionSeries.Sequence>

        {/* FileFirst → Markdown: fade — same file-first theme */}
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: T })}
        />

        <TransitionSeries.Sequence durationInFrames={270}>
          <MarkdownScene />
        </TransitionSeries.Sequence>

        {/* Markdown → Html: slide from right — next output format */}
        <TransitionSeries.Transition
          presentation={slide({ direction: "from-right" })}
          timing={springTiming({ config: { damping: 200 }, durationInFrames: T })}
        />

        <TransitionSeries.Sequence durationInFrames={360}>
          <HtmlScene />
        </TransitionSeries.Sequence>

        {/* Html → Terminal: wipe — dramatic dark reveal */}
        <TransitionSeries.Transition
          presentation={wipe({ direction: "from-left" })}
          timing={springTiming({ config: { damping: 200 }, durationInFrames: T })}
        />

        <TransitionSeries.Sequence durationInFrames={870}>
          <TerminalScene />
        </TransitionSeries.Sequence>

        {/* Terminal → Outro: fade — soft close */}
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: T_OUT })}
        />

        <TransitionSeries.Sequence durationInFrames={540}>
          <OutroScene />
        </TransitionSeries.Sequence>
      </TransitionSeries>

      {/* Subtitle strip — outside TransitionSeries, gets global frame for audio sync */}
      <SubtitleStrip />
    </AbsoluteFill>
  );
};
```

**Step 2: Sync everything to run location**

```bash
rsync -a /tmp/capcat-video-run/src/ "Video/src/"
rsync -a "Video/src/" /tmp/capcat-video-run/src/
```

**Step 3: Verify full composition in studio**

- Frame 0: BrowsingScene, Globe + BookmarkCheck icons visible
- Frame 90 (3s): Subtitle "Open a website, scan..."
- Frame 510 (17s): ProblemScene, BookmarkX + FileQuestion
- Frame 1050 (35s): FileFirstScene, folder icon
- Frame 1680 (56s): HtmlScene, HTML icon
- Frame 2040 (68s): TerminalScene, dark terminal
- Frame 2310 (77s): ASCII logo in terminal
- Frame 2910 (97s): OutroScene, cat bounces in
- Audio should play through entire sequence

---

## Task 11: Install lucide-react and final sync

**Step 1: Install in run location**

```bash
cd /tmp/capcat-video-run && npm install lucide-react
```

**Step 2: Add to Video/package.json**

Add to `dependencies`:
```json
"lucide-react": "^0.460.0"
```

**Step 3: Copy audio file to public/**

```bash
cp "Video/Audio/AudioVersionFinalNonMastered.mp4" /tmp/capcat-video-run/public/
cp "Video/Audio/AudioVersionFinalNonMastered.mp4" "Video/public/"
```

**Step 4: Copy missing icons**

```bash
cp docs/icons/Crowd.svg /tmp/capcat-video-run/public/
cp docs/icons/Crowd.svg Video/public/
cp docs/icons/Interactive-Menu-icon.svg /tmp/capcat-video-run/public/
cp docs/icons/Interactive-Menu-icon.svg Video/public/
```

**Step 5: Final studio check**

Open studio at localhost:3001. Play the full composition. Verify:
- [ ] Audio plays
- [ ] Subtitles appear and match audio timing
- [ ] All scene transitions are clean
- [ ] Terminal animation shows full TUI sequence
- [ ] Cat bounces in at 97s
- [ ] "capcat.org" types out in orange
- [ ] Final fade to paper white

---

## Polishing pass (after approval)

These are deferred — do not implement yet:
- Fine-tune subtitle timing offsets if audio drifts
- Adjust icon sizes/positions per feedback
- Add background tint to subtitle strip if text is hard to read on terminal scene
- Tweak cat bounce spring parameters
- Consider adding `Offline-Accessibility-icon.svg` to MarkdownScene or HtmlScene
