import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";

export const lowerThirdSchema = z.object({
  name: z.string(),
  title: z.string(),
  accent: z.string(),
});

type Props = z.infer<typeof lowerThirdSchema>;

// Full-frame 1080x1920 transparent overlay; the card sits inside the 9:16 safe zone
// (x 60–960, y 250–1500) so it can be composited 1:1 without repositioning.
export const LowerThird: React.FC<Props> = ({ name, title, accent }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const enter = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 18 });
  const exit = interpolate(frame, [durationInFrames - 12, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });

  const barScale = interpolate(enter, [0, 1], [0, 1]) * (1 - exit);
  const textY = interpolate(enter, [0, 1], [60, 0]) + exit * 40;
  const textOpacity = Math.min(1, frame / 8) * (1 - exit);
  const titleOpacity = interpolate(frame, [8, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) * (1 - exit);

  return (
    <AbsoluteFill style={{ backgroundColor: "transparent" }}>
      <div style={{ position: "absolute", left: 80, top: 1320, display: "flex", alignItems: "stretch", gap: 24 }}>
        <div style={{ width: 14, borderRadius: 7, background: accent, transform: `scaleY(${barScale})`, transformOrigin: "top" }} />
        <div style={{ overflow: "hidden" }}>
          <div
            style={{
              background: "rgba(10,10,12,0.82)",
              padding: "22px 36px 26px",
              borderRadius: 18,
              transform: `translateY(${textY}px)`,
              opacity: textOpacity,
            }}
          >
            <div style={{ fontFamily: "Segoe UI, sans-serif", fontWeight: 700, fontSize: 64, color: "#f5f5f4", letterSpacing: -1 }}>
              {name}
            </div>
            <div style={{ fontFamily: "Segoe UI, sans-serif", fontWeight: 600, fontSize: 36, color: accent, opacity: titleOpacity, letterSpacing: 2 }}>
              {title}
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
