import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "And I am still missing valuable information";

export const S3_B1: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Magnifying glass sweeps left → right
  const glassX = interpolate(frame, [0, durationInFrames - 10], [-200, 200], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", width: 500, height: 300 }}>
          {/* Empty dotted area — nothing to find */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              border: `2px dashed ${colors.borderColor}`,
              borderRadius: 16,
              opacity: 0.4,
            }}
          />
          {/* Magnifying glass emoji sweeps */}
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              fontSize: 64,
              transform: `translate(calc(-50% + ${glassX}px), -50%)`,
            }}
          >
            🔍
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} charsPerFrame={5} />
      </TextZone>
    </BeatWrapper>
  );
};
