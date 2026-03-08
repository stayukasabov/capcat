import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";

const TEXT = "And organize";

export const S2_B4: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Folder tries to move right, snaps back — 2 cycles
  const cycle = (frame % Math.floor(durationInFrames / 2)) / Math.floor(durationInFrames / 2);
  const dragX = Math.sin(cycle * Math.PI) * 80;

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div
          style={{
            fontSize: 80,
            transform: `translateX(${dragX}px)`,
            cursor: "grabbing",
          }}
        >
          📁
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
