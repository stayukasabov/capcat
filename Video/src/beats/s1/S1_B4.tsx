import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { BrowserChrome } from "../../components/BrowserChrome";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Choose article";

export const S1_B4: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Cursor dot moves to card 1 (center card)
  const cursorX = interpolate(frame, [4, 16], [-200, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cursorY = interpolate(frame, [4, 16], [80, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Border pulse on selected card
  const pulse = spring({ frame: frame - 16, fps, config: { damping: 8, stiffness: 200 }, durationInFrames: 12 });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative" }}>
          <BrowserChrome content="selected" highlightCard />
          {/* Cursor dot */}
          <div
            style={{
              position: "absolute",
              bottom: 120,
              left: "50%",
              width: 14,
              height: 14,
              borderRadius: "50%",
              backgroundColor: colors.accentPrimary,
              transform: `translate(calc(-50% + ${cursorX}px), ${cursorY}px)`,
              boxShadow: `0 0 0 ${pulse * 6}px rgba(241,84,13,0.2)`,
            }}
          />
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
