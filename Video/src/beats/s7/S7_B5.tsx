import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

// Full-frame center takeover — no illustration zone split, no text zone duplication
export const S7_B5: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const glowPulse = 1 + 0.04 * Math.sin((frame / durationInFrames) * Math.PI * 4);

  const chars = Math.min("Capcat.org".length, Math.floor(Math.max(0, frame - 4) * 3));
  const displayed = "Capcat.org".slice(0, chars);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.paper,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          fontFamily,
          fontSize: 80,
          fontWeight: 700,
          color: colors.accentPrimary,
          textAlign: "center",
          transform: `scale(${glowPulse})`,
          textShadow: `0 0 ${glowPulse * 20}px rgba(241,84,13,0.3)`,
        }}
      >
        {displayed}
        {chars < "Capcat.org".length && (
          <span style={{ color: colors.accentPrimary }}>▌</span>
        )}
      </div>
    </AbsoluteFill>
  );
};
