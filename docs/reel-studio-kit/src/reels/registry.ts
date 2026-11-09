// Every reel the studio and the renderer know about. `npm run new -- <id>` adds a line here.
import type React from "react";
import type { ReelProps } from "../components";
import type { Word } from "../timing";
import { PRESETS } from "../presets";
import * as demo from "./demo/Reel";
import * as r_content_factory from "./content-factory/Reel";
import * as r_deleted_production from "./deleted-production/Reel";
import * as r_claude_vs_premiere from "./claude-vs-premiere/Reel";
import * as r_replaced_editor from "./replaced-editor/Reel";
import * as r_local_voice from "./local-voice/Reel";
import * as r_doc_engine from "./doc-engine/Reel";
import * as r_happy_diwali from "./happy-diwali/Reel";
import * as r_diwali_dev_mode from "./diwali-dev-mode/Reel";
// <new-reel-imports>

export type ReelEntry = {
  id: string;
  Component: React.FC<ReelProps>;
  durationInFrames: number;
  /** Extra compositions of the same reel with other props, e.g. another avatar style or brand preset. */
  variants?: { suffix: string; props: ReelProps }[];
};

export const REELS: ReelEntry[] = [
  {
    id: "Demo",
    Component: demo.Reel,
    durationInFrames: demo.durationInFrames,
    variants: [
      { suffix: "Illustrated", props: { avatar: "illustrated" } },
      { suffix: "Pixel", props: { avatar: "pixel" } },
      { suffix: "BoldDark", props: { brand: PRESETS.boldDark } },
      { suffix: "SoftPastel", props: { brand: PRESETS.softPastel } },
    ],
  },
  { id: "content-factory", Component: r_content_factory.Reel, durationInFrames: r_content_factory.durationInFrames },
  { id: "deleted-production", Component: r_deleted_production.Reel, durationInFrames: r_deleted_production.durationInFrames },
  { id: "claude-vs-premiere", Component: r_claude_vs_premiere.Reel, durationInFrames: r_claude_vs_premiere.durationInFrames },
  { id: "replaced-editor", Component: r_replaced_editor.Reel, durationInFrames: r_replaced_editor.durationInFrames },
  { id: "local-voice", Component: r_local_voice.Reel, durationInFrames: r_local_voice.durationInFrames },
  { id: "doc-engine", Component: r_doc_engine.Reel, durationInFrames: r_doc_engine.durationInFrames },
  { id: "happy-diwali", Component: r_happy_diwali.Reel, durationInFrames: r_happy_diwali.durationInFrames },
  { id: "diwali-dev-mode", Component: r_diwali_dev_mode.Reel, durationInFrames: r_diwali_dev_mode.durationInFrames },
  // <new-reel-entries>
];

export type { Word };
