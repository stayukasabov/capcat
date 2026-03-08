import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Defined with natural language processing";
const WORDS = TEXT.split(" ");

export const S7_B6: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();

  const framesPerWord = 6;

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 12,
            maxWidth: 700,
            justifyContent: "center",
            padding: 40,
          }}
        >
          {WORDS.map((word, i) => {
            const highlight = interpolate(
              frame,
              [i * framesPerWord, i * framesPerWord + framesPerWord],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            return (
              <span
                key={i}
                style={{
                  fontFamily,
                  fontSize: 32,
                  fontWeight: 400,
                  color: highlight > 0.5 ? colors.accentPrimary : colors.imprintMuted,
                  backgroundColor: highlight > 0.5 ? `rgba(241,84,13,0.1)` : "transparent",
                  padding: "2px 6px",
                  borderRadius: 4,
                }}
              >
                {word}
              </span>
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
