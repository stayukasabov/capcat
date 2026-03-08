import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "What if I capture first";

const DOTS = [
  { delay: 0, x: -60 },
  { delay: 4, x: 0 },
  { delay: 8, x: 60 },
];

export const S4_B1: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const handScale = spring({ frame: frame - 20, fps, config: { damping: 12 }, durationInFrames: 16 });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", width: 300, height: 280 }}>
          {/* Falling dots */}
          {DOTS.map((d, i) => {
            const dotY = interpolate(
              frame,
              [d.delay, d.delay + 18],
              [-120, 80],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  top: "30%",
                  left: "50%",
                  width: 16,
                  height: 16,
                  borderRadius: "50%",
                  backgroundColor: colors.accentPrimary,
                  transform: `translate(calc(-50% + ${d.x}px), ${dotY}px)`,
                }}
              />
            );
          })}
          {/* Hand opening */}
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: "50%",
              transform: `translateX(-50%) scale(${0.6 + handScale * 0.4})`,
              fontSize: 80,
            }}
          >
            🤲
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
