# Validation status

Release preparation date: 2026-10-05.

## Verified on the distributed files

- Original artwork SHA-256; all four 640 × 640 RGBA frames; identical alpha throughout
- Exact changed-pixel counts (0 / 713 / 2,918 / 3,631), no changes outside the explicit masks, and exact combined-patch composition
- Patch and native-container rebuilds reproduce the distributed asset bytes
- Native `.veado` chunk boundaries, four state names, all image slot references and lossless raw texture round trips
- Controller command targeting, instance listing and attempted Idle restoration on a simulated failure, using mocks only
- Exact script reconstruction from JSON and subtitles; 14 bash/fish cues and 77 introduction cues with monotone approximate timing
- Full decode of both distributed videos; expected codec, dimensions, frame rates and frame counts (1,835 / 6,225)
- High correlation between encoded speech and its included MP3 source; no decoded clipping; trailing silence
- Offline audio-master regeneration, two-second smoke renders for both example renderers, and a complete nine-second silent preview render
- SHA-256 manifest for the explicit distributed file set
- PNG metadata contains no ancillary chunks; audio/video metadata was reviewed; native container text was reviewed

The software checks run locally with Python 3.12, Pillow 12.3.0, NumPy 2.3.5 and FFmpeg/FFprobe. Reproduction can produce different compressed video bytes on different codec versions. A smoke render tests renderer execution, not every possible input or operating system.

## Native application status

An earlier original-only import was visually verified in veadotube mini. The final four-state avatar has structural and texture tests, but the final native import, live state API, automatic blink/bounce appearance and realtime integration have **not** been verified. Native access was unavailable during final checks; structural validation is not runtime certification.

## Other limits

- This is a PNGtuber, not a Live2D Cubism or 3D rig.
- The finished videos are offline renders, not native application recordings.
- Mouth switching is amplitude-driven, not phoneme-level lip sync.
- Caption timing is estimated from the waveform, not verified word-level alignment.
- Exact voice performance and delivery were not independently audited by ear.
- Independent-account voice recreation has not been tested; the original design model and some design controls were not recorded.
- Microphone, camera, audio routing, public broadcasting and an autonomous AI/TTS pipeline were not configured or tested.

## Rerun

```sh
python3 tools/validate_package.py --media
```

The machine-readable result is written to `build/qa/validation.json`. Generated local output is excluded from the release manifest and should not be committed without a fresh review.
