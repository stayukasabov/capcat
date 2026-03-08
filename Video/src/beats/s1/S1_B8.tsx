import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { BeatWrapper } from "../../components/BeatWrapper";
import { IllustrationZone } from "../../components/IllustrationZone";
import { TextZone, getFontSize } from "../../components/TextZone";
import { BrowserChrome } from "../../components/BrowserChrome";
import { Typewriter } from "../../components/Typewriter";

const TEXT = "Clip with Obsidian";

export const S1_B8: React.FC<{ fontFamily: string }> = ({ fontFamily }) => {
  const frame = useCurrentFrame();

  // Browser background crossfades from paper to Obsidian purple
  const hue = interpolate(frame, [0, 20], [38, 265], { extrapolateRight: "clamp" });
  const sat = interpolate(frame, [0, 20], [85, 76], { extrapolateRight: "clamp" });
  const lig = interpolate(frame, [0, 20], [93, 55], { extrapolateRight: "clamp" });
  const bgColor = `hsl(${hue}, ${sat}%, ${lig}%)`;

  const logoOpacity = interpolate(frame, [5, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <BeatWrapper>
      <IllustrationZone>
        <div style={{ position: "relative" }}>
          <BrowserChrome content="website" backgroundColorHex={bgColor} />
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              opacity: logoOpacity,
            }}
          >
            <Img
              src={staticFile("ILLUSTRATION/2023_Obsidian_logo.svg")}
              style={{ width: 140, height: 140 }}
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
