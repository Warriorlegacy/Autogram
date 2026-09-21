import React from 'react';
import {Composition} from 'remotion';
import {SignhifyReel} from './SignhifyReel';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="SignhifyReel"
    component={SignhifyReel}
    durationInFrames={1800}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{scenes: [], hyperframesVideo: '', voiceover: '', theme: 'A', hook: '', cta: 'Follow Signhify.studio for more.'}}
  />
);
