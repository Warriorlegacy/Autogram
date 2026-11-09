// Reel "diwali-dev-mode": "The Developer's Diwali: How Engineers Light Up The World"
import React from "react";
import { brand as myBrand } from "../../brand";
import { Avatar } from "../../avatars/Avatar";
import { useMouth } from "../../avatars/useMouth";
import type { PoseCue } from "../../avatars/SpritePlayer";
import { Card, EndCard, Karaoke, Line, ReelFrame, SceneBlock, Sticker, Title, type ReelProps } from "../../components";
import { AVATAR_BOX, CAPTION_BOTTOM, SAFE, SAFE_BOX } from "../../layout";
import { timing } from "../../timing";
import mouth from "../../../public/reels/diwali-dev-mode/mouth.json";
import words from "../../../public/reels/diwali-dev-mode/captions.words.json";

export const t = timing(words);
export const AUDIO = "reels/diwali-dev-mode/vo.wav";
export const durationInFrames = t.duration();

// Scene cuts on unique spoken words (aim for 3.5 - 6.5s per scene for ideal pacing):
const S = {
  hook: [0, t.atText("While", 5.78)],
  cleaning: [t.atText("While", 5.78), t.atText("Instead", 12.38)],
  burning1: [t.atText("Instead", 12.38), t.atText("fine-tuning", 16.2)],
  burning2: [t.atText("fine-tuning", 16.2), t.atText("May", 21.06)],
  blessings1: [t.atText("May", 21.06), t.atText("cloud", 26.14)],
  blessings2: [t.atText("cloud", 26.14), t.atText("From", 30.02)],
  wishes: [t.atText("From", 30.02), t.atText("Drop", 35.46)],
  end: [t.atText("Drop", 35.46), t.duration()],
} as const;

const poseCues: PoseCue[] = [
  { at: 0, pose: "thumbs-up" },
  { at: 5.7, pose: "explain" },
  { at: 12.3, pose: "shrug" },
  { at: 16.1, pose: "present" },
  { at: 21.0, pose: "ok" },
  { at: 26.1, pose: "thumbs-up" },
  { at: 30.0, pose: "explain" },
  { at: 35.4, pose: "point-down" },
];

