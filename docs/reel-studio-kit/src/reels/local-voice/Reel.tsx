// Reel "local-voice": "The $0 Local Voice Clone (Unlimited Studio Voices On Device)"
import React from "react";
import { brand as myBrand } from "../../brand";
import { Avatar } from "../../avatars/Avatar";
import { useMouth } from "../../avatars/useMouth";
import type { PoseCue } from "../../avatars/SpritePlayer";
import { BigNumber, Card, EndCard, Karaoke, Line, ReelFrame, SceneBlock, Sticker, Title, type ReelProps } from "../../components";
import { AVATAR_BOX, CAPTION_BOTTOM, SAFE, SAFE_BOX } from "../../layout";
import { timing } from "../../timing";
import mouth from "../../../public/reels/local-voice/mouth.json";
import words from "../../../public/reels/local-voice/captions.words.json";

export const t = timing(words);
export const AUDIO = "reels/local-voice/vo.wav";
export const durationInFrames = t.duration();

// Scene cuts on spoken words:
const S = {
  hook: [0, t.atText("A", 5.26)],
  repo: [t.atText("A", 5.26), t.atText("called", 12.22)],
  engine: [t.atText("called", 12.22), t.atText("can", 21.54)],
  speed: [t.atText("can", 21.54), t.atText("Comment", 26.14)],
  end: [t.atText("Comment", 26.14), t.duration()],
} as const;

const poseCues: PoseCue[] = [
  { at: 0, pose: "thinking" },
  { at: 2.5, pose: "explain" },
  { at: 5.3, pose: "point-right" },
  { at: 10.0, pose: "thumbs-up" },
  { at: 12.3, pose: "present" },
  { at: 17.5, pose: "ok" },
  { at: 21.6, pose: "point-right" },
  { at: 26.1, pose: "point-down" },
];

export const Reel: React.FC<ReelProps> = ({ brand = myBrand, avatar = "flat", debugSafeZones, probe }) => {
  const m = useMouth(mouth, words);
  return (
    <ReelFrame brand={brand} audio={AUDIO} debugSafeZones={debugSafeZones} probe={probe}>
      {/* Scene 1: Hook - Subscriptions Cancelled */}
      <SceneBlock name="hook" from={S.hook[0]} to={S.hook[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: SAFE.top + 30, width: SAFE_BOX.width }}>
          <Title text="Stop Paying For AI Voices In 2026..." highlight="Stop Paying" at={t.at(0)} size={92} />
        </div>
        <Sticker text="$30/Mo Cancelled" at={t.atText("subscriptions", 0.86)} rotate={-6} style={{ position: "absolute", left: 540, top: 580 }} />
        <Sticker text="Zero API Bills" at={t.atText("clones", 2.38)} rotate={6} style={{ position: "absolute", left: 520, top: 710 }} />
      </SceneBlock>

      {/* Scene 2: The Repository - VoiceStudio */}
      <SceneBlock name="repo" from={S.repo[0]} to={S.repo[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.repo[0]}>
            <Title text="1 Open-Source Repository" highlight="Repository" at={S.repo[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("unlimited", 7.0)}>1 &nbsp;Unlimited studio voice clones</Line>
            <Line at={t.atText("local", 10.5)}>2 &nbsp;100% on your local machine</Line>
          </Card>
        </div>
        <Sticker text="VoiceStudio" at={t.atText("VoiceStudio", 12.3)} rotate={-5} style={{ position: "absolute", left: 560, top: 730 }} />
      </SceneBlock>

      {/* Scene 3: The Engine - Claude Integration */}
      <SceneBlock name="engine" from={S.engine[0]} to={S.engine[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.engine[0]}>
            <Title text="Zero Token Bills" highlight="Zero" at={S.engine[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={S.engine[0]}>1 &nbsp;No monthly character limits</Line>
            <Line at={t.atText("Claude", 17.5)}>2 &nbsp;Plugs directly into Claude Code</Line>
          </Card>
        </div>
        <Sticker text="Claude Code" at={t.atText("scripts", 19.5)} rotate={6} style={{ position: "absolute", left: 570, top: 760 }} />
      </SceneBlock>

      {/* Scene 4: Performance - Kokoro vs Neural */}
      <SceneBlock name="speed" from={S.speed[0]} to={S.speed[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.speed[0]}>
            <Title text="Real-Time CPU Speed" highlight="Real-Time" at={S.speed[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={t.atText("Kokoro", 22.0)}>1 &nbsp;Kokoro-82M on laptop CPU</Line>
            <Line at={t.atText("neural", 24.0)}>2 &nbsp;Neural clone for studio master</Line>
          </Card>
        </div>
        <Sticker text="Kokoro ONNX" at={t.atText("quality", 25.0)} rotate={-5} style={{ position: "absolute", left: 550, top: 750 }} />
      </SceneBlock>

      {/* Scene 5: End Card / CTA */}
      <SceneBlock name="end" from={S.end[0]} to={S.end[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <EndCard keyword="VOICE" lead="Get VoiceStudio local setup" sub="Comment VOICE & I'll DM the install command" at={S.end[0]} />
        </div>
      </SceneBlock>

      {/* Mascot Avatar + Captions */}
      {avatar !== "none" ? (
        <div style={{ position: "absolute", left: AVATAR_BOX.x, top: AVATAR_BOX.y }}>
          <Avatar style={avatar} mouth={m} cues={poseCues} size={AVATAR_BOX.size} />
        </div>
      ) : null}
      <div style={{ position: "absolute", left: SAFE_BOX.x, width: SAFE_BOX.width, bottom: CAPTION_BOTTOM }}>
        <Karaoke words={words} perChunk={4} keywords={["subscriptions", "VoiceStudio", "bills", "Claude", "Kokoro", "VOICE"]} />
      </div>
    </ReelFrame>
  );
};
