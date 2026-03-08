import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Structure before I even decide what matters";

// Tree: root node → 2 children → each has 1 child
const NODES = [
  { x: 200, y: 20, delay: 0 },
  { x: 80,  y: 120, delay: 10 },
  { x: 320, y: 120, delay: 14 },
  { x: 20,  y: 220, delay: 22 },
  { x: 380, y: 220, delay: 26 },
];
const EDGES = [
  { x1: 200, y1: 40, x2: 80,  y2: 120, delay: 6 },
  { x1: 200, y1: 40, x2: 320, y2: 120, delay: 10 },
  { x1: 80,  y1: 140, x2: 20, y2: 220, delay: 18 },
  { x1: 320, y1: 140, x2: 380, y2: 220, delay: 22 },
];

export const S4_B6: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();

  const nodeOpacity = (delay: number) =>
    interpolate(frame, [delay, delay + 8], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const edgeLength = (delay: number, len: number) =>
    interpolate(frame, [delay, delay + 10], [0, len], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <svg width={420} height={260} style={{ overflow: "visible" }}>
          {EDGES.map((e, i) => {
            const dx = e.x2 - e.x1;
            const dy = e.y2 - e.y1;
            const fullLen = Math.sqrt(dx * dx + dy * dy);
            const drawn = edgeLength(e.delay, fullLen);
            const ratio = drawn / fullLen;
            return (
              <line
                key={i}
                x1={e.x1}
                y1={e.y1}
                x2={e.x1 + dx * ratio}
                y2={e.y1 + dy * ratio}
                stroke={colors.imprintMuted}
                strokeWidth={2}
              />
            );
          })}
          {NODES.map((n, i) => (
            <circle
              key={i}
              cx={n.x}
              cy={n.y}
              r={20}
              fill={colors.accentLighter}
              stroke={colors.accentPrimary}
              strokeWidth={2}
              opacity={nodeOpacity(n.delay)}
            />
          ))}
        </svg>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} charsPerFrame={5} />
      </TextZone>
    </BeatWrapper>
  );
};
