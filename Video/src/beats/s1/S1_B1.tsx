import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { BrowserChrome } from "../../components/BrowserChrome";
import { Typewriter } from "../../components/Typewriter";

const TEXT = "This is my browsing workflow";

export const S1_B1: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 20 });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ transform: `scale(${scale})` }}>
          <BrowserChrome content="empty" />
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
