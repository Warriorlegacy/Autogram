// Reel "claude-vs-premiere": "Claude > Premiere Pro?"
import React from "react";
import { brand as myBrand } from "../../brand";
import { Avatar } from "../../avatars/Avatar";
import { useMouth } from "../../avatars/useMouth";
import type { PoseCue } from "../../avatars/SpritePlayer";
import { BigNumber, Card, EndCard, Karaoke, Line, ReelFrame, SceneBlock, Sticker, Title, type ReelProps } from "../../components";
import { AVATAR_BOX, CAPTION_BOTTOM, SAFE, SAFE_BOX } from "../../layout";
import { timing } from "../../timing";
import mouth from "../../../public/reels/claude-vs-premiere/mouth.json";
import words from "../../../public/reels/claude-vs-premiere/captions.words.json";

export const t = timing(words);
export const AUDIO = "reels/claude-vs-premiere/vo.wav";
export const durationInFrames = t.duration();

// Scene cuts on spoken words:
const S = {
  hook: [0, t.atText("What", 4.34)],
  reveal: [t.atText("What", 4.34), t.atText("Using", 12.1)],
  hyperframes: [t.atText("Using", 12.1), t.atText("Zero", 21.8)],
  comparison: [t.atText("Zero", 21.8), t.atText("Comment", 25.56)],
  end: [t.atText("Comment", 25.56), t.duration()],
} as const;

const poseCues: PoseCue[] = [
  { at: 0, pose: "thinking" },
  { at: 2.2, pose: "explain" },
  { at: 4.34, pose: "point-right" },
  { at: 7.0, pose: "thumbs-up" },
  { at: 12.1, pose: "present" },
  { at: 17.3, pose: "ok" },
  { at: 21.8, pose: "point-right" },
  { at: 25.56, pose: "point-down" },
];

export const Reel: React.FC<ReelProps> = ({ brand = myBrand, avatar = "flat", debugSafeZones, probe }) => {
  const m = useMouth(mouth, words);
  return (
    <ReelFrame brand={brand} audio={AUDIO} debugSafeZones={debugSafeZones} probe={probe}>
      {/* Scene 1: Hook - $35/mo Video Editing vs Code */}
      <SceneBlock name="hook" from={S.hook[0]} to={S.hook[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: SAFE.top + 30, width: SAFE_BOX.width }}>
          <Title text="Why Pay $35/Mo For Video Editing?" highlight="Editing" at={t.at(0)} size={100} />
        </div>
        <Sticker text="$35/Month" at={t.atText("thirtyfive", 2.12)} rotate={-6} style={{ position: "absolute", left: 560, top: 580 }} />
        <Sticker text="RIP Keyframes" at={t.atText("keyframes", 3.28)} rotate={7} style={{ position: "absolute", left: 540, top: 710 }} />
      </SceneBlock>

      {/* Scene 2: The Reveal - 0% Premiere, 100% Claude */}
      <SceneBlock name="reveal" from={S.reveal[0]} to={S.reveal[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.reveal[0]}>
            <Title text="Not Edited In Premiere" highlight="Premiere" at={S.reveal[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("Premiere", 6.22)}>1 &nbsp;Zero timeline scrubbing</Line>
            <Line at={t.atText("drawn", 10.38)}>2 &nbsp;Drawn frame-by-frame in code</Line>
          </Card>
        </div>
        <Sticker text="No Timeline" at={t.atText("Effects", 6.98)} rotate={-6} style={{ position: "absolute", left: 590, top: 730 }} />
        <Sticker text="Claude 3.5 Sonnet" at={t.atText("Claude", 11.26)} rotate={5} style={{ position: "absolute", left: 520, top: 820 }} />
      </SceneBlock>

      {/* Scene 3: The Engine - HyperFrames 45s Render */}
      <SceneBlock name="hyperframes" from={S.hyperframes[0]} to={S.hyperframes[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 300, width: SAFE_BOX.width }}>
          <Card at={S.hyperframes[0]}>
            <BigNumber to={45} suffix="s" at={S.hyperframes[0] + 2} label={<>code to<br />vertical MP4</>} tracked={false} size={160} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("HTML", 14.78)}>1 &nbsp;HTML & GSAP web animation</Line>
            <Line at={t.atText("compiles", 17.34)}>2 &nbsp;Automatic voice & subtitles</Line>
          </Card>
        </div>
        <Sticker text="Open Source" at={t.atText("opensource", 12.48)} rotate={-5} style={{ position: "absolute", left: 560, top: 760 }} />
      </SceneBlock>

      {/* Scene 4: Speed / Comparison */}
      <SceneBlock name="comparison" from={S.comparison[0]} to={S.comparison[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.comparison[0]}>
            <Title text="The New Video Stack" highlight="Stack" at={S.comparison[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("timeline", 22.16)}>0s &nbsp;Timeline scrubbing</Line>
            <Line at={t.atText("rendering", 23.68)}>0s &nbsp;Rendering lag</Line>
            <Line at={t.atText("pure", 24.9)}>100% &nbsp;Pure reproducible code</Line>
          </Card>
        </div>
        <Sticker text="Pure Code" at={t.atText("code", 25.16)} rotate={6} style={{ position: "absolute", left: 570, top: 760 }} />
      </SceneBlock>

      {/* Scene 5: End Card / CTA */}
      <SceneBlock name="end" from={S.end[0]} to={S.end[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <EndCard keyword="HYPER" lead="Get the code-to-video stack" sub="Comment HYPER & I'll DM the repository" at={S.end[0]} />
        </div>
      </SceneBlock>

      {/* Mascot Avatar + Captions */}
      {avatar !== "none" ? (
        <div style={{ position: "absolute", left: AVATAR_BOX.x, top: AVATAR_BOX.y }}>
          <Avatar style={avatar} mouth={m} cues={poseCues} size={AVATAR_BOX.size} />
        </div>
      ) : null}
      <div style={{ position: "absolute", left: SAFE_BOX.x, width: SAFE_BOX.width, bottom: CAPTION_BOTTOM }}>
        <Karaoke words={words} perChunk={4} keywords={["paying", "dollars", "Premiere", "Claude", "HyperFrames", "fortyfive", "HYPER"]} />
      </div>
    </ReelFrame>
  );
};
