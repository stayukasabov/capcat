import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";

const TEXT = "Capcat";

export const S5_B2: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Cat enters from LEFT with elastic spring
  const catX = spring({
    frame,
    fps,
    config: { damping: 8, stiffness: 120, mass: 0.8 },
    durationInFrames: 30,
  });

  // Motion blur: blur decreases as cat settles
  const blur = interpolate(catX, [0, 0.8, 1], [12, 4, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Cat starts off-screen left (-700px) and settles at center (0)
  const translateX = interpolate(catX, [0, 1], [-700, 0]);

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div
          style={{
            transform: `translateX(${translateX}px)`,
            filter: `blur(${blur}px)`,
          }}
        >
          <Img
            src={staticFile("ILLUSTRATION/Capcat-Cat-Color.svg")}
            style={{ width: 380, height: 380 }}
          />
        </div>
      </IllustrationZone>
      <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
        <Typewriter text={TEXT} />
      </TextZone>
    </BeatWrapper>
  );
};
