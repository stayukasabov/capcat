import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "I have to dig into the bookmarks and clippings";

const FOLDERS = [
  { delay: 0, rotate: -12, x: -180 },
  { delay: 6, rotate: 8, x: -60 },
  { delay: 10, rotate: -5, x: 60 },
  { delay: 14, rotate: 15, x: 180 },
  { delay: 18, rotate: -9, x: 0 },
];

const Folder: React.FC<{ delay: number; rotate: number; x: number; frame: number; fps: number }> = ({
  delay, rotate, x, frame, fps,
}) => {
  const y = interpolate(
    spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 12, stiffness: 120 } }),
    [0, 1],
    [-300, 0]
  );
  return (
    <div
      style={{
        position: "absolute",
        transform: `translateX(${x}px) translateY(${y}px) rotate(${rotate}deg)`,
        fontSize: 64,
      }}
    >
      📁
    </div>
  );
};

export const S2_B1: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", width: 500, height: 300 }}>
          {FOLDERS.map((f, i) => (
            <Folder key={i} {...f} frame={frame} fps={fps} />
          ))}
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} charsPerFrame={5} />
      </TextZone>
    </BeatWrapper>
  );
};
