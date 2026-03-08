import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Clean data for Obsidian graph";

const GRAPH_NODES = [
  { x: 160, y: 80, delay: 0 },
  { x: 80,  y: 180, delay: 8 },
  { x: 260, y: 160, delay: 12 },
  { x: 180, y: 260, delay: 18 },
];
const GRAPH_EDGES = [
  { x1: 160, y1: 80, x2: 80,  y2: 180, delay: 6 },
  { x1: 160, y1: 80, x2: 260, y2: 160, delay: 10 },
  { x1: 80,  y1: 180, x2: 180, y2: 260, delay: 16 },
  { x1: 260, y1: 160, x2: 180, y2: 260, delay: 20 },
];

export const S4_B8: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const nodeScale = (delay: number) =>
    spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 10 });

  const edgeDash = (delay: number, len: number) => {
    const progress = interpolate(frame, [delay, delay + 12], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    return len * (1 - progress);
  };

  return (
    <BeatWrapper>
      <IllustrationZone>
        <svg width={340} height={300} style={{ overflow: "visible" }}>
          {GRAPH_EDGES.map((e, i) => {
            const dx = e.x2 - e.x1;
            const dy = e.y2 - e.y1;
            const len = Math.sqrt(dx * dx + dy * dy);
            const offset = edgeDash(e.delay, len);
            return (
              <line
                key={i}
                x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2}
                stroke={colors.accentLight}
                strokeWidth={1.5}
                strokeDasharray={len}
                strokeDashoffset={offset}
              />
            );
          })}
          {GRAPH_NODES.map((n, i) => (
            <circle
              key={i}
              cx={n.x} cy={n.y} r={18}
              fill={colors.accentPrimary}
              opacity={0.85}
              transform={`scale(${nodeScale(n.delay)})`}
              style={{ transformOrigin: `${n.x}px ${n.y}px` }}
            />
          ))}
        </svg>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
