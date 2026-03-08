import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Quick to Archive";

export const S4_B13: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Zipper close: clip-path height shrinks from 100% to 0%
  const zipProgress = interpolate(frame, [4, 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const checkScale = spring({ frame: frame - 22, fps, config: { damping: 200 }, durationInFrames: 12 });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", width: 200, height: 220 }}>
          {/* ZIP icon */}
          <div style={{ fontSize: 100 }}>🗜️</div>
          {/* Zipper bar closing from bottom */}
          <div
            style={{
              position: "absolute",
              bottom: 30,
              left: "10%",
              width: "80%",
              height: `${(1 - zipProgress) * 60}%`,
              backgroundColor: colors.accentPrimary,
              borderRadius: 4,
              opacity: 0.7,
            }}
          />
          {/* Checkmark appears after zip */}
          <div
            style={{
              position: "absolute",
              bottom: -10,
              right: -10,
              width: 48,
              height: 48,
              borderRadius: "50%",
              backgroundColor: "#27c93f",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 24,
              transform: `scale(${checkScale})`,
            }}
          >
            ✓
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
