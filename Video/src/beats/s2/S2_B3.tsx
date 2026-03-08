import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Tag";

export const S2_B3: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 8, stiffness: 200 }, durationInFrames: 18 });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", width: 400, height: 200, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ fontSize: 80 }}>📁</div>
          {/* # hashtag overlaps with overshoot spring */}
          <div
            style={{
              position: "absolute",
              transform: `scale(${scale})`,
              fontSize: 96,
              fontFamily: "SF Mono, monospace",
              fontWeight: 700,
              color: colors.accentPrimary,
              opacity: 0.9,
            }}
          >
            #
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
