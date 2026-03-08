import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Every day";

const DAYS = ["MON", "TUE", "WED"];

export const S3_B2: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const framesPerDay = Math.floor(durationInFrames / 3);

  const currentDay = Math.min(2, Math.floor(frame / framesPerDay));
  const dayProgress = (frame % framesPerDay) / framesPerDay;

  // Page flip: rotateX 0 → -90° over half frame, then snap to next
  const flipAngle = interpolate(dayProgress, [0, 0.4, 0.5, 1], [0, -90, 0, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div
          style={{
            width: 220,
            height: 260,
            backgroundColor: colors.paper,
            border: `2px solid ${colors.borderColor}`,
            borderRadius: 8,
            boxShadow: "0 4px 24px rgba(26,18,18,0.12)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {/* Calendar header */}
          <div
            style={{
              backgroundColor: colors.accentPrimary,
              color: "#fff",
              textAlign: "center",
              padding: "8px 0",
              fontSize: 18,
              fontFamily: "SF Mono, monospace",
              fontWeight: 700,
            }}
          >
            {DAYS[currentDay]}
          </div>
          {/* Day number flipping */}
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 80,
              fontWeight: 700,
              color: colors.imprint,
              transform: `perspective(400px) rotateX(${flipAngle}deg)`,
            }}
          >
            {currentDay + 1}
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
