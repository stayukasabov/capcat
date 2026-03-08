import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Plus Code Coloring";

const CODE_TOKENS = [
  { text: "const", color: "#7c3aed", delay: 0 },
  { text: " fetch", color: colors.accentPrimary, delay: 4 },
  { text: " =", color: colors.imprintMuted, delay: 8 },
  { text: " async", color: "#7c3aed", delay: 12 },
  { text: "(url)", color: colors.imprint, delay: 16 },
  { text: " => {", color: colors.imprintMuted, delay: 20 },
];

export const S4_B11: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div
          style={{
            backgroundColor: "#1a1212",
            borderRadius: 10,
            padding: "20px 28px",
            fontFamily: "SF Mono, monospace",
            fontSize: 22,
            lineHeight: 1.8,
          }}
        >
          {CODE_TOKENS.map((token, i) => {
            const opacity = interpolate(frame, [token.delay, token.delay + 6], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <span key={i} style={{ color: token.color, opacity }}>
                {token.text}
              </span>
            );
          })}
          <br />
          {[
            { text: "  return", color: "#7c3aed", delay: 24 },
            { text: " markdown", color: colors.accentLight, delay: 28 },
            { text: "(await", color: colors.imprintMuted, delay: 32 },
            { text: " res", color: colors.imprint, delay: 36 },
            { text: ".text())", color: colors.imprintMuted, delay: 40 },
          ].map((token, i) => {
            const opacity = interpolate(frame, [token.delay, token.delay + 6], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <span key={i} style={{ color: token.color, opacity }}>
                {token.text}
              </span>
            );
          })}
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
