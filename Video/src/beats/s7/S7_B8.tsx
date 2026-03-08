import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { TextZone, getFontSize } from "../../components/TextZone";
import { Typewriter } from "../../components/Typewriter";
import { colors } from "../../tokens";

const TEXT = "A minimum viable product";

// Final beat — logo stays, entire screen fades to dark #1a1212
export const S7_B8: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Background fades from paper to dark over 60 frames at end
  const darkFade = interpolate(
    frame,
    [durationInFrames - 60, durationInFrames],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const bgColor = `rgb(
    ${Math.round(250 - (250 - 26) * darkFade)},
    ${Math.round(245 - (245 - 18) * darkFade)},
    ${Math.round(238 - (238 - 18) * darkFade)}
  )`;

  // Logo fades in then stays
  const logoOpacity = interpolate(frame, [0, 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Text fades out as screen goes dark
  const textOpacity = interpolate(
    frame,
    [durationInFrames - 40, durationInFrames - 10],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: bgColor }}>
      {/* Logo centered in illustration zone */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 648,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: logoOpacity,
        }}
      >
        <Img
          src={staticFile("ILLUSTRATION/Capcat-Logo.svg")}
          style={{ width: 300, height: 300 }}
        />
      </div>
      {/* Text zone */}
      <div style={{ opacity: textOpacity }}>
        <TextZone fontFamily={fontFamily} fontSize={getFontSize(TEXT)}>
          <Typewriter text={TEXT} />
        </TextZone>
      </div>
    </AbsoluteFill>
  );
};
