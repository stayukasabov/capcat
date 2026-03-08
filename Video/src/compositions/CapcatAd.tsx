import React from "react";
import { AbsoluteFill, Audio, Series, staticFile, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/SourceSerif4";
import { beatTimings } from "../beatTimings";
import { colors } from "../tokens";

// Scene 1
import { S1_B1 } from "../beats/s1/S1_B1";
// Scene 2
import { S2_B1 } from "../beats/s2/S2_B1";
import { S2_B2 } from "../beats/s2/S2_B2";
import { S2_B3 } from "../beats/s2/S2_B3";
import { S2_B4 } from "../beats/s2/S2_B4";
// Scene 3
import { S3_B1 } from "../beats/s3/S3_B1";
import { S3_B2 } from "../beats/s3/S3_B2";
import { S1_B2 } from "../beats/s1/S1_B2";
import { S1_B3 } from "../beats/s1/S1_B3";
import { S1_B4 } from "../beats/s1/S1_B4";
import { S1_B5 } from "../beats/s1/S1_B5";
import { S1_B6 } from "../beats/s1/S1_B6";
import { S1_B7 } from "../beats/s1/S1_B7";
import { S1_B8 } from "../beats/s1/S1_B8";

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
        <Series.Sequence durationInFrames={dur("s1_b2")} premountFor={fps}>
          <S1_B2 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s1_b3")} premountFor={fps}>
          <S1_B3 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s1_b4")} premountFor={fps}>
          <S1_B4 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s1_b5")} premountFor={fps}>
          <S1_B5 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s1_b6")} premountFor={fps}>
          <S1_B6 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s1_b7")} premountFor={fps}>
          <S1_B7 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s1_b8")} premountFor={fps}>
          <S1_B8 fontFamily={fontFamily} />
        </Series.Sequence>
        {/* Scene 2 */}
        <Series.Sequence durationInFrames={dur("s2_b1")} premountFor={fps}>
          <S2_B1 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s2_b2")} premountFor={fps}>
          <S2_B2 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s2_b3")} premountFor={fps}>
          <S2_B3 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s2_b4")} premountFor={fps}>
          <S2_B4 fontFamily={fontFamily} />
        </Series.Sequence>
        {/* Scene 3 */}
        <Series.Sequence durationInFrames={dur("s3_b1")} premountFor={fps}>
          <S3_B1 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s3_b2")} premountFor={fps}>
          <S3_B2 fontFamily={fontFamily} />
        </Series.Sequence>
        {/* Scene 4+ beats added as tasks complete */}
      </Series>
    </AbsoluteFill>
  );
};
