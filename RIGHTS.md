# Licenses and reuse scope

This package has separate licenses for source code and artwork. **There is no single license covering every file.** The synthetic voice, audio examples and provider services are separate from both open licenses.

## Code: MIT

The project-specific Python source files in `tools/` and `examples/*/tools/`, including their comments and docstrings, are licensed under the [MIT License](LICENSE-CODE). Retain that license and its copyright notice with copies or substantial portions of the software.

The MIT grant does not relicense embedded/referenced artwork, narration text, voice directions, audio, video or third-party software. Referencing an asset from a script does not transfer that asset into the code license.

## Artwork: CC BY 4.0

All PNG artwork under `assets/`, the supplied native avatar project and the silent four-state preview are licensed under [CC BY 4.0](LICENSE-ARTWORK.md). Sharing, modifications and commercial use are permitted under that license, including its attribution and change-notice requirements. See the artwork license file for the exact scope and a ready-to-use attribution example.

The underlying artwork remains CC BY 4.0 where it appears inside a spoken video. The complete spoken video also contains separately governed audio and text; it is not covered as a whole by the artwork license.

## Voice, narration and spoken examples: separate scope

The selected speech is from an original adult fictional voice created with ElevenLabs Voice Design, without real-person imitation or cloning. The two included recordings are published as reference examples under the applicable ElevenLabs output-generation terms. Publication eligibility was reviewed separately; no account or billing details are included.

The MP3 recordings, complete spoken MP4s, narration scripts, captions, timing data and `voice/recipe.json` are **not licensed under MIT or CC BY 4.0**. They are included for listening, inspection and the documented own-account recreation workflow. No additional blanket redistribution, commercial-use or sublicensing grant for these materials is made by this repository; ask the repository owner if you need permission beyond an independently available right.

ElevenLabs' terms, use policy, plan conditions and applicable model restrictions still govern use of its service and outputs. Those provider terms do not automatically grant every downstream recipient rights in this repository's recordings or narration. No proprietary voice/model weights, provider account access or license to the ElevenLabs service are transferred. The saved designed voice is not externally importable simply by using its ID; see [voice/README.md](voice/README.md).

Do not use the example audio as a voice-cloning or model-training dataset. This audio-specific notice imposes no additional restriction on the separately CC-licensed artwork or MIT-licensed code.

- [ElevenLabs output publication guidance](https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform)
- [ElevenLabs Terms of Use](https://elevenlabs.io/terms-of-use)
- [ElevenLabs Prohibited Use Policy](https://elevenlabs.io/use-policy)

## External applications and independent rights

No veadotube app binary, bundled avatar, runtime, model weights or third-party library is distributed here. Install those separately under their own terms. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Nothing here claims ownership of third-party material or takes away rights, exceptions or permissions that exist independently. The licenses only grant rights the licensor is authorized to grant; they do not promise endorsement or clear every possible third-party right.
