import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Catalogue later";

export const S4_B2: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const drawerX = interpolate(frame, [4, 22], [0, 120], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", width: 320, height: 200 }}>
          {/* Cabinet body */}
          <div
            style={{
              width: 200,
              height: 160,
              backgroundColor: colors.imprintLight,
              borderRadius: 6,
              position: "absolute",
              left: 0,
            }}
          />
          {/* Drawer slides out */}
          <div
            style={{
              position: "absolute",
              top: 40,
              left: 0,
              width: 190,
              height: 80,
              backgroundColor: colors.imprintMuted,
              borderRadius: 4,
              transform: `translateX(${drawerX}px)`,
              display: "flex",
              alignItems: "center",
              paddingLeft: 16,
            }}
          >
            <div
              style={{
                width: 30,
                height: 8,
                backgroundColor: colors.accentPrimary,
                borderRadius: 4,
              }}
            />
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
