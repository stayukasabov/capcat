import React from "react";
import { Img, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { ProgressDisplay } from "../../components/ProgressDisplay";

const TEXT = "Bulk RSS fetching";

export const S6_B3: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const iconScale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 16 });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
          <Img
            src={staticFile("ILLUSTRATION/Bulk-RSS-Fetching-icon.svg")}
            style={{ width: 80, height: 80, transform: `scale(${iconScale})` }}
          />
          <ProgressDisplay />
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
