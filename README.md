# Maple Nekokami PNGtuber

A four-state PNGtuber package for **Maple / Koyou**, an AI-powered fictional adult character with a synthetic voice. It includes aligned transparent artwork, an optional native veadotube mini avatar, an offline renderer, and the selected ElevenLabs voice examples and recreation settings.

This is PNG frame switching, **not a Live2D Cubism rig or a 3D model**. The recorded examples were rendered offline. Final four-state live playback and live API control have not been verified.

## Watch the selected voice

- [Come get comfortable: Maple's fictional introduction](examples/lore-intro/maple-lore-introduction-elevenlabs-voice1.mp4) — 4:19.375, 960 × 720, 24 fps, approximately 7.6 MB.
- [Bash versus fish](examples/bash-fish/maple-bash-vs-fish-elevenlabs-voice1.mp4) — 1:01.167, 960 × 720, 30 fps, approximately 2.3 MB.
- [Silent four-state preview](examples/four-state-preview.mp4) — 9 seconds.

Each spoken example includes its original selected MP3, exact script, approximate subtitle cues and source renderer. Both use the selected **Maple Nekokami - Mommy Voice v1**, created with ElevenLabs Voice Design. No real person's voice was cloned or imitated. See [voice settings and account portability](voice/README.md).

## Use the four images

The files in [assets/aligned](assets/aligned) are all 640 × 640 RGBA PNGs:

| Frame | Eyes | Mouth |
| --- | --- | --- |
| `maple-idle.png` | Open | Closed |
| `maple-speaking.png` | Open | Open |
| `maple-blink.png` | Closed | Closed |
| `maple-speaking-blink.png` | Closed | Open |

Load these into a PNGtuber application that supports the corresponding four slots. No provider account or voice service is needed to use image switching. The artwork is available under [CC BY 4.0](LICENSE-ARTWORK.md), including commercial reuse and modifications with attribution. See [RIGHTS.md](RIGHTS.md) for the exact scopes.

### Optional veadotube mini setup

1. Download the app from its [official page](https://olmewe.itch.io/veadotube-mini), and review its [installation instructions](https://veado.tube/docs/install/) and [terms](https://veado.tube/docs/terms/).
2. Open `project/maple-pngtuber.veado` through the app's avatar controls. Preserve existing work before loading a different avatar.
3. Check all four named states and the blink slots locally before using it live. The Speaking states have a small native bounce effect.

An original-only native import was verified during preparation. The final four-state container has passed structural and pixel round-trip tests, but its final live import, effects and state changes still need verification. No app executable is bundled. veadotube mini is free of charge but is **not FOSS**; its own terms apply.

[Native controller instructions and limits](docs/NATIVE.md)

## Inspect and reproduce

The Python tools require Python 3, NumPy and Pillow; rendering and full media checks also require FFmpeg/FFprobe with H.264/AAC support and DejaVu Sans fonts. Dependencies are not bundled. The tested Python library versions are in `requirements.txt`. Install dependencies using your usual trusted environment/package manager.

From this repository's root:

```sh
python3 tools/validate_package.py
python3 tools/create_expression_patches.py
python3 tools/build_avatar.py
python3 tools/render_offline_preview.py
python3 tools/validate_package.py
```

The first command verifies the distributed package before rebuilding it. Patch assembly reproduces only the explicitly masked face edits. It never modifies the original. [Artwork and masks](docs/ARTWORK.md) explain the method.

To reproduce an example without contacting ElevenLabs:

```sh
python3 tools/prepare_example_audio.py bash-fish
python3 examples/bash-fish/tools/render_clip.py
python3 tools/prepare_example_audio.py lore-intro
python3 examples/lore-intro/tools/render_intro.py
```

Generated audio, video, logs and preview images go into `build/` directories and leave the distributed examples untouched. Add `--limit-seconds 2` to either example renderer for a short smoke render. For nonstandard font locations, set `MAPLE_FONT_DIR` to a directory containing the DejaVu Sans font family. Compressed bytes can vary with FFmpeg versions.

`python3 tools/validate_package.py --media` additionally decodes the complete distributed media, checks formats/captions and compares the encoded speech with its included MP3 source. `MANIFEST.json` records the explicit distributed file set, sizes and SHA-256 hashes.

## What the animation does

- Switches between two mouth shapes using audio amplitude, plus short deterministic blinks
- Keeps expression pixels aligned and preserves the original alpha channel
- Provides optional commands for the four native avatar states

It does not provide phoneme-level lip sync, continuous gaze, facial deformation, motion tracking or a fully integrated autonomous livestream. No microphone, camera, system audio routing or provider connection is configured by this package.

The subtitles are waveform-grounded estimates, not verified word-level alignment. The selected voice performances and exact spoken delivery were not independently audited by ear. The lore introduction contains mild profanity. See [validation status](docs/VALIDATION.md) for tested and untested stages.

## Voice recreation and rights

The original saved Voice Design voice cannot be imported into an unrelated ElevenLabs account just by using a voice ID. The included recipe lets another account try a similar original voice; it does not guarantee the identical voice. No exact public add-to-account voice link is available in this package.

Python source code is [MIT-licensed](LICENSE-CODE). The PNG artwork, native avatar project and silent preview are [CC BY 4.0](LICENSE-ARTWORK.md). The selected synthetic recordings, complete spoken videos, narration and voice recipe are separate from both licenses; no proprietary provider voice/model is relicensed. See [RIGHTS.md](RIGHTS.md) and [third-party notices](THIRD_PARTY_NOTICES.md) for the exact scope. Do not use the audio samples to clone a voice or train a model.