export const Reel: React.FC<ReelProps> = ({ brand = myBrand, avatar = "flat", debugSafeZones, probe }) => {
  const m = useMouth(mouth, words);
  return (
    <ReelFrame brand={brand} audio={AUDIO} debugSafeZones={debugSafeZones} probe={probe}>
      {/* Scene 1: Hook - Light Up Your Terminal */}
      <SceneBlock name="hook" from={S.hook[0]} to={S.hook[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: SAFE.top + 30, width: SAFE_BOX.width }}>
          <Title text="Diwali Dev Mode 🪔" highlight="Dev Mode" at={t.at(0)} size={90} />
        </div>
        <Sticker text="Light Up Terminal 💻" at={t.atText("terminal", 4.48)} rotate={-5} style={{ position: "absolute", left: 440, top: 580 }} />
        <Sticker text="Push In Dark Mode ⚡" at={t.atText("firecrackers", 1.7)} rotate={5} style={{ position: "absolute", left: 430, top: 710 }} />
      </SceneBlock>

      {/* Scene 2: Spring Cleaning (Docker Prune) */}
      <SceneBlock name="cleaning" from={S.cleaning[0]} to={S.cleaning[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 300, width: SAFE_BOX.width }}>
          <Card at={S.cleaning[0]}>
            <Title text="Dev Spring Clean 🧹" highlight="Clean" at={S.cleaning[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={S.cleaning[0]}>🏠 &nbsp;Family: Cleaning rooms</Line>
            <Line at={t.atText("running", 8.06)}>🐳 &nbsp;Devs: docker system prune</Line>
            <Line at={t.atText("300GB", 9.78)}>💾 &nbsp;Reclaimed: 300GB cached layers</Line>
          </Card>
        </div>
        <Sticker text="docker prune 🚀" at={t.atText("prune", 8.94)} rotate={-6} style={{ position: "absolute", left: 450, top: 760 }} />
      </SceneBlock>

      {/* Scene 3: Sky Shots vs GPU Cycles */}
      <SceneBlock name="burning1" from={S.burning1[0]} to={S.burning1[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 300, width: SAFE_BOX.width }}>
          <Card at={S.burning1[0]}>
            <Title text="Sky Shots vs GPUs" highlight="GPUs" at={S.burning1[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={S.burning1[0]}>🎆 &nbsp;Sky shots: $0 burned</Line>
            <Line at={t.atText("burning", 14.96)}>⚡ &nbsp;GPU cycles: Max throughput</Line>
          </Card>
        </div>
        <Sticker text="Burn Cycles Not Cash ⚡" at={t.atText("cash", 13.1)} rotate={4} style={{ position: "absolute", left: 390, top: 750 }} />
      </SceneBlock>

      {/* Scene 4: Local Models at 40 tok/sec */}
      <SceneBlock name="burning2" from={S.burning2[0]} to={S.burning2[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 300, width: SAFE_BOX.width }}>
          <Card at={S.burning2[0]}>
            <Title text="Zero Token Bills 💸" highlight="Zero" at={S.burning2[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={S.burning2[0]}>🧠 &nbsp;Fine-tuning local neural models</Line>
            <Line at={t.atText("40", 18.1)}>⚡ &nbsp;Speed: 40 tokens per second</Line>
            <Line at={t.atText("$0", 19.44)}>💰 &nbsp;Monthly API cost: $0.00</Line>
          </Card>
        </div>
        <Sticker text="40 tok/sec ⚡" at={t.atText("tokens", 18.4)} rotate={-5} style={{ position: "absolute", left: 450, top: 760 }} />
      </SceneBlock>

      {/* Scene 5: Goddess Lakshmi Blessing - 10x ARR */}
      <SceneBlock name="blessings1" from={S.blessings1[0]} to={S.blessings1[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <Card at={S.blessings1[0]}>
            <Title text="Lakshmi Blessings 🪔" highlight="Lakshmi" at={S.blessings1[0]} size={76} />
            <div style={{ height: 24 }} />
            <Line first at={S.blessings1[0]}>📈 &nbsp;Codebase: 10x ARR delivery</Line>
            <Line at={t.atText("500", 24.74)}>🛡️ &nbsp;Cloud logs: Zero 500 errors</Line>
          </Card>
        </div>
        <Sticker text="10x ARR 🚀" at={t.atText("10x", 22.38)} rotate={-6} style={{ position: "absolute", left: 460, top: 760 }} />
      </SceneBlock>

      {/* Scene 6: Paid on Time */}
      <SceneBlock name="blessings2" from={S.blessings2[0]} to={S.blessings2[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 310, width: SAFE_BOX.width }}>
          <Card at={S.blessings2[0]}>
            <Title text="Paid On Time 💳" highlight="Time" at={S.blessings2[0]} size={76} />
            <div style={{ height: 20 }} />
            <Line first at={S.blessings2[0]}>🏦 &nbsp;Clients who pay on time</Line>
            <Line at={t.atText("pay", 27.84)}>✨ &nbsp;Zero invoice chasing</Line>
          </Card>
        </div>
        <Sticker text="Cash Flow Flowing 💵" at={t.atText("clients", 27.28)} rotate={4} style={{ position: "absolute", left: 400, top: 750 }} />
      </SceneBlock>

      {/* Scene 7: Festive Wishes from Signhify Studio */}
      <SceneBlock name="wishes" from={S.wishes[0]} to={S.wishes[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 310, width: SAFE_BOX.width }}>
          <Card at={S.wishes[0]}>
            <Title text="Electric Diwali 🪔" highlight="Electric" at={S.wishes[0]} size={76} />
            <div style={{ height: 20 }} />
            <Line first at={S.wishes[0]}>✨ &nbsp;From Signhify Studio</Line>
            <Line at={t.atText("builder", 33.24)}>🚢 &nbsp;To every builder shipping</Line>
          </Card>
        </div>
        <Sticker text="Happy Diwali! 🪔" at={t.atText("Diwali", 32.38)} rotate={-5} style={{ position: "absolute", left: 440, top: 760 }} />
      </SceneBlock>

      {/* Scene 8: End Card / CTA */}
      <SceneBlock name="end" from={S.end[0]} to={S.end[1]}>
        <div style={{ position: "absolute", left: SAFE_BOX.x, top: 290, width: SAFE_BOX.width }}>
          <EndCard keyword="FESTIVE" lead="Get The Open-Source Stack" sub="Comment FESTIVE to unlock the free repo vault" at={S.end[0]} />
        </div>
      </SceneBlock>

      {/* Mascot Avatar + Captions */}
      {avatar !== "none" ? (
        <div style={{ position: "absolute", left: AVATAR_BOX.x, top: AVATAR_BOX.y }}>
          <Avatar style={avatar} mouth={m} cues={poseCues} size={AVATAR_BOX.size} />
        </div>
      ) : null}
      <div style={{ position: "absolute", left: SAFE_BOX.x, width: SAFE_BOX.width, bottom: CAPTION_BOTTOM }}>
        <Karaoke words={words} perChunk={4} keywords={["Diwali", "terminal", "docker", "prune", "GPU", "Lakshmi", "ARR", "Signhify", "FESTIVE"]} />
      </div>
    </ReelFrame>
  );
};
