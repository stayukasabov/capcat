import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";

const TEXT = "Capcat?";

export const S5_B3: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Crowd reveals from center behind cat — fast spring translateY upward
  const crowdY = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 200 },
    durationInFrames: 20,
  });

  const crowdTranslateY = interpolate(crowdY, [0, 1], [200, 0]);
  const crowdOpacity = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative", width: 500, height: 400 }}>
          {/* Crowd behind */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              opacity: crowdOpacity,
              transform: `translateY(${crowdTranslateY}px)`,
              display: "flex",
              alignItems: "flex-end",
              justifyContent: "center",
            }}
          >
            <Img
              src={staticFile("ILLUSTRATION/Crowd.svg")}
              style={{ width: 500, height: 300 }}
            />
          </div>
          {/* Cat on top, centered */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Img
              src={staticFile("ILLUSTRATION/Capcat-Cat-Color.svg")}
              style={{ width: 320, height: 320 }}
            />
          </div>
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
