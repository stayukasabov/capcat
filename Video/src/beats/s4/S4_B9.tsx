import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "Workflow and input for any LLM";

export const S4_B9: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();

  const arrowProgress = interpolate(frame, [8, 28], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const bubbleOpacity = interpolate(frame, [24, 34], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          {/* Circuit/brain source */}
          <div style={{ fontSize: 64 }}>🧠</div>
          {/* Arrow drawing left to right */}
          <svg width={120} height={20} style={{ overflow: "visible" }}>
            <line
              x1={0} y1={10}
              x2={120 * arrowProgress} y2={10}
              stroke={colors.accentPrimary}
              strokeWidth={3}
              strokeLinecap="round"
            />
            {arrowProgress > 0.9 && (
              <polygon
                points={`${120},10 ${108},4 ${108},16`}
                fill={colors.accentPrimary}
              />
            )}
          </svg>
          {/* Chat bubble */}
          <div
            style={{
              opacity: bubbleOpacity,
              backgroundColor: colors.accentLighter,
              borderRadius: "16px 16px 16px 4px",
              padding: "12px 20px",
              fontSize: 28,
              color: colors.imprint,
              fontFamily: "SF Mono, monospace",
              border: `1px solid ${colors.borderColor}`,
            }}
          >
            {"{ }"}
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
