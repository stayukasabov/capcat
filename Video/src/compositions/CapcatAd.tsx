import React from "react";
import { AbsoluteFill, Audio, Series, staticFile, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/SourceSerif4";
import { beatTimings } from "../beatTimings";
import { colors } from "../tokens";

// Scene 1
import { S1_B1 } from "../beats/s1/S1_B1";

const { fontFamily } = loadFont("normal", { weights: ["400", "700"], subsets: ["latin"] });

export const CapcatAd: React.FC = () => {
  const { fps } = useVideoConfig();

  const dur = (id: string) =>
    Math.round((beatTimings.find((b) => b.id === id)?.durationSec ?? 3) * fps);

  return (
    <AbsoluteFill style={{ backgroundColor: colors.paper }}>
      <Audio src={staticFile("AudioVersionFinalNonMastered.mp4")} />
      <Series>
        <Series.Sequence durationInFrames={dur("s1_b1")} premountFor={fps}>
          <S1_B1 fontFamily={fontFamily} />
        </Series.Sequence>
        {/* Beats added as each task completes */}
      </Series>
    </AbsoluteFill>
  );
};
