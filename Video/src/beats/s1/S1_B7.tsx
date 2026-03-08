import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { BrowserChrome } from "../../components/BrowserChrome";
import { Typewriter } from "../../components/Typewriter";

const TEXT = "If it has added value";

export const S1_B7: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Subtle scale pulse 1 → 1.02 → 1
  const scale = 1 + 0.02 * Math.sin((frame / durationInFrames) * Math.PI);

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ transform: `scale(${scale})` }}>
          <BrowserChrome content="website" bookmarkFilled />
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
