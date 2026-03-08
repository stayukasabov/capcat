import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "A folder with a title";

export const S4_B5: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const folderScale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 16 });

  // Title typewriters on folder tab
  const titleChars = Math.min(12, Math.floor(Math.max(0, frame - 16) * 4));
  const title = "2026-03-08-article".slice(0, titleChars);

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ transform: `scale(${folderScale})`, position: "relative" }}>
          {/* Folder tab */}
          <div
            style={{
              position: "absolute",
              top: -24,
              left: 0,
              width: 160,
              height: 24,
              backgroundColor: colors.accentLight,
              borderRadius: "6px 6px 0 0",
              display: "flex",
              alignItems: "center",
              paddingLeft: 10,
              fontSize: 12,
              fontFamily: "SF Mono, monospace",
              color: colors.imprint,
              overflow: "hidden",
              whiteSpace: "nowrap",
            }}
          >
            {title}
          </div>
          {/* Folder body */}
          <div
            style={{
              width: 280,
              height: 180,
              backgroundColor: colors.accentLighter,
              borderRadius: "0 8px 8px 8px",
              border: `1px solid ${colors.borderColor}`,
            }}
          />
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
