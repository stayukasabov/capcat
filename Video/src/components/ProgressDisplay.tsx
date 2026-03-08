import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { colors, fonts } from "../tokens";

const SPINNER_CHARS = ["◒", "◓", "◔", "◕"];
const TOTAL_ITEMS = 27;
const DOT_COUNT = 6;

function getStatus(pct: number): string {
  if (pct < 0.15) return "STARTING";
  if (pct < 0.55) return "FETCHING";
  if (pct < 0.9) return "CONVERTING";
  return "COMPLETE";
}

export const ProgressDisplay: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = interpolate(frame, [10, durationInFrames - 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const spinner = SPINNER_CHARS[Math.floor(frame / 8) % SPINNER_CHARS.length];
  const currentItem = Math.floor(progress * TOTAL_ITEMS);
  const pct = (currentItem / TOTAL_ITEMS) * 100;
  const filledDots = Math.floor(progress * DOT_COUNT);
  const dots = Array.from({ length: DOT_COUNT }, (_, i) => i < filledDots ? "◉" : "◎").join(" ");
  const status = getStatus(progress);

  return (
    <div
      style={{
        backgroundColor: "#1a1212",
        borderRadius: 10,
        padding: "20px 28px",
        fontFamily: fonts.mono,
        fontSize: 22,
        color: colors.accentPrimary,
        minWidth: 640,
        boxShadow: "0 4px 32px rgba(0,0,0,0.5)",
      }}
    >
      {`${spinner} CATCHING ▶  NATURE ${dots}  ${currentItem}/${TOTAL_ITEMS} (${pct.toFixed(1)}%) (${status})`}
    </div>
  );
};
