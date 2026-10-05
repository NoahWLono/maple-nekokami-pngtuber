# Selected Maple voice

The included examples use **Maple Nekokami - Mommy Voice v1**, an original fictional adult voice created with ElevenLabs Voice Design. No real person's voice was cloned or imitated. Both examples use the selected Generation 1 recording.

## Can I add the same voice to my own account?

Not through this repository. The selected voice is a Voice Design voice. ElevenLabs currently documents sharing designed voices within the same workspace; public Voice Library sharing and outside-account add links are for Professional Voice Clones. A saved voice ID is not a portable voice file or an access grant. See the [official Voice Library documentation](https://elevenlabs.io/docs/eleven-creative/voices/voice-library).

There is no verified public add-to-account link for this selected voice. Making another voice by uploading these recordings as a clone is not the supported recreation route.

## Recreate a similar original voice

[recipe.json](recipe.json) contains the original character direction, preview text, description and settings:

- Design seed: 500301
- Design loudness: 0.5; guidance scale: 5
- Original UI sliders: loudness 75, guidance 37.5
- Speech generation: Eleven v4, stability 0.5, similarity 0.75

In your own ElevenLabs account, use Voice Design and the supplied original prompt. If your current interface exposes the same design controls, use those values, then audition the results and save the one you prefer. Slider display scales and model availability may change; the recorded normalized values and UI positions are deliberately labeled separately.

ElevenLabs documents deterministic generation for the same seed and inputs, but the original Voice Design model identifier, prompt-enhancement setting and quality setting were not recorded. The speech-generation model listed above is separate from the design model. This recipe has not been verified end-to-end on an independent account and does not promise byte-identical audio or permanence across service/model changes. See the [Voice Design API reference](https://elevenlabs.io/docs/api-reference/text-to-voice/design). Review the provider's current terms and the [repository rights notice](../RIGHTS.md) before further use.

No account credentials, API keys or provider login are included or required for offline playback. The repository does not perform online generation. Any account setup and credentials belong in your own provider workflow; never commit them here.

## Example audio

- [Bash/fish selected MP3](../examples/bash-fish/maple-bash-fish-elevenlabs-v4-generation1.mp3)
- [Lore introduction selected MP3](../examples/lore-intro/maple-introduction-elevenlabs-v4-generation1.mp3)

The MP3s preserve the downloaded selected speech. The video masters apply only static gain and silence padding, without pitch shifting, time stretching or a substitute voice. The exact scripts are alongside the recordings. Caption timings are approximate and the recordings were not independently audited by ear.

These recordings are published as listening examples under the applicable provider terms. They, the complete spoken videos, narration and recipe are excluded from the code/artwork licenses; no proprietary voice model or service license is transferred. Provider terms and any additional permission needed from the repository owner remain separate. See [RIGHTS.md](../RIGHTS.md). Do not use these recordings for voice cloning or model training.
