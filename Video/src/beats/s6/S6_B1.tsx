import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors, fonts } from "../../tokens";

const TEXT = "Command Line mode";
const COMMAND = "./capcat fetch hn --count 5";
const CHARS_PER_FRAME = 3;

export const S6_B1: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const iconScale = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 16 });

  const terminalOpacity = interpolate(frame, [12, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const cmdChars = Math.min(COMMAND.length, Math.floor(Math.max(0, frame - 20) * CHARS_PER_FRAME));
  const displayed = COMMAND.slice(0, cmdChars);

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
          <Img
            src={staticFile("ILLUSTRATION/Command-Line-Mode-icon.svg")}
            style={{ width: 120, height: 120, transform: `scale(${iconScale})` }}
          />
          <div
            style={{
              opacity: terminalOpacity,
              backgroundColor: "#1a1212",
              borderRadius: 10,
              padding: "16px 24px",
              fontFamily: fonts.mono,
              fontSize: 20,
              color: colors.accentPrimary,
              minWidth: 420,
            }}
          >
            <span style={{ color: colors.imprintMuted }}>$ </span>
            {displayed}
            {cmdChars < COMMAND.length && (
              <span style={{ color: colors.accentPrimary }}>▌</span>
            )}
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
