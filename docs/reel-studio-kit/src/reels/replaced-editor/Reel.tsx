// Reel "replaced-editor": "I Replaced A $5,000/Mo Video Editor With 1 Open-Source Script"
import React from "react";
import { brand as myBrand } from "../../brand";
import { Avatar } from "../../avatars/Avatar";
import { useMouth } from "../../avatars/useMouth";
import type { PoseCue } from "../../avatars/SpritePlayer";
import { BigNumber, Card, EndCard, Karaoke, Line, ReelFrame, SceneBlock, Sticker, Title, type ReelProps } from "../../components";
import { AVATAR_BOX, CAPTION_BOTTOM, SAFE, SAFE_BOX } from "../../layout";
import { timing } from "../../timing";
import mouth from "../../../public/reels/replaced-editor/mouth.json";
import words from "../../../public/reels/replaced-editor/captions.words.json";

export const t = timing(words);
export const AUDIO = "reels/replaced-editor/vo.wav";
export const durationInFrames = t.duration();

// Scene cuts on spoken words:
const S = {
  hook: [0, t.atText("Instead", 7.5)],
  solution: [t.atText("Instead", 7.5), t.atText("You", 12.2)],
  engine: [t.atText("You", 12.2), t.atText("Zero", 21.96)],
  punchline: [t.atText("Zero", 21.96), t.atText("Comment", 24.8)],
  end: [t.atText("Comment", 24.8), t.duration()],
} as const;

const poseCues: PoseCue[] = [
  { at: 0, pose: "thinking" },
  { at: 3.4, pose: "explain" },
  { at: 7.5, pose: "point-right" },
  { at: 10.1, pose: "thumbs-up" },
  { at: 12.3, pose: "present" },
  { at: 17.5, pose: "ok" },
  { at: 22.0, pose: "point-right" },
  { at: 24.8, pose: "point-down" },
];

export const Reel: React.FC<ReelProps> = ({ brand = myBrand, avatar = "flat", debugSafeZones, probe }) => {
  const m = useMouth(mouth, words);
  return (
    <ReelFrame brand={brand} audio={AUDIO} debugSafeZones={debugSafeZones} probe={probe}>
      {/* Scene 1: Hook - $5,000/mo Video Editor Invoice */}
      <SceneBlock name="hook" from={S.hook[0]} to={S.hook[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: SAFE.top + 30, width: SAFE_BOX.width }}>
          <Title text="An Editor Quoted $5,000/Month..." highlight="$5,000" at={t.at(0)} size={96} />
        </div>
        <Sticker text="$5,000 / Mo" at={t.atText("thousand", 3.69)} rotate={-6} style={{ position: "absolute", left: 560, top: 580 }} />
        <Sticker text="Agency Invoice" at={t.atText("podcasts", 5.5)} rotate={6} style={{ position: "absolute", left: 530, top: 710 }} />
      </SceneBlock>

      {/* Scene 2: The Solution - OpenMontage Script */}
      <SceneBlock name="solution" from={S.solution[0]} to={S.solution[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.solution[0]}>
            <Title text="1 Open-Source Script" highlight="Script" at={S.solution[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("Python", 8.8)}>1 &nbsp;Zero freelance invoices</Line>
            <Line at={t.atText("OpenMontage", 10.4)}>2 &nbsp;calesthio/OpenMontage</Line>
          </Card>
        </div>
        <Sticker text="OpenMontage" at={t.atText("script", 9.2)} rotate={-5} style={{ position: "absolute", left: 560, top: 730 }} />
      </SceneBlock>

      {/* Scene 3: The 60-Second Machine */}
      <SceneBlock name="engine" from={S.engine[0]} to={S.engine[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 300, width: SAFE_BOX.width }}>
          <Card at={S.engine[0]}>
            <BigNumber to={60} suffix="s" at={S.engine[0] + 2} label={<>1-hour video to<br />viral vertical cuts</>} tracked={false} size={160} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("cuts", 14.48)}>1 &nbsp;Auto dead-air & silence removal</Line>
            <Line at={t.atText("face", 17.46)}>2 &nbsp;Active speaker face tracking</Line>
          </Card>
        </div>
        <Sticker text="Auto Cut" at={t.atText("sixty", 20.92)} rotate={6} style={{ position: "absolute", left: 580, top: 760 }} />
      </SceneBlock>

      {/* Scene 4: Punchline - Zero Human Editing */}
      <SceneBlock name="punchline" from={S.punchline[0]} to={S.punchline[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.punchline[0]}>
            <Title text="Zero Human Editing" highlight="Zero" at={S.punchline[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("human", 22.26)}>1 &nbsp;100% reproducible code</Line>
            <Line at={t.atText("opensource", 23.5)}>2 &nbsp;Runs locally or on cloud</Line>
          </Card>
        </div>
        <Sticker text="100% Code" at={t.atText("code", 24.0)} rotate={-5} style={{ position: "absolute", left: 560, top: 750 }} />
      </SceneBlock>

      {/* Scene 5: End Card / CTA */}
      <SceneBlock name="end" from={S.end[0]} to={S.end[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <EndCard keyword="CUT" lead="Get the OpenMontage stack" sub="Comment CUT & I'll DM the repository" at={S.end[0]} />
        </div>
      </SceneBlock>

      {/* Mascot Avatar + Captions */}
      {avatar !== "none" ? (
        <div style={{ position: "absolute", left: AVATAR_BOX.x, top: AVATAR_BOX.y }}>
          <Avatar style={avatar} mouth={m} cues={poseCues} size={AVATAR_BOX.size} />
        </div>
      ) : null}
      <div style={{ position: "absolute", left: SAFE_BOX.x, width: SAFE_BOX.width, bottom: CAPTION_BOTTOM }}>
        <Karaoke words={words} perChunk={4} keywords={["five", "thousand", "dollars", "OpenMontage", "sixty", "CUT"]} />
      </div>
    </ReelFrame>
  );
};
