import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, Video, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {ReelProps} from './types';

const ACCENTS: Record<string, string> = {A: '#00E599', B: '#38BDF8', C: '#A78BFA', D: '#22D3EE', E: '#FBBF24'};

const Caption: React.FC<{text: string; start: number; end: number}> = ({text, start, end}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = start * fps;
  const e = end * fps;
  if (frame < s || frame > e) return null;
  const scale = spring({frame: frame - s, fps, config: {damping: 18, stiffness: 220}});
  const opacity = interpolate(frame, [s, s + 6, e - 6, e], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 60, right: 60, bottom: 420, opacity, transform: `scale(${0.94 + 0.06 * scale})`, background: 'rgba(2,6,23,0.88)', border: '2px solid rgba(255,255,255,0.25)', borderRadius: 24, padding: '22px 30px', textAlign: 'center', color: '#fff', fontSize: 40, fontWeight: 800, fontFamily: 'Inter, system-ui, sans-serif', lineHeight: 1.3}}>{text}</div>
  );
};

export const SignhifyReel: React.FC<ReelProps> = ({scenes, hyperframesVideo, voiceover, theme, hook, cta}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const accent = ACCENTS[theme] ?? ACCENTS.A;
  const push = interpolate(frame, [0, 1800], [1.06, 1.0]);
  return (
    <AbsoluteFill style={{background: '#020617', width: 1080, height: 1920}}>
      {/* HyperFrames scene layer: full-bleed, slow push-in for cinematic depth */}
      <div style={{position: 'absolute', inset: 0, transform: `scale(${push})`}}>
        <Video src={hyperframesVideo} style={{width: 1080, height: 1920, objectFit: 'cover'}} />
      </div>
      {/* Brand watermark: subtle, never covers core visuals */}
      <div style={{position: 'absolute', top: 150, left: 60, display: 'flex', alignItems: 'center', gap: 12, background: 'rgba(2,6,23,0.6)', border: `1.5px solid ${accent}`, borderRadius: 999, padding: '10px 26px', color: '#fff', fontSize: 26, fontWeight: 800, letterSpacing: 1}}>● Signhify Studio</div>
      {/* End-card CTA ramp: last 8s */}
      {frame > (60 - 8) * fps && (
        <div style={{position: 'absolute', left: 60, right: 60, bottom: 620, textAlign: 'center', background: accent, borderRadius: 24, padding: '26px', color: '#020617', fontSize: 38, fontWeight: 900}}>{cta}</div>
      )}
      {frame <= (60 - 8) * fps && (
        <div style={{position: 'absolute', left: 60, right: 140, top: 260, color: '#fff', fontSize: 34, fontWeight: 700, textShadow: '0 4px 20px rgba(0,0,0,0.9)'}}>{hook.slice(0, 110)}</div>
      )}
      {scenes.map((s) => (
        <Sequence key={s.index} from={Math.round(s.start * fps)} durationInFrames={Math.max(1, Math.round((s.end - s.start) * fps))}>
          <Caption text={s.on_screen_text} start={0} end={s.end - s.start} />
        </Sequence>
      ))}
      <Audio src={voiceover} />
    </AbsoluteFill>
  );
};
