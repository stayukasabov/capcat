import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Easy to Read";

export const S4_B14: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Book cover rotates open
  const coverAngle = interpolate(frame, [0, 20], [-80, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Text lines draw in after book opens
  const lineCount = Math.floor(
    interpolate(frame, [20, 50], [0, 6], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ display: "flex", gap: 0, perspective: 600 }}>
          {/* Cover */}
          <div
            style={{
              width: 130,
              height: 200,
              backgroundColor: colors.accentPrimary,
              borderRadius: "4px 0 0 4px",
              transformOrigin: "right center",
              transform: `rotateY(${coverAngle}deg)`,
              boxShadow: "-4px 4px 16px rgba(0,0,0,0.2)",
            }}
          />
          {/* Pages */}
          <div
            style={{
              width: 180,
              height: 200,
              backgroundColor: "#fff",
              borderRadius: "0 4px 4px 0",
              border: `1px solid ${colors.borderColor}`,
              padding: 16,
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                style={{
                  height: 6,
                  backgroundColor: i < lineCount ? colors.imprintMuted : "transparent",
                  borderRadius: 3,
                  width: i % 3 === 2 ? "60%" : "100%",
                  transition: "none",
                }}
              />
            ))}
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
