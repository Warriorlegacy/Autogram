// Reel "doc-engine": "How We Code 30-Minute AI Documentaries (Zero Human Editing)"
import React from "react";
import { brand as myBrand } from "../../brand";
import { Avatar } from "../../avatars/Avatar";
import { useMouth } from "../../avatars/useMouth";
import type { PoseCue } from "../../avatars/SpritePlayer";
import { BigNumber, Card, EndCard, Karaoke, Line, ReelFrame, SceneBlock, Sticker, Title, type ReelProps } from "../../components";
import { AVATAR_BOX, CAPTION_BOTTOM, SAFE, SAFE_BOX } from "../../layout";
import { timing } from "../../timing";
import mouth from "../../../public/reels/doc-engine/mouth.json";
import words from "../../../public/reels/doc-engine/captions.words.json";

export const t = timing(words);
export const AUDIO = "reels/doc-engine/vo.wav";
export const durationInFrames = t.duration();

// Scene cuts on spoken words:
const S = {
  hook: [0, t.atText("We", 4.14)],
  solution: [t.atText("We", 4.14), t.atText("Step", 9.28)],
  pipeline: [t.atText("Step", 9.28), t.atText("HyperFrames", 17.98)],
  engine: [t.atText("HyperFrames", 17.98), t.atText("Comment", 23.84)],
  end: [t.atText("Comment", 23.84), t.duration()],
} as const;

const poseCues: PoseCue[] = [
  { at: 0, pose: "thinking" },
  { at: 2.2, pose: "explain" },
  { at: 4.2, pose: "point-right" },
  { at: 7.8, pose: "thumbs-up" },
  { at: 9.3, pose: "present" },
  { at: 13.6, pose: "ok" },
  { at: 18.0, pose: "point-right" },
  { at: 23.8, pose: "point-down" },
];

export const Reel: React.FC<ReelProps> = ({ brand = myBrand, avatar = "flat", debugSafeZones, probe }) => {
  const m = useMouth(mouth, words);
  return (
    <ReelFrame brand={brand} audio={AUDIO} debugSafeZones={debugSafeZones} probe={probe}>
      {/* Scene 1: Hook - 2 Weeks Work vs Code */}
      <SceneBlock name="hook" from={S.hook[0]} to={S.hook[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: SAFE.top + 30, width: SAFE_BOX.width }}>
          <Title text="Coding 30-Min Documentaries..." highlight="30-Min" at={t.at(0)} size={92} />
        </div>
        <Sticker text="2 Weeks Editing" at={t.atText("weeks", 0.94)} rotate={-6} style={{ position: "absolute", left: 540, top: 580 }} />
        <Sticker text="Zero Human Editors" at={t.atText("documentary", 3.2)} rotate={6} style={{ position: "absolute", left: 510, top: 710 }} />
      </SceneBlock>

      {/* Scene 2: Solution - 60 Seconds Script */}
      <SceneBlock name="solution" from={S.solution[0]} to={S.solution[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 300, width: SAFE_BOX.width }}>
          <Card at={S.solution[0]}>
            <BigNumber to={60} suffix="s" at={S.solution[0] + 2} label={<>Terminal runtime for<br />30-min long form</>} tracked={false} size={160} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("script", 6.8)}>1 &nbsp;One open-source script</Line>
            <Line at={t.atText("architecture", 8.2)}>2 &nbsp;Autonomous Python engine</Line>
          </Card>
        </div>
        <Sticker text="60s Runtime" at={t.atText("seconds", 4.7)} rotate={-5} style={{ position: "absolute", left: 560, top: 760 }} />
      </SceneBlock>

      {/* Scene 3: Pipeline - Deep Research & Claude Acts */}
      <SceneBlock name="pipeline" from={S.pipeline[0]} to={S.pipeline[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.pipeline[0]}>
            <Title text="3 Autonomous Acts" highlight="3" at={S.pipeline[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("sources", 11.2)}>1 &nbsp;Europe PMC & ArXiv citations</Line>
            <Line at={t.atText("narrative", 15.2)}>2 &nbsp;Claude 3-act story arc</Line>
          </Card>
        </div>
        <Sticker text="Deep Research" at={t.atText("research", 10.1)} rotate={6} style={{ position: "absolute", left: 540, top: 740 }} />
      </SceneBlock>

      {/* Scene 4: Engine - HyperFrames 4K Motion */}
      <SceneBlock name="engine" from={S.engine[0]} to={S.engine[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.engine[0]}>
            <Title text="HyperFrames 4K Core" highlight="HyperFrames" at={S.engine[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("motion", 19.8)}>1 &nbsp;Dynamic maps & motion graphics</Line>
            <Line at={t.atText("audio", 21.8)}>2 &nbsp;Multi-track audio master</Line>
          </Card>
        </div>
        <Sticker text="HyperFrames" at={t.atText("MP4", 23.0)} rotate={-5} style={{ position: "absolute", left: 560, top: 750 }} />
      </SceneBlock>

      {/* Scene 5: End Card / CTA */}
      <SceneBlock name="end" from={S.end[0]} to={S.end[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <EndCard keyword="DOCS" lead="Get the Documentary Engine" sub="Comment DOCS & I'll DM the repository" at={S.end[0]} />
        </div>
      </SceneBlock>

      {/* Mascot Avatar + Captions */}
      {avatar !== "none" ? (
        <div style={{ position: "absolute", left: AVATAR_BOX.x, top: AVATAR_BOX.y }}>
          <Avatar style={avatar} mouth={m} cues={poseCues} size={AVATAR_BOX.size} />
        </div>
      ) : null}
      <div style={{ position: "absolute", left: SAFE_BOX.x, width: SAFE_BOX.width, bottom: CAPTION_BOTTOM }}>
        <Karaoke words={words} perChunk={4} keywords={["weeks", "sixty", "architecture", "ArXiv", "HyperFrames", "DOCS"]} />
      </div>
    </ReelFrame>
  );
};
