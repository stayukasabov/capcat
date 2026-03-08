import React from "react";
import { Img, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";

const TEXT = "Local Markdown storage";

export const S6_B4: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 20 });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <Img
          src={staticFile("ILLUSTRATION/Local-Markdown-Storage-icon.svg")}
          style={{ width: 280, height: 280, transform: `scale(${scale})` }}
        />
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
