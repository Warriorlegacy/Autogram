// Reel "deleted-production": "Claude. I deleted production."
import React from "react";
import { brand as myBrand } from "../../brand";
import { Avatar } from "../../avatars/Avatar";
import { useMouth } from "../../avatars/useMouth";
import type { PoseCue } from "../../avatars/SpritePlayer";
import { BigNumber, Card, EndCard, Karaoke, Line, ReelFrame, SceneBlock, Sticker, Title, type ReelProps } from "../../components";
import { AVATAR_BOX, CAPTION_BOTTOM, SAFE, SAFE_BOX } from "../../layout";
import { timing } from "../../timing";
import mouth from "../../../public/reels/deleted-production/mouth.json";
import words from "../../../public/reels/deleted-production/captions.words.json";

export const t = timing(words);
export const AUDIO = "reels/deleted-production/vo.wav";
export const durationInFrames = t.duration();

// Scene cuts on spoken words:
const S = {
  hook: [0, t.atText("The", 2.6)],
  panic: [t.atText("The", 2.6), t.atText("Instead", 9.2)],
  solution: [t.atText("Instead", 9.2), t.atText("It", 12.0)],
  restore: [t.atText("It", 12.0), t.atText("Stop", 17.3)],
  end: [t.atText("Stop", 17.3), t.duration()],
} as const;

const poseCues: PoseCue[] = [
  { at: 0, pose: "thinking" },
  { at: 2.6, pose: "explain" },
  { at: 6.2, pose: "point-right" },
  { at: 9.2, pose: "thumbs-up" },
  { at: 12.1, pose: "present" },
  { at: 17.3, pose: "ok" },
  { at: 19.8, pose: "point-down" },
];

export const Reel: React.FC<ReelProps> = ({ brand = myBrand, avatar = "flat", debugSafeZones, probe }) => {
  const m = useMouth(mouth, words);
  return (
    <ReelFrame brand={brand} audio={AUDIO} debugSafeZones={debugSafeZones} probe={probe}>
      {/* Scene 1: Hook - Dev Panic */}
      <SceneBlock name="hook" from={S.hook[0]} to={S.hook[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: SAFE.top + 30, width: SAFE_BOX.width }}>
          <Title text="Claude... I Deleted Production" highlight="Production" at={t.at(0)} size={104} />
        </div>
        <Sticker text="FATAL ERROR" at={t.atText("database", 1.6)} rotate={6} style={{ position: "absolute", left: 560, top: 620 }} />
      </SceneBlock>

      {/* Scene 2: The Nightmare */}
      <SceneBlock name="panic" from={S.panic[0]} to={S.panic[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.panic[0]}>
            <Title text="The CEO Is Calling" highlight="Calling" at={S.panic[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("phone", 4.3)}>1 &nbsp;Hands shaking on keyboard</Line>
            <Line at={t.atText("branches", 6.7)}>2 &nbsp;Branch: production-DO-NOT-TOUCH</Line>
          </Card>
        </div>
        <Sticker text="RIP Career" at={t.atText("shaking", 5.5)} rotate={-6} style={{ position: "absolute", left: 600, top: 730 }} />
      </SceneBlock>

      {/* Scene 3: The Claude Skill Solution */}
      <SceneBlock name="solution" from={S.solution[0]} to={S.solution[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.solution[0]}>
            <Title text="1 Claude Skill" highlight="Skill" at={S.solution[0]} size={84} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("panicking", 9.5)}>1 &nbsp;Open-source CLI automation</Line>
            <Line at={t.atText("skill", 11.4)}>2 &nbsp;Zero apology emails sent</Line>
          </Card>
        </div>
        <Sticker text="Secret Weapon" at={t.atText("Claude", 11.1)} rotate={5} style={{ position: "absolute", left: 570, top: 730 }} />
      </SceneBlock>

      {/* Scene 4: 40 PRs Diffed in 3 Minutes */}
      <SceneBlock name="restore" from={S.restore[0]} to={S.restore[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 300, width: SAFE_BOX.width }}>
          <Card at={S.restore[0]}>
            <BigNumber to={40} suffix=" PRs" at={S.restore[0] + 2} label={<>schema state<br />restored</>} tracked={false} size={170} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("schema", 14.6)}>1 &nbsp;Diffed 40 merged commits</Line>
            <Line at={t.atText("minutes", 16.7)}>2 &nbsp;Tables back in 3 minutes</Line>
          </Card>
        </div>
        <Sticker text="3 min fix" at={t.atText("restored", 15.4)} rotate={-7} style={{ position: "absolute", left: 540, top: 740 }} />
      </SceneBlock>

      {/* Scene 5: End Card / CTA */}
      <SceneBlock name="end" from={S.end[0]} to={S.end[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <EndCard keyword="RESTORE" lead="Get the terminal script" sub="Comment RESTORE & I'll DM the repository" at={S.end[0]} />
        </div>
      </SceneBlock>

      {/* Mascot Avatar + Captions */}
      {avatar !== "none" ? (
        <div style={{ position: "absolute", left: AVATAR_BOX.x, top: AVATAR_BOX.y }}>
          <Avatar style={avatar} mouth={m} cues={poseCues} size={AVATAR_BOX.size} />
        </div>
      ) : null}

      <div style={{ position: "absolute", left: SAFE_BOX.x, width: SAFE_BOX.width, bottom: CAPTION_BOTTOM }}>
        <Karaoke words={words} perChunk={4} keywords={["database", "production", "CEO", "Claude", "RESTORE"]} />
      </div>
    </ReelFrame>
  );
};
