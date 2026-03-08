import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "HTML version with Dark and Light Theme";

export const S4_B10: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const iconScale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 16 });

  const splitProgress = interpolate(frame, [16, 32], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const leftX = -splitProgress * 60;
  const rightX = splitProgress * 60;

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
          <Img
            src={staticFile("ILLUSTRATION/HTML-Generation-icon.svg")}
            style={{ width: 140, height: 140, transform: `scale(${iconScale})` }}
          />
          {/* Split browser halves */}
          <div style={{ display: "flex", gap: 4 }}>
            {/* Light half */}
            <div
              style={{
                width: 100,
                height: 140,
                backgroundColor: "#faf5ee",
                borderRadius: "8px 0 0 8px",
                border: `1px solid ${colors.borderColor}`,
                transform: `translateX(${leftX}px)`,
                overflow: "hidden",
              }}
            >
              <div style={{ height: 20, backgroundColor: colors.imprintLight }} />
              <div style={{ padding: 8, display: "flex", flexDirection: "column", gap: 4 }}>
                {[70, 50, 80].map((w, i) => (
                  <div key={i} style={{ height: 5, width: `${w}%`, backgroundColor: colors.imprint, borderRadius: 2 }} />
                ))}
              </div>
            </div>
            {/* Dark half */}
            <div
              style={{
                width: 100,
                height: 140,
                backgroundColor: "#1a1212",
                borderRadius: "0 8px 8px 0",
                border: `1px solid ${colors.borderColor}`,
                transform: `translateX(${rightX}px)`,
                overflow: "hidden",
              }}
            >
              <div style={{ height: 20, backgroundColor: "#3a3737" }} />
              <div style={{ padding: 8, display: "flex", flexDirection: "column", gap: 4 }}>
                {[70, 50, 80].map((w, i) => (
                  <div key={i} style={{ height: 5, width: `${w}%`, backgroundColor: "#827c7c", borderRadius: 2 }} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} charsPerFrame={5} />
      </TextZone>
    </BeatWrapper>
  );
};
