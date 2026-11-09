// Reel "happy-diwali": "Happy Diwali to every engineer still pushing code in dark mode"
import React from "react";
import { brand as myBrand } from "../../brand";
import { Avatar } from "../../avatars/Avatar";
import { useMouth } from "../../avatars/useMouth";
import type { PoseCue } from "../../avatars/SpritePlayer";
import { Card, EndCard, Karaoke, Line, ReelFrame, SceneBlock, Sticker, Title, type ReelProps } from "../../components";
import { AVATAR_BOX, CAPTION_BOTTOM, SAFE, SAFE_BOX } from "../../layout";
import { timing } from "../../timing";
import mouth from "../../../public/reels/happy-diwali/mouth.json";
import words from "../../../public/reels/happy-diwali/captions.words.json";

export const t = timing(words);
export const AUDIO = "reels/happy-diwali/vo.wav";
export const durationInFrames = t.duration();

// Scene cuts on unique spoken words (aim for 4-8s per scene):
const S = {
  hook: [0, t.atText("inference", 3.98)],
  blessing1: [t.atText("inference", 3.98), t.atText("firecrackers", 11.46)],
  swarms: [t.atText("firecrackers", 11.46), t.atText("Lakshmi", 20.1)],
  blessing2: [t.atText("Lakshmi", 20.1), t.atText("Signhify", 27.54)],
  wishes: [t.atText("Signhify", 27.54), t.atText("Comment", 30.18)],
  end: [t.atText("Comment", 30.18), t.duration()],
} as const;

const poseCues: PoseCue[] = [
  { at: 0, pose: "thumbs-up" },
  { at: 3.8, pose: "point-right" },
  { at: 11.2, pose: "explain" },
  { at: 20.0, pose: "present" },
  { at: 27.0, pose: "ok" },
  { at: 30.2, pose: "point-down" },
];

export const Reel: React.FC<ReelProps> = ({ brand = myBrand, avatar = "flat", debugSafeZones, probe }) => {
  const m = useMouth(mouth, words);
  return (
    <ReelFrame brand={brand} audio={AUDIO} debugSafeZones={debugSafeZones} probe={probe}>
      {/* Scene 1: Hook - Happy Diwali in Dark Mode */}
      <SceneBlock name="hook" from={S.hook[0]} to={S.hook[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: SAFE.top + 30, width: SAFE_BOX.width }}>
          <Title text="Happy Diwali Devs 🪔" highlight="Diwali" at={t.at(0)} size={92} />
        </div>
        <Sticker text="Dark Mode Only ⚡" at={t.atText("engineer", 1.14)} rotate={-6} style={{ position: "absolute", left: 450, top: 580 }} />
        <Sticker text="Production Deploy 🚀" at={t.atText("code", 2.18)} rotate={6} style={{ position: "absolute", left: 430, top: 710 }} />
      </SceneBlock>

      {/* Scene 2: High-Yield Specs Blessing */}
      <SceneBlock name="blessing1" from={S.blessing1[0]} to={S.blessing1[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 300, width: SAFE_BOX.width }}>
          <Card at={S.blessing1[0]}>
            <Title text="High-Yield Specs 🪔" highlight="Specs" at={S.blessing1[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={S.blessing1[0]}>⚡ &nbsp;Latency: under 40ms</Line>
            <Line at={t.atText("GPUs", 6.72)}>🎮 &nbsp;GPU VRAM: Zero OOM errors</Line>
            <Line at={t.atText("token", 8.92)}>💸 &nbsp;Token Bills: $0 on Local ONNX</Line>
          </Card>
        </div>
        <Sticker text="Zero OOM 🛡️" at={t.atText("memory", 8.0)} rotate={-5} style={{ position: "absolute", left: 460, top: 760 }} />
      </SceneBlock>

      {/* Scene 3: Multi-Agent Swarms & 60fps Code */}
      <SceneBlock name="swarms" from={S.swarms[0]} to={S.swarms[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.swarms[0]}>
            <Title text="Autonomous Factory" highlight="Factory" at={S.swarms[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={S.swarms[0]}>🤖 &nbsp;Multi-agent swarms active</Line>
            <Line at={t.atText("compiling", 16.18)}>🎬 &nbsp;60fps video-as-code</Line>
            <Line at={t.atText("terminal", 18.56)}>💻 &nbsp;Terminal-driven publishing</Line>
          </Card>
        </div>
        <Sticker text="60 FPS Code 🔥" at={t.atText("video", 18.0)} rotate={5} style={{ position: "absolute", left: 450, top: 750 }} />
      </SceneBlock>

      {/* Scene 4: Goddess Lakshmi Dev Blessing */}
      <SceneBlock name="blessing2" from={S.blessing2[0]} to={S.blessing2[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.blessing2[0]}>
            <Title text="Lakshmi Blessings 🪔" highlight="Lakshmi" at={S.blessing2[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={S.blessing2[0]}>🌿 &nbsp;0 merge conflicts in Git</Line>
            <Line at={t.atText("hundred", 23.22)}>🧪 &nbsp;100% test suite passing</Line>
            <Line at={t.atText("automated", 25.66)}>📈 &nbsp;Autonomous passive revenue</Line>
          </Card>
        </div>
        <Sticker text="100% Passing ✅" at={t.atText("passes", 24.66)} rotate={-6} style={{ position: "absolute", left: 450, top: 760 }} />
      </SceneBlock>

      {/* Scene 5: Festive Wishes from Signhify Studio */}
      <SceneBlock name="wishes" from={S.wishes[0]} to={S.wishes[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 310, width: SAFE_BOX.width }}>
          <Card at={S.wishes[0]}>
            <Title text="Electric Diwali 🪔" highlight="Electric" at={S.wishes[0]} size={76} />
            <div style={{ height: 20 }} />
            <Line first at={S.wishes[0]}>✨ &nbsp;From Signhify Studio</Line>
            <Line at={t.atText("electric", 29.22)}>⚡ &nbsp;High-yield autonomous code</Line>
          </Card>
        </div>
        <Sticker text="Happy Diwali! 🪔" at={t.atText("Diwali", 29.56)} rotate={-5} style={{ position: "absolute", left: 440, top: 760 }} />
      </SceneBlock>

      {/* Scene 6: End Card / CTA */}
      <SceneBlock name="end" from={S.end[0]} to={S.end[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <EndCard keyword="DIWALI" lead="Get The Open-Source Vault" sub="Comment DIWALI to unlock the free repo vault" at={S.end[0]} />
        </div>
      </SceneBlock>

      {/* Mascot Avatar + Captions */}
      {avatar !== "none" ? (
        <div style={{ position: "absolute", left: AVATAR_BOX.x, top: AVATAR_BOX.y }}>
          <Avatar style={avatar} mouth={m} cues={poseCues} size={AVATAR_BOX.size} />
        </div>
      ) : null}
      <div style={{ position: "absolute", left: SAFE_BOX.x, width: SAFE_BOX.width, bottom: CAPTION_BOTTOM }}>
        <Karaoke words={words} perChunk={4} keywords={["Diwali", "latency", "GPUs", "swarms", "Lakshmi", "DIWALI"]} />
      </div>
    </ReelFrame>
  );
};
