import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Date";

export const S4_B3: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 8, stiffness: 300 }, durationInFrames: 14 });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", width: 280, height: 200 }}>
          {/* Document */}
          <div
            style={{
              width: 180,
              height: 220,
              backgroundColor: "#fff",
              border: `1px solid ${colors.borderColor}`,
              borderRadius: 6,
              boxShadow: "0 4px 16px rgba(26,18,18,0.1)",
              position: "absolute",
              top: 0,
              left: "50%",
              transform: "translateX(-50%)",
            }}
          />
          {/* Date stamp */}
          <div
            style={{
              position: "absolute",
              top: "30%",
              left: "50%",
              transform: `translate(-50%, -50%) scale(${scale}) rotate(-8deg)`,
              backgroundColor: colors.accentPrimary,
              color: "#fff",
              fontFamily: "SF Mono, monospace",
              fontSize: 20,
              fontWeight: 700,
              padding: "6px 14px",
              borderRadius: 4,
              border: "3px solid rgba(255,255,255,0.4)",
              whiteSpace: "nowrap",
            }}
          >
            2026-03-08
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
