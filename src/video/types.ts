export type Scene = {
  index: number; start: number; end: number; duration: number;
  narration: string; on_screen_text: string; visual_type: string;
  motion: string; transition: string;
};
export type ReelProps = {
  scenes: Scene[];
  hyperframesVideo: string;
  voiceover: string;
  theme: string;
  hook: string;
  cta: string;
};
