import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { colors, fonts } from "../tokens";

const ASCII_LOGO = `       ____
     / ____|                     _
    | |     __ _ _ __   ___ __ _| |_
    | |    / _  |  _ \\  / __/ _  | __|
    | |___| (_| | |_) | (_| (_| | |_
     \\_____\\__,_|  __/ \\___\\__,_|\\__|
                | |
                |_|`;

const MENU_OPTIONS = [
  "Catch articles from a bundle of sources",
  "Catch articles from a list of sources",
  "Catch from a single source",
  "Catch a single article by URL",
  "Manage Sources (add/remove/configure)",
  "Exit",
];

const FRAMES_PER_STEP = 12;
const MENU_START_FRAME = 40;

export const TUIDisplay: React.FC = () => {
  const frame = useCurrentFrame();

  const logoOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const menuStart = 20;
  const menuLineOpacity = (i: number) =>
    interpolate(frame, [menuStart + i * 3, menuStart + i * 3 + 6], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const pointerIndex = (() => {
    if (frame < MENU_START_FRAME) return 0;
    const step = Math.floor((frame - MENU_START_FRAME) / FRAMES_PER_STEP);
    const sequence = [0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0];
    return sequence[Math.min(step, sequence.length - 1)];
  })();

  return (
    <div
      style={{
        backgroundColor: "#1a1212",
        borderRadius: 10,
        padding: "20px 28px",
        fontFamily: fonts.mono,
        fontSize: 18,
        lineHeight: 1.6,
        minWidth: 640,
        boxShadow: "0 4px 32px rgba(0,0,0,0.5)",
      }}
    >
      <pre style={{ color: colors.accentPrimary, opacity: logoOpacity, margin: "0 0 16px", fontSize: 15 }}>
        {ASCII_LOGO}
      </pre>
      <div style={{ opacity: menuLineOpacity(0), color: colors.imprintMuted }}>
        {"   What would you like me to do?"}
      </div>
      <div style={{ opacity: menuLineOpacity(1), color: colors.imprintMuted, marginBottom: 4 }}>
        {"   (Use arrow keys to navigate)"}
      </div>
      {MENU_OPTIONS.map((opt, i) => (
        <div
          key={i}
          style={{
            opacity: menuLineOpacity(i + 2),
            color: i === pointerIndex ? colors.accentPrimary : colors.imprintMuted,
            fontFamily: fonts.mono,
          }}
        >
          {i === pointerIndex ? ` ▶ ${opt}` : `   ${opt}`}
        </div>
      ))}
    </div>
  );
};
