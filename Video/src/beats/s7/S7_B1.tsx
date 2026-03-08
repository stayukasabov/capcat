import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Archive with confidence";

export const S7_B1: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const zipProgress = interpolate(frame, [4, 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const checkScale = spring({ frame: frame - 22, fps, config: { damping: 200 }, durationInFrames: 12 });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", width: 200, height: 220 }}>
          <div style={{ fontSize: 100 }}>🗄️</div>
          <div
            style={{
              position: "absolute",
              bottom: 30,
              left: "10%",
              width: "80%",
              height: `${(1 - zipProgress) * 50}%`,
              backgroundColor: colors.accentPrimary,
              borderRadius: 4,
              opacity: 0.7,
            }}
          />
          <div
            style={{
              position: "absolute",
              bottom: -10,
              right: -10,
              width: 52,
              height: 52,
              borderRadius: "50%",
              backgroundColor: "#27c93f",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 26,
              color: "#fff",
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
