import React from "react";
import { Composition } from "remotion";
import { CapcatAd } from "./compositions/CapcatAd";
import { TOTAL_DURATION_FRAMES } from "./beatTimings";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="CapcatAd"
      component={CapcatAd}
      durationInFrames={TOTAL_DURATION_FRAMES}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
