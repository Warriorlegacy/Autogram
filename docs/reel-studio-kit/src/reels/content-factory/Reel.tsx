// Reel "content-factory": "Stop paying 200 dollars a month for AI video tools"
import React from "react";
import { brand as myBrand } from "../../brand";
import { Avatar } from "../../avatars/Avatar";
import { useMouth } from "../../avatars/useMouth";
import type { PoseCue } from "../../avatars/SpritePlayer";
import { BigNumber, Card, EndCard, Karaoke, Line, ReelFrame, SceneBlock, Sticker, Title, type ReelProps } from "../../components";
import { AVATAR_BOX, CAPTION_BOTTOM, SAFE, SAFE_BOX } from "../../layout";
import { timing } from "../../timing";
import mouth from "../../../public/reels/content-factory/mouth.json";
import words from "../../../public/reels/content-factory/captions.words.json";

export const t = timing(words);
export const AUDIO = "reels/content-factory/vo.wav";
export const durationInFrames = t.duration();

// Scene cuts on spoken words:
const S = {
  hook: [0, t.atText("We", 2.6)],
  factory: [t.atText("We", 2.6), t.atText("Local", 5.8)],
  research: [t.atText("Local", 5.8), t.atText("Code", 10.04)],
  code: [t.atText("Code", 10.04), t.atText("Comment", 12.98)],
  end: [t.atText("Comment", 12.98), t.duration()],
} as const;

const poseCues: PoseCue[] = [
  { at: 0, pose: "idle" },
  { at: 1.5, pose: "explain" },
  { at: 3.4, pose: "point-right" },
  { at: 5.5, pose: "thumbs-up" },
  { at: 7.9, pose: "thinking" },
  { at: 11.0, pose: "present" },
  { at: 13.8, pose: "ok" },
  { at: 18.1, pose: "point-down" },
];

export const Reel: React.FC<ReelProps> = ({ brand = myBrand, avatar = "flat", debugSafeZones, probe }) => {
  const m = useMouth(mouth, words);
  return (
    <ReelFrame brand={brand} audio={AUDIO} debugSafeZones={debugSafeZones} probe={probe}>
      {/* Scene 1: Hook */}
      <SceneBlock name="hook" from={S.hook[0]} to={S.hook[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: SAFE.top + 30, width: SAFE_BOX.width }}>
          <Title text="Stop Paying $200 For AI Video Tools" highlight="$200" at={t.at(0)} size={106} />
        </div>
        <Sticker text="save your cash" at={t.atText("tools", 1.8)} rotate={6} style={{ position: "absolute", left: 560, top: 620 }} />
      </SceneBlock>

      {/* Scene 2: 12 Repos Factory */}
      <SceneBlock name="factory" from={S.factory[0]} to={S.factory[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.factory[0]}>
            <BigNumber to={12} at={S.factory[0] + 3} label="GitHub Repos" size={180} tracked={false} />
            <div style={{ height: 28 }} />
            <Line first at={t.atText("open", 4.2)}>1 &nbsp;Open-source factory</Line>
            <Line at={t.atText("GitHub", 4.6)}>2 &nbsp;Runs 100% locally</Line>
          </Card>
        </div>
        <Sticker text="$0 monthly" at={t.atText("using", 3.7)} rotate={-6} style={{ position: "absolute", left: 600, top: 730 }} />
      </SceneBlock>

      {/* Scene 3: Research + Voice */}
      <SceneBlock name="research" from={S.research[0]} to={S.research[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.research[0]}>
            <Title text="Research + Voice" highlight="Voice" at={S.research[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("research", 6.1)}>1 &nbsp;Deep research finds viral hooks</Line>
            <Line at={t.atText("voice", 8.0)}>2 &nbsp;VoiceStudio clones audio</Line>
            <Line at={t.atText("free", 9.3)}>3 &nbsp;Zero API subscriptions</Line>
          </Card>
        </div>
        <Sticker text="Viral AI Voice" at={t.atText("cloning", 8.2)} rotate={5} style={{ position: "absolute", left: 570, top: 730 }} />
      </SceneBlock>

      {/* Scene 4: Code Animation */}
      <SceneBlock name="code" from={S.code[0]} to={S.code[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 300, width: SAFE_BOX.width }}>
          <Card at={S.code[0]}>
            <BigNumber to={0} suffix=" limits" at={S.code[0] + 2} label={<>pure code<br />rendering</>} tracked={false} size={180} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("animations", 10.3)}>1 &nbsp;Remotion + HyperFrames</Line>
            <Line at={t.atText("seconds", 11.3)}>2 &nbsp;Exported in seconds</Line>
          </Card>
        </div>
        <Sticker text="no cloud needed" at={t.atText("zero", 11.7)} rotate={-7} style={{ position: "absolute", left: 520, top: 740 }} />
      </SceneBlock>

      {/* Scene 5: End Card / CTA */}
      <SceneBlock name="end" from={S.end[0]} to={S.end[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <EndCard keyword="FACTORY" lead="Get all 12 repos" sub="Comment FACTORY & I'll DM the architecture" at={S.end[0]} />
        </div>
      </SceneBlock>

      {/* Always on: talking character + captions */}
      {avatar !== "none" ? (
        <div style={{ position: "absolute", left: AVATAR_BOX.x, top: AVATAR_BOX.y }}>
          <Avatar style={avatar} mouth={m} cues={poseCues} size={AVATAR_BOX.size} />
        </div>
      ) : null}
      <div style={{ position: "absolute", left: SAFE_BOX.x, width: SAFE_BOX.width, bottom: CAPTION_BOTTOM }}>
        <Karaoke words={words} perChunk={4} keywords={["FACTORY", "200", "12", "GitHub", "free", "zero"]} />
      </div>
    </ReelFrame>
  );
};
