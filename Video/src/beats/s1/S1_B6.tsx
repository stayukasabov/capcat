import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { BrowserChrome } from "../../components/BrowserChrome";
import { Typewriter } from "../../components/Typewriter";

const TEXT = "Bookmark";

export const S1_B6: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();

  // Bookmark star fills orange over 20 frames
  const filled = frame >= 20;

  return (
    <BeatWrapper>
      <IllustrationZone>
        <BrowserChrome content="website" bookmarkFilled={filled} />
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
