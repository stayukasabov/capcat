import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Ready to share";

export const S4_B12: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const iconScale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 14 });

  // 3 concentric ripple rings
  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center", width: 300, height: 300 }}>
          {[0, 1, 2].map((i) => {
            const ringProgress = interpolate(
              frame,
              [i * 8, i * 8 + 30],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            const size = 60 + ringProgress * 160;
            const ringOpacity = interpolate(ringProgress, [0.3, 1], [0.5, 0]);
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  width: size,
                  height: size,
                  borderRadius: "50%",
                  border: `2px solid ${colors.accentPrimary}`,
                  opacity: ringOpacity,
                }}
              />
            );
          })}
          <div style={{ fontSize: 64, transform: `scale(${iconScale})`, zIndex: 1 }}>
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
