import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "To label";

export const S2_B2: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();

  const tagX = interpolate(frame, [4, 18], [200, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", width: 400, height: 200 }}>
          {/* Folder stack */}
          <div style={{ fontSize: 80, textAlign: "center" }}>📁</div>
          {/* Label tag slides in from right */}
          <div
            style={{
              position: "absolute",
              top: 20,
              right: -20,
              transform: `translateX(${tagX}px)`,
              backgroundColor: colors.accentPrimary,
              color: "#fff",
              fontSize: 18,
              fontFamily: "SF Mono, monospace",
              padding: "4px 14px 4px 10px",
              borderRadius: "4px 16px 16px 4px",
              boxShadow: "0 2px 8px rgba(241,84,13,0.3)",
            }}
          >
            label
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
