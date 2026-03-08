import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Source";

export const S4_B4: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Two chain links connect left to right
  const linkProgress = interpolate(frame, [4, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const link2X = interpolate(linkProgress, [0, 1], [-60, 0]);
  const link2Opacity = linkProgress;

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ display: "flex", alignItems: "center", gap: 0 }}>
          <div style={{ fontSize: 72 }}>🔗</div>
          <div
            style={{
              fontSize: 72,
              opacity: link2Opacity,
              transform: `translateX(${link2X}px)`,
            }}
          >
            🔗
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
