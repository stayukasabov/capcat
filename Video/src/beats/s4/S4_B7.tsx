import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Markdown files with embedded images";

export const S4_B7: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const iconScale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 18 });
  const thumbOpacity = interpolate(frame, [18, 28], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Img
            src={staticFile("ILLUSTRATION/Local-Markdown-Storage-icon.svg")}
            style={{ width: 220, height: 220, transform: `scale(${iconScale})` }}
          />
          {/* Thumbnail inset */}
          <div
            style={{
              position: "absolute",
              bottom: -10,
              right: -30,
              width: 100,
              height: 70,
              backgroundColor: colors.cardBg,
              border: `1px solid ${colors.borderColor}`,
              borderRadius: 6,
              opacity: thumbOpacity,
              overflow: "hidden",
              boxShadow: "0 4px 12px rgba(26,18,18,0.15)",
            }}
          >
            <div style={{ height: "60%", backgroundColor: colors.accentLighter }} />
            <div style={{ padding: "4px 6px", display: "flex", flexDirection: "column", gap: 3 }}>
              <div style={{ height: 4, backgroundColor: colors.imprintMuted, borderRadius: 2 }} />
              <div style={{ height: 4, backgroundColor: colors.imprintMuted, borderRadius: 2, width: "70%" }} />
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
