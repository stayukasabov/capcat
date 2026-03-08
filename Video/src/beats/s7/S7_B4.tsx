import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "For developers, researchers and tech enthusiasts";

const SILHOUETTES = [
  { emoji: "💻", label: "dev", delay: 0 },
  { emoji: "🔬", label: "researcher", delay: 8 },
  { emoji: "⚡", label: "enthusiast", delay: 16 },
];

export const S7_B4: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ display: "flex", gap: 40, alignItems: "flex-end" }}>
          {SILHOUETTES.map((s, i) => {
            const slideX = interpolate(
              spring({ frame: frame - s.delay, fps, config: { damping: 200 }, durationInFrames: 18 }),
              [0, 1],
              [-200, 0]
            );
            const opacity = interpolate(frame, [s.delay, s.delay + 10], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <div
                key={i}
                style={{
                  transform: `translateX(${slideX}px)`,
                  opacity,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 12,
                }}
              >
                <div style={{ fontSize: 72 }}>{s.emoji}</div>
                <div
                  style={{
                    fontSize: 16,
                    color: colors.imprintMuted,
                    fontFamily: "SF Mono, monospace",
                    textTransform: "lowercase",
                  }}
                >
                  {s.label}
                </div>
              </div>
            );
          })}
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} charsPerFrame={5} />
      </TextZone>
    </BeatWrapper>
  );
};
