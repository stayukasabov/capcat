import React from "react";
import { AbsoluteFill, Audio, Series, staticFile, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/SourceSerif4";
import { beatTimings } from "../beatTimings";
import { colors } from "../tokens";

// Scene 1
import { S1_B1 } from "../beats/s1/S1_B1";
// Scene 2
import { S2_B1 } from "../beats/s2/S2_B1";
// Scene 4
import { S4_B1 } from "../beats/s4/S4_B1";
// Scene 5
import { S5_B1 } from "../beats/s5/S5_B1";
// Scene 6
import { S6_B1 } from "../beats/s6/S6_B1";
// Scene 7
import { S7_B1 } from "../beats/s7/S7_B1";
import { S7_B2 } from "../beats/s7/S7_B2";
import { S7_B3 } from "../beats/s7/S7_B3";
import { S7_B4 } from "../beats/s7/S7_B4";
import { S7_B5 } from "../beats/s7/S7_B5";
import { S7_B6 } from "../beats/s7/S7_B6";
import { S7_B7 } from "../beats/s7/S7_B7";
import { S7_B8 } from "../beats/s7/S7_B8";
import { S6_B2 } from "../beats/s6/S6_B2";
import { S6_B3 } from "../beats/s6/S6_B3";
import { S6_B4 } from "../beats/s6/S6_B4";
import { S6_B5 } from "../beats/s6/S6_B5";
import { S5_B2 } from "../beats/s5/S5_B2";
import { S5_B3 } from "../beats/s5/S5_B3";
import { S4_B2 } from "../beats/s4/S4_B2";
import { S4_B3 } from "../beats/s4/S4_B3";
import { S4_B4 } from "../beats/s4/S4_B4";
import { S4_B5 } from "../beats/s4/S4_B5";
import { S4_B6 } from "../beats/s4/S4_B6";
import { S4_B7 } from "../beats/s4/S4_B7";
import { S4_B8 } from "../beats/s4/S4_B8";
import { S4_B9 } from "../beats/s4/S4_B9";
import { S4_B10 } from "../beats/s4/S4_B10";
import { S4_B11 } from "../beats/s4/S4_B11";
import { S4_B12 } from "../beats/s4/S4_B12";
import { S4_B13 } from "../beats/s4/S4_B13";
import { S4_B14 } from "../beats/s4/S4_B14";
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
        {/* Scene 4 */}
        <Series.Sequence durationInFrames={dur("s4_b1")} premountFor={fps}>
          <S4_B1 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b2")} premountFor={fps}>
          <S4_B2 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b3")} premountFor={fps}>
          <S4_B3 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b4")} premountFor={fps}>
          <S4_B4 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b5")} premountFor={fps}>
          <S4_B5 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b6")} premountFor={fps}>
          <S4_B6 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b7")} premountFor={fps}>
          <S4_B7 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b8")} premountFor={fps}>
          <S4_B8 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b9")} premountFor={fps}>
          <S4_B9 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b10")} premountFor={fps}>
          <S4_B10 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b11")} premountFor={fps}>
          <S4_B11 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b12")} premountFor={fps}>
          <S4_B12 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b13")} premountFor={fps}>
          <S4_B13 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s4_b14")} premountFor={fps}>
          <S4_B14 fontFamily={fontFamily} />
        </Series.Sequence>
        {/* Scene 5 */}
        <Series.Sequence durationInFrames={dur("s5_b1")} premountFor={fps}>
          <S5_B1 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s5_b2")} premountFor={fps}>
          <S5_B2 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s5_b3")} premountFor={fps}>
          <S5_B3 fontFamily={fontFamily} />
        </Series.Sequence>
        {/* Scene 6 */}
        <Series.Sequence durationInFrames={dur("s6_b1")} premountFor={fps}>
          <S6_B1 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s6_b2")} premountFor={fps}>
          <S6_B2 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s6_b3")} premountFor={fps}>
          <S6_B3 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s6_b4")} premountFor={fps}>
          <S6_B4 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s6_b5")} premountFor={fps}>
          <S6_B5 fontFamily={fontFamily} />
        </Series.Sequence>
        {/* Scene 7 */}
        <Series.Sequence durationInFrames={dur("s7_b1")} premountFor={fps}>
          <S7_B1 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s7_b2")} premountFor={fps}>
          <S7_B2 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s7_b3")} premountFor={fps}>
          <S7_B3 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s7_b4")} premountFor={fps}>
          <S7_B4 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s7_b5")} premountFor={fps}>
          <S7_B5 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s7_b6")} premountFor={fps}>
          <S7_B6 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s7_b7")} premountFor={fps}>
          <S7_B7 fontFamily={fontFamily} />
        </Series.Sequence>
        <Series.Sequence durationInFrames={dur("s7_b8")} premountFor={fps}>
          <S7_B8 fontFamily={fontFamily} />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
