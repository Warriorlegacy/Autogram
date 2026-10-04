import React from 'react';
import {AbsoluteFill, Audio, Video, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import type {ReelProps} from './types';

const ACCENTS: Record<string, string> = {A: '#00E599', B: '#38BDF8', C: '#A78BFA', D: '#22D3EE', E: '#FBBF24'};

/**
 * Remotion composition layer for the Signhify 60s reel.
 *
 * The HyperFrames engine already renders the SINGLE time-synced caption layer
 * (per-scene sub-bar) inside the video itself, so this layer must NOT draw its
 * own full-narration caption boxes — that produced doubled captions. It only
 * adds the premium overlay: slow cinematic push-in, brand watermark, hook line
 * and the end-card CTA. FFmpeg fallback likewise must not burn captions.srt.
 */

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
      <Audio src={voiceover} />
    </AbsoluteFill>
  );
};
