import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { BrowserChrome } from "../../components/BrowserChrome";
import { Typewriter } from "../../components/Typewriter";

const TEXT = "Read";

export const S1_B5: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const linesComplete = Math.floor(
    interpolate(frame, [4, durationInFrames - 8], [0, 8], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  return (
    <BeatWrapper>
      <IllustrationZone>
        <BrowserChrome content="selected" highlightCard showReadLines={linesComplete} />
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
