import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Free and open source software";

// OSI logo: keyhole inside gear — CSS drawn
const OSILogo: React.FC<{ scale: number }> = ({ scale }) => (
  <div style={{ transform: `scale(${scale})`, display: "flex", alignItems: "center", justifyContent: "center" }}>
    <div
      style={{
        width: 140,
        height: 140,
        borderRadius: "50%",
        border: `12px solid ${colors.accentPrimary}`,
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Gear teeth - outer ring notches */}
      {Array.from({ length: 8 }).map((_, i) => {
        const angle = (i * 45 * Math.PI) / 180;
        const x = Math.cos(angle) * 74;
        const y = Math.sin(angle) * 74;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              width: 16,
              height: 16,
              backgroundColor: colors.accentPrimary,
              borderRadius: 3,
              left: "50%",
              top: "50%",
              transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px)) rotate(${i * 45}deg)`,
            }}
          />
        );
      })}
      {/* Keyhole */}
      <div style={{ position: "relative", zIndex: 1 }}>
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: "50%",
            backgroundColor: colors.accentPrimary,
          }}
        />
        <div
          style={{
            width: 18,
            height: 28,
            backgroundColor: colors.accentPrimary,
            margin: "2px auto 0",
            clipPath: "polygon(25% 0%, 75% 0%, 100% 100%, 0% 100%)",
          }}
        />
      </div>
    </div>
  </div>
);

export const S7_B3: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 20 });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <OSILogo scale={scale} />
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} charsPerFrame={5} />
      </TextZone>
    </BeatWrapper>
  );
};
