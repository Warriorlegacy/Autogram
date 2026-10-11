# QA — D:\Autogram\video_studio\output\zip-deploy-fullstack\reel.mp4

- Verdict: **PASS**
- HyperFrames gate clean: True
- Spec: 1080x1920 @30.0fps, 37.5s, h264/aac, 2277209 bytes

## Checks

- PASS — container_valid: h264
- PASS — dimensions: 1080x1920 (need vertical >= 540x960)
- PASS — aspect_9_16: ratio 0.5625
- PASS — fps_supported: 30.0 fps
- PASS — duration_in_range: 37.5s
- PASS — duration_matches_plan: got 37.5s, planned 37.5s
- PASS — video_codec_h264: h264
- PASS — audio_present: audio codec aac
- PASS — nonzero_size: 2277209 bytes
- PASS — frames_extractable: 7 frames extracted

## Frames extracted

- `D:\Autogram\video_studio\output\zip-deploy-fullstack\qa_frames\frame_00_t5.36s.jpg`
- `D:\Autogram\video_studio\output\zip-deploy-fullstack\qa_frames\frame_01_t10.71s.jpg`
- `D:\Autogram\video_studio\output\zip-deploy-fullstack\qa_frames\frame_02_t16.07s.jpg`
- `D:\Autogram\video_studio\output\zip-deploy-fullstack\qa_frames\frame_03_t21.43s.jpg`
- `D:\Autogram\video_studio\output\zip-deploy-fullstack\qa_frames\frame_04_t26.79s.jpg`
- `D:\Autogram\video_studio\output\zip-deploy-fullstack\qa_frames\frame_05_t32.14s.jpg`
- `D:\Autogram\video_studio\output\zip-deploy-fullstack\qa_frames\frame_06_t37.42s.jpg`

## Remaining defects

- none

Visual inspection of the extracted frames is still required; a passing automated gate is not a production verdict.