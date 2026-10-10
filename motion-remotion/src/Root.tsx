import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { LowerThird, lowerThirdSchema } from "./LowerThird";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MyComposition />
      <Composition
        id="LowerThird"
        component={LowerThird}
        schema={lowerThirdSchema}
        defaultProps={{ name: "Alex Rivera", title: "FOUNDER · STUDIO TEST", accent: "#ff5a36" }}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
